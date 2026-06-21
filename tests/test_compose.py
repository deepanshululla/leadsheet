"""Unit tests for the music21-based composition layer."""

from leadsheet.compose import Song, demo_song


def test_demo_song_note_names():
    # First line of Happy Birthday in C: G G A G C B.
    assert demo_song().note_names == ["G4", "G4", "A4", "G4", "C5", "B4"]


def test_from_notation_applies_lyrics():
    song = Song.from_notation("4/4 c4 d e f", lyrics=["do", "re", "mi", "fa"])
    lyrics = [n.lyric for n in song.score.recurse().notes]
    assert lyrics == ["do", "re", "mi", "fa"]


def test_transposed_up_major_second():
    up = demo_song().transposed("M2")
    # G G A G C B  ->  A A B A D C#
    assert up.note_names == ["A4", "A4", "B4", "A4", "D5", "C#5"]


def test_to_midi_writes_file(tmp_path):
    out = demo_song().to_midi(tmp_path / "demo.mid")
    assert out.exists() and out.stat().st_size > 0
