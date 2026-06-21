"""Verification harness: scoring, MIDI round-trip, and the oracle loop.

No network, fluidsynth, LilyPond, or ML deps — everything runs on note arrays
and small MIDI files written via pretty_midi.
"""

from __future__ import annotations

import numpy as np
import pytest

from leadsheet import verify
from leadsheet.corpus import CorpusItem


def _notes(triples):
    """(start, end, midi_pitch) tuples -> a Notes pair."""
    intervals = np.array([[s, e] for s, e, _ in triples], float)
    pitches = np.array([p for *_, p in triples], int)
    return intervals, pitches


def test_score_perfect_match():
    ref = _notes([(0.0, 0.5, 60), (0.5, 1.0, 62), (1.0, 1.5, 64)])
    s = verify.score(ref, ref)
    assert s.precision == pytest.approx(1.0)
    assert s.recall == pytest.approx(1.0)
    assert s.f1 == pytest.approx(1.0)


def test_score_dropped_note_lowers_recall():
    ref = _notes([(0.0, 0.5, 60), (0.5, 1.0, 62), (1.0, 1.5, 64), (1.5, 2.0, 65)])
    est = _notes([(0.0, 0.5, 60), (0.5, 1.0, 62)])
    s = verify.score(ref, est)
    assert s.recall == pytest.approx(0.5)
    assert s.precision == pytest.approx(1.0)


def test_score_onset_shift_beyond_tolerance():
    ref = _notes([(0.0, 0.5, 60)])
    est = _notes([(0.3, 0.8, 60)])  # 300 ms > 50 ms tolerance
    assert verify.score(ref, est, onset_tolerance=0.05).f1 == pytest.approx(0.0)


def test_score_wrong_pitch_misses():
    ref = _notes([(0.0, 0.5, 60)])
    est = _notes([(0.0, 0.5, 67)])  # a fifth off
    assert verify.score(ref, est).f1 == pytest.approx(0.0)


def test_score_empty_estimate_is_zero():
    ref = _notes([(0.0, 0.5, 60)])
    est = (np.empty((0, 2), float), np.empty((0,), int))
    assert verify.score(ref, est).f1 == pytest.approx(0.0)


def test_post_filter_removes_short_notes():
    intervals = np.array([[0.0, 0.5], [0.5, 0.52]], float)
    pitches = np.array([60, 61])
    _, kept = verify.apply_post_filter((intervals, pitches), min_duration=0.1)
    assert list(kept) == [60]


def test_midi_round_trip(tmp_path):
    intervals = np.array([[0.0, 0.5], [0.5, 1.0]], float)
    pitches = np.array([60, 62])
    path = tmp_path / "x.mid"
    verify.write_midi(path, intervals, pitches)
    riv, rp = verify.notes_from_midi(path)
    assert list(rp) == [60, 62]
    assert riv == pytest.approx(intervals, abs=1e-2)


def _oracle_item(tmp_path):
    intervals = np.array([[i * 0.5, i * 0.5 + 0.4] for i in range(20)], float)
    pitches = np.arange(60, 80)
    ref_midi = tmp_path / "song.mid"
    verify.write_midi(ref_midi, intervals, pitches)
    wav = tmp_path / "song.wav"  # oracle reads the .mid sibling; content unused
    wav.write_bytes(b"")
    return CorpusItem("song", ref_midi, wav)


def test_oracle_clean_pass_is_perfect(tmp_path):
    item = _oracle_item(tmp_path)
    clean = verify.OracleTranscriber(drop=0.0, jitter=0.0, spurious=0.0, seed=1)
    r = verify.verify_one(item, clean, est_dir=tmp_path / "est")
    assert r.score.f1 == pytest.approx(1.0)


def test_oracle_more_drop_lowers_recall(tmp_path):
    item = _oracle_item(tmp_path)
    est_dir = tmp_path / "est"
    low = verify.OracleTranscriber(drop=0.1, jitter=0.0, spurious=0.0, seed=1)
    high = verify.OracleTranscriber(drop=0.8, jitter=0.0, spurious=0.0, seed=1)
    r_low = verify.verify_one(item, low, est_dir=est_dir)
    r_high = verify.verify_one(item, high, est_dir=est_dir)
    assert r_low.score.recall > r_high.score.recall


def test_verify_corpus_reports_mean(tmp_path):
    item = _oracle_item(tmp_path)
    clean = verify.OracleTranscriber(drop=0.0, jitter=0.0, spurious=0.0, seed=1)
    report = verify.verify_corpus(
        [item, item], clean, est_dir=tmp_path / "est", log=lambda *_: None
    )
    assert report.mean_f1 == pytest.approx(1.0)
    assert len(report.results) == 2
