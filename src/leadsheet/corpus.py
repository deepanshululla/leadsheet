"""Build a reference corpus: ground-truth MIDI + synthesized WAV pairs.

The source MIDI comes from the project's own ``.ly`` songs (engraved by
LilyPond), then each is synthesized to WAV with the same fluidsynth pipeline the
engine uses. The WAV is the transcription input; the MIDI is the ground truth.
Alignment is exact *by construction*, so the verification F1 is honest with no
downloads — see :mod:`leadsheet.verify`.

    from leadsheet import corpus, engine
    items = corpus.build_corpus(engine.discover_songs(Path("data")), "data/corpus")
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable

from . import engine


@dataclass(frozen=True)
class CorpusItem:
    """A reference piece: ground-truth ``midi`` paired with its synth ``wav``."""

    name: str
    midi: Path
    wav: Path


def build_corpus(
    songs: Iterable[Path],
    corpus_dir: str | Path,
    *,
    soundfont: str | None = None,
    log: Callable[[str], None] = print,
) -> list[CorpusItem]:
    """Engrave each ``.ly`` to MIDI and synthesize a WAV beside it.

    Returns the corpus items written under ``corpus_dir`` as ``<name>.mid`` +
    ``<name>.wav``.
    """
    corpus_dir = Path(corpus_dir)
    corpus_dir.mkdir(parents=True, exist_ok=True)

    soundfont = soundfont or engine.find_soundfont()
    if soundfont is None:
        raise engine.BuildError(
            "no soundfont found — set MUSIC_SF2 or pass --soundfont"
        )

    items: list[CorpusItem] = []
    for ly in songs:
        stem = corpus_dir / ly.stem
        produced = engine.render_midi(ly, out_stem=stem)
        midi = corpus_dir / f"{ly.stem}.mid"
        if produced.resolve() != midi.resolve():
            produced.replace(midi)
        stem.with_suffix(".pdf").unlink(missing_ok=True)  # engraving byproduct

        wav = corpus_dir / f"{ly.stem}.wav"
        engine.midi_to_wav(midi, wav, soundfont, what=ly.stem)

        items.append(CorpusItem(ly.stem, midi, wav))
        log(f"  {ly.stem}: {midi.name} + {wav.name}")
    return items


def load_corpus(corpus_dir: str | Path) -> list[CorpusItem]:
    """Load previously built ``<name>.mid`` / ``<name>.wav`` pairs.

    Only top-level ``.mid`` files are considered, so transcription outputs kept
    under ``corpus_dir/est/`` are excluded.
    """
    corpus_dir = Path(corpus_dir)
    items: list[CorpusItem] = []
    for midi in sorted(corpus_dir.glob("*.mid")):
        wav = midi.with_suffix(".wav")
        if wav.exists():
            items.append(CorpusItem(midi.stem, midi, wav))
    return items