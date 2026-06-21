"""AMT verification loop.

Transcribe each corpus WAV back to notes and score against the ground-truth
MIDI with ``mir_eval``, sweeping cheap post-filter parameters over a single
(expensive) transcription per piece.

Transcribers are pluggable:

* :class:`OracleTranscriber` — degrades the ground truth (drop / jitter /
  spurious notes). Needs no ML deps, so the loop and scoring are runnable and
  unit-testable out of the box, and the wiring is provable before installing a
  real engine.
* :class:`PianoTranscriber` — real audio->notation via
  ``piano_transcription_inference`` (optional ``[transcribe]`` extra).

    from leadsheet import corpus, verify
    items = corpus.load_corpus("data/corpus")
    verify.verify_corpus(items, verify.OracleTranscriber(), est_dir="data/corpus/est")
"""

from __future__ import annotations

import abc
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import numpy as np

from .corpus import CorpusItem

# A note set: (intervals[N, 2] in seconds, pitches[N] as MIDI numbers).
Notes = tuple[np.ndarray, np.ndarray]


# --------------------------------------------------------------------------- #
# MIDI <-> note arrays
# --------------------------------------------------------------------------- #
def notes_from_midi(path: str | Path) -> Notes:
    """Read a MIDI file into ``(intervals_seconds, midi_pitches)``, onset-sorted."""
    import warnings  # noqa: PLC0415

    import pretty_midi  # noqa: PLC0415

    with warnings.catch_warnings():
        # LilyPond puts tempo/key on a non-zero track; pretty_midi reads it
        # correctly but warns. Harmless for our purposes.
        warnings.filterwarnings("ignore", category=RuntimeWarning, module="pretty_midi")
        pm = pretty_midi.PrettyMIDI(str(path))
    notes = [n for inst in pm.instruments if not inst.is_drum for n in inst.notes]
    notes.sort(key=lambda n: (n.start, n.pitch))
    if not notes:
        return np.empty((0, 2), float), np.empty((0,), int)
    intervals = np.array([[n.start, n.end] for n in notes], float)
    pitches = np.array([n.pitch for n in notes], int)
    return intervals, pitches


def write_midi(
    path: str | Path,
    intervals: np.ndarray,
    pitches: np.ndarray,
    *,
    velocity: int = 80,
    program: int = 0,
) -> Path:
    """Write ``(intervals_seconds, midi_pitches)`` to a single-instrument MIDI."""
    import pretty_midi  # noqa: PLC0415

    pm = pretty_midi.PrettyMIDI()
    inst = pretty_midi.Instrument(program=program)
    for (start, end), pitch in zip(intervals, pitches):
        inst.notes.append(
            pretty_midi.Note(
                velocity=velocity, pitch=int(pitch), start=float(start), end=float(end)
            )
        )
    pm.instruments.append(inst)
    pm.write(str(path))
    return Path(path)


def _midi_to_hz(pitches: np.ndarray) -> np.ndarray:
    return 440.0 * 2.0 ** ((np.asarray(pitches, float) - 69.0) / 12.0)


# --------------------------------------------------------------------------- #
# Scoring
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class Score:
    precision: float
    recall: float
    f1: float


def score(
    ref: Notes,
    est: Notes,
    *,
    onset_tolerance: float = 0.05,
    pitch_tolerance: float = 50.0,
) -> Score:
    """Onset+pitch precision/recall/F1 via ``mir_eval`` (offsets ignored).

    ``onset_tolerance`` is in seconds; ``pitch_tolerance`` in cents (50 = within
    a quarter-tone, i.e. exact semitone match).
    """
    import mir_eval  # noqa: PLC0415

    ref_iv, ref_p = ref
    est_iv, est_p = est
    if len(ref_p) == 0 or len(est_p) == 0:
        return Score(0.0, 0.0, 0.0)
    precision, recall, f1, _ = mir_eval.transcription.precision_recall_f1_overlap(
        ref_iv,
        _midi_to_hz(ref_p),
        est_iv,
        _midi_to_hz(est_p),
        onset_tolerance=onset_tolerance,
        pitch_tolerance=pitch_tolerance,
        offset_ratio=None,
    )
    return Score(float(precision), float(recall), float(f1))


def apply_post_filter(notes: Notes, *, min_duration: float = 0.0) -> Notes:
    """Drop est notes shorter than ``min_duration`` seconds (kills spurious blips)."""
    intervals, pitches = notes
    if min_duration <= 0.0 or len(pitches) == 0:
        return intervals, pitches
    keep = (intervals[:, 1] - intervals[:, 0]) >= min_duration
    return intervals[keep], pitches[keep]


# --------------------------------------------------------------------------- #
# Transcribers
# --------------------------------------------------------------------------- #
class Transcriber(abc.ABC):
    """Maps a WAV to an estimated MIDI. Subclasses set ``name``."""

    name = "transcriber"

    @abc.abstractmethod
    def transcribe(self, wav: str | Path, out_midi: str | Path) -> Path: ...


