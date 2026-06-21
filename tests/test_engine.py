"""Unit tests for the pure (non-subprocess) parts of the engine."""

import pytest

from leadsheet import engine


def test_rank_prefers_ascii_gm_bank():
    cands = [
        "/x/Wéird-bank.sf2",          # non-ascii -> demoted
        "/x/RandomWaves.sf2",
        "/x/FluidR3_GM.sf2",          # GM bank -> first
        "/x/VintageDreams.sf2",       # vintage -> second
    ]
    ranked = engine.rank_soundfonts(cands)
    assert ranked[0] == "/x/FluidR3_GM.sf2"
    assert ranked[1] == "/x/VintageDreams.sf2"
    assert "/x/Wéird-bank.sf2" not in ranked  # dropped when ascii names exist


def test_rank_keeps_nonascii_if_only_option():
    cands = ["/x/Wéird-bank.sf2"]
    assert engine.rank_soundfonts(cands) == cands


def test_discover_songs_finds_only_ly(tmp_path):
    (tmp_path / "a.ly").write_text("")
    (tmp_path / "b.ly").write_text("")
    (tmp_path / "helper.ily").write_text("")
    (tmp_path / "notes.txt").write_text("")
    found = [p.name for p in engine.discover_songs(tmp_path)]
    assert found == ["a.ly", "b.ly"]


def test_discover_songs_finds_flat_and_nested(tmp_path):
    # flat layout + self-contained per-song folders under gallery/
    (tmp_path / "flat.ly").write_text("")
    nested = tmp_path / "gallery" / "tune"
    nested.mkdir(parents=True)
    (nested / "tune.ly").write_text("")
    (tmp_path / "gallery" / "assets").mkdir()  # no .ly -> ignored
    found = sorted(p.stem for p in engine.discover_songs(tmp_path))
    assert found == ["flat", "tune"]


def test_resolve_song_adds_extension_and_dir(tmp_path):
    (tmp_path / "song.ly").write_text("")
    assert engine.resolve_song("song", tmp_path).name == "song.ly"
    assert engine.resolve_song("song.ly", tmp_path).name == "song.ly"


def test_resolve_song_prefers_nested_folder(tmp_path):
    song = tmp_path / "gallery" / "tune" / "tune.ly"
    song.parent.mkdir(parents=True)
    song.write_text("")
    assert engine.resolve_song("tune", tmp_path) == song


def test_include_args_are_absolute_and_find_shared_include(tmp_path):
    (tmp_path / "lead-sheet.ily").write_text("")
    song = tmp_path / "gallery" / "tune" / "tune.ly"
    song.parent.mkdir(parents=True)
    song.write_text("")
    args = engine._include_args(song)
    dirs = [args[i] for i in range(1, len(args), 2)]  # values after each -I
    assert all(engine.Path(d).is_absolute() for d in dirs)
    assert str(song.parent.resolve()) in dirs       # the song's own folder
    assert str(tmp_path.resolve()) in dirs           # where lead-sheet.ily lives


def test_resolve_song_missing_raises(tmp_path):
    with pytest.raises(engine.BuildError):
        engine.resolve_song("nope", tmp_path)


def test_find_soundfont_env_missing_raises(monkeypatch):
    monkeypatch.setenv("MUSIC_SF2", "/definitely/not/here.sf2")
    with pytest.raises(engine.BuildError):
        engine.find_soundfont()
