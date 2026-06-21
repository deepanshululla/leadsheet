"""Unit tests for the HTML gallery generator (pure parts; no LilyPond)."""

import json
from pathlib import Path

from leadsheet import gallery
from leadsheet.gallery import SongCard


def _write_ly(path, *, header=True):
    head = (
        '\\header { title = "My Tune" composer = "A. Person" '
        'poet = "Key of C" tagline = ##f }\n'
        if header
        else "\\header { tagline = ##f }\n"
    )
    path.write_text(head + "melody = { c'4 d' e' }\n", encoding="utf-8")
    return path


def test_parse_header_reads_fields(tmp_path):
    ly = _write_ly(tmp_path / "song.ly")
    hdr = gallery.parse_header(ly)
    assert hdr["title"] == "My Tune"
    assert hdr["composer"] == "A. Person"
    assert hdr["poet"] == "Key of C"


def test_parse_header_falls_back_to_stem(tmp_path):
    ly = _write_ly(tmp_path / "we_wish.ly", header=False)
    assert gallery.parse_header(ly)["title"] == "We Wish"


def test_song_page_inlines_notes_and_links_assets():
    card = SongCard(
        stem="my_tune", title="My Tune", composer="A. Person", poet="Key of C",
        pdf=None, mp3=None, png=None, notes=[[60, 0.0, 0.5], [64, 0.5, 0.5]],
    )
    page = gallery._song_page(card)
    assert "window.SONG" in page
    assert '[[60,0.0,0.5],[64,0.5,0.5]]' in page
    assert '../assets/app.js' in page
    assert "My Tune" in page


def test_build_gallery_creates_song_folders(tmp_path, monkeypatch):
    # Avoid invoking LilyPond: stub the extraction steps.
    monkeypatch.setattr(gallery, "extract_notes", lambda _ly: [[60, 0.0, 1.0]])
    monkeypatch.setattr(gallery, "extract_measures", lambda _ly: [])

    root = tmp_path / "data"
    root.mkdir()
    _write_ly(root / "my_tune.ly")
    (root / "my_tune.pdf").write_bytes(b"%PDF-1.4 fake")
    (root / "my_tune.mp3").write_bytes(b"ID3 fake")
    (root / "my_tune_preview-1.png").write_bytes(b"\x89PNG fake")

    landing = gallery.build_gallery(root)

    assert landing == root / "gallery" / "index.html"
    assert landing.exists()
    # shared assets copied
    assert (root / "gallery" / "assets" / "app.js").exists()
    assert (root / "gallery" / "assets" / "style.css").exists()
    # per-song folder with copied artifacts + data
    song = root / "gallery" / "my_tune"
    assert (song / "index.html").exists()
    assert (song / "my_tune.pdf").exists()
    assert (song / "my_tune.mp3").exists()
    assert (song / "my_tune_preview-1.png").exists()
    assert json.loads((song / "notes.json").read_text()) == [[60, 0.0, 1.0]]
    # landing links to the song page
    assert "my_tune/index.html" in landing.read_text()


def test_build_gallery_self_contained_song_folder(tmp_path, monkeypatch):
    # New layout: the source .ly already lives in gallery/<song>/ with its built
    # artifacts. build_gallery must write notes.json + index.html in place and
    # NOT choke trying to copy the artifacts onto themselves.
    monkeypatch.setattr(gallery, "extract_notes", lambda _ly: [[60, 0.0, 1.0]])
    monkeypatch.setattr(gallery, "extract_measures", lambda _ly: [])

    root = tmp_path / "data"
    folder = root / "gallery" / "my_tune"
    folder.mkdir(parents=True)
    _write_ly(folder / "my_tune.ly")
    (folder / "my_tune.pdf").write_bytes(b"%PDF-1.4 fake")
    (folder / "my_tune.mp3").write_bytes(b"ID3 fake")
    (folder / "my_tune_preview-1.png").write_bytes(b"\x89PNG fake")

    landing = gallery.build_gallery(root)

    # artifacts stay in the song's own folder (no SameFileError, no move)
    assert (folder / "my_tune.pdf").exists()
    assert (folder / "my_tune.mp3").exists()
    assert (folder / "index.html").exists()
    assert json.loads((folder / "notes.json").read_text()) == [[60, 0.0, 1.0]]
    assert "my_tune/index.html" in landing.read_text()


def test_seconds_per_whole_from_tempo():
    assert gallery._seconds_per_whole("x \\tempo 4 = 100 y") == 2.4   # quarter=100
    assert gallery._seconds_per_whole("\\tempo 2 = 60") == 2.0         # half=60
    assert gallery._seconds_per_whole("no tempo here") == 2.0          # default 120


def test_apply_transform_composes_translate_and_scale():
    # translate then scale: point (1,1) -> 10 + 2*1 = 12
    sx, sy, tx, ty = gallery._apply_transform("translate(10, 20) scale(2)", 1, 1, 0, 0)
    assert (sx, sy, tx, ty) == (2, 2, 10, 20)


def test_systems_from_lines_groups_two_staves():
    # two staff clusters (y~0 and y~10), each 5 lines, same x-span -> 2 systems
    lines = []
    for y in (0, 1, 2, 3, 4, 10, 11, 12, 13, 14):
        lines.append((5.0, 95.0, float(y)))
    systems = gallery._systems_from_lines(lines)
    assert len(systems) == 2
    assert systems[0]["y0"] < systems[1]["y0"]


def test_song_page_inlines_measures_and_overlay():
    card = SongCard(
        stem="t", title="T", composer="", poet="", pdf=None, mp3=None,
        png=Path("t_preview-1.png"),
        measures=[{"t0": 0.0, "t1": 1.0, "x": 0.1, "y": 0.2, "w": 0.3, "h": 0.4}],
    )
    page = gallery._song_page(card)
    assert 'id="hl"' in page and "score-stage" in page
    assert '"measures"' in page and '"t1":1.0' in page


def test_collect_songs_handles_missing_artifacts(tmp_path, monkeypatch):
    monkeypatch.setattr(gallery, "extract_notes", lambda _ly: [])
    monkeypatch.setattr(gallery, "extract_measures", lambda _ly: [])
    root = tmp_path / "data"
    root.mkdir()
    _write_ly(root / "bare.ly")  # no pdf/mp3/png alongside
    (cards,) = gallery.collect_songs(root)
    assert cards.pdf is None and cards.mp3 is None and cards.png is None
    assert cards.title == "My Tune"