@dataclass
class OracleTranscriber(Transcriber):
    """Simulated engine: degrade the ground truth to exercise the loop deps-free.

    Reads the ground-truth MIDI sibling of ``wav`` (``<wav>.mid``) and applies
    ``drop`` (fraction of notes removed), ``jitter`` (onset stddev, seconds), and
    ``spurious`` (fraction of extra short blips added).
    """

    name = "oracle"
    drop: float = 0.1
    jitter: float = 0.02
    spurious: float = 0.1
    seed: int = 0

    def transcribe(self, wav: str | Path, out_midi: str | Path) -> Path:
        intervals, pitches = notes_from_midi(Path(wav).with_suffix(".mid"))
        rng = np.random.default_rng(self.seed)
        n = len(pitches)

        keep = rng.random(n) >= self.drop
        intervals, pitches = intervals[keep], pitches[keep]

        if len(pitches):
            shift = rng.normal(0.0, self.jitter, size=len(pitches))
            intervals = np.clip(intervals + shift[:, None], 0.0, None)

        n_spur = int(round(self.spurious * n))
        if n_spur and len(pitches):
            idx = rng.integers(0, len(pitches), size=n_spur)
            starts = intervals[idx, 0]
            durs = rng.uniform(0.01, 0.04, size=n_spur)
            intervals = np.vstack([intervals, np.column_stack([starts, starts + durs])])
            pitches = np.concatenate([pitches, pitches[idx] + rng.integers(-2, 3, n_spur)])

        order = np.argsort(intervals[:, 0]) if len(pitches) else slice(None)
        return write_midi(out_midi, intervals[order], pitches[order])


class PianoTranscriber(Transcriber):
    """Real piano AMT via ``piano_transcription_inference`` (optional extra).

    First use downloads the model checkpoint (~170 MB) to the package cache.
    """

    name = "piano_transcription"

    def __init__(self, *, device: str = "cpu", checkpoint_path: str | None = None) -> None:
        self.device = device
        self.checkpoint_path = checkpoint_path
        self._model = None

    def transcribe(self, wav: str | Path, out_midi: str | Path) -> Path:
        from piano_transcription_inference import (  # noqa: PLC0415
            PianoTranscription,
            load_audio,
            sample_rate,
        )

        if self._model is None:
            self._model = PianoTranscription(
                device=self.device, checkpoint_path=self.checkpoint_path
            )
        audio, _ = load_audio(str(wav), sr=sample_rate, mono=True)
        self._model.transcribe(audio, str(out_midi))
        return Path(out_midi)


# --------------------------------------------------------------------------- #
# The loop
# --------------------------------------------------------------------------- #
DEFAULT_POST_GRID: list[dict] = [{"min_duration": d} for d in (0.0, 0.05, 0.1)]


@dataclass
class PieceResult:
    name: str
    score: Score
    params: dict
    n_ref: int
    n_est: int


@dataclass
class Report:
    results: list[PieceResult]

    @property
    def mean_f1(self) -> float:
        return (
            float(np.mean([r.score.f1 for r in self.results])) if self.results else 0.0
        )


def verify_one(
    item: CorpusItem,
    transcriber: Transcriber,
    *,
    est_dir: str | Path,
    post_grid: list[dict] = DEFAULT_POST_GRID,
    onset_tolerance: float = 0.05,
) -> PieceResult:
    """Transcribe one piece once, then pick the best-scoring post-filter."""
    est_dir = Path(est_dir)
    est_dir.mkdir(parents=True, exist_ok=True)
    est_midi = est_dir / f"{item.name}.{transcriber.name}.mid"
    transcriber.transcribe(item.wav, est_midi)

    ref = notes_from_midi(item.midi)
    est_raw = notes_from_midi(est_midi)

    best: tuple[Score, dict, int] | None = None
    for params in post_grid:
        est = apply_post_filter(est_raw, **params)
        s = score(ref, est, onset_tolerance=onset_tolerance)
        if best is None or s.f1 > best[0].f1:
            best = (s, params, len(est[1]))

    assert best is not None  # post_grid is non-empty
    s, params, n_est = best
    return PieceResult(item.name, s, params, n_ref=len(ref[1]), n_est=n_est)


def verify_corpus(
    items: list[CorpusItem],
    transcriber: Transcriber,
    *,
    est_dir: str | Path,
    post_grid: list[dict] = DEFAULT_POST_GRID,
    onset_tolerance: float = 0.05,
    log: Callable[[str], None] = print,
) -> Report:
    """Run :func:`verify_one` over the corpus and report per-piece + mean F1."""
    results = []
    for item in items:
        r = verify_one(
            item,
            transcriber,
            est_dir=est_dir,
            post_grid=post_grid,
            onset_tolerance=onset_tolerance,
        )
        results.append(r)
        log(
            f"  {r.name:32s} F1={r.score.f1:.3f}  P={r.score.precision:.3f}  "
            f"R={r.score.recall:.3f}  (ref {r.n_ref}/est {r.n_est}, {r.params})"
        )
    report = Report(results)
    log(f"  {'mean F1':32s} {report.mean_f1:.3f}")
    return report
