"""Generate a self-contained HTML gallery for the built songs.

For each ``data/<song>.ly`` this collects the engraved score preview, the
verification MP3, and the PDF, extracts a per-note timeline from the song's MIDI
(via :mod:`music21`), and writes a *song-specific folder* under
``data/gallery/<song>/`` containing the assets plus an ``index.html`` with a
Synthesia-style falling-notes piano visualization synced to the audio. A landing
``data/gallery/index.html`` links them together.

Public entry point: :func:`build_gallery`.
"""
from __future__ import annotations

import html
import json
import re
import shutil
import tempfile
import webbrowser
from dataclasses import dataclass, field
from pathlib import Path

from . import engine

GALLERY_DIRNAME = "gallery"

# --- header parsing -------------------------------------------------------

_FIELD_RE = {
    "title": re.compile(r'title\s*=\s*"([^"]*)"'),
    "composer": re.compile(r'composer\s*=\s*"([^"]*)"'),
    "poet": re.compile(r'poet\s*=\s*"([^"]*)"'),
}


def parse_header(ly: Path) -> dict[str, str]:
    """Pull ``title`` / ``composer`` / ``poet`` from a song's ``\\header`` block.

    Falls back to a title derived from the file stem.
    """
    text = ly.read_text(encoding="utf-8", errors="replace")
    out: dict[str, str] = {}
    for name, rx in _FIELD_RE.items():
        m = rx.search(text)
        if m:
            out[name] = m.group(1)
    out.setdefault("title", ly.stem.replace("_", " ").title())
    out.setdefault("composer", "")
    out.setdefault("poet", "")
    return out


# --- note timeline --------------------------------------------------------


def extract_notes(ly: Path) -> list[list[float]]:
    """Return ``[[midi, start_sec, dur_sec], ...]`` for the song, onset-sorted.

    Re-engraves the ``.ly`` to MIDI (kept in a temp dir) and reads it with
    music21, converting quarter-note offsets to seconds via the score tempo.
    Returns ``[]`` if the song has no ``\\midi`` block or extraction fails.
    """
    try:
        from music21 import converter, tempo
    except Exception:  # pragma: no cover - music21 is a hard dep, but be safe
        return []
    try:
        with tempfile.TemporaryDirectory() as td:
            midi = engine.render_midi(ly, out_stem=Path(td) / ly.stem)
            flat = converter.parse(str(midi)).flatten()
            marks = flat.getElementsByClass(tempo.MetronomeMark)
            bpm = float(marks[0].number) if marks else 120.0
            spq = 60.0 / bpm  # seconds per quarter note
            events: list[list[float]] = []
            for n in flat.notes:
                start = round(float(n.offset) * spq, 4)
                dur = round(float(n.quarterLength) * spq, 4)
                for p in n.pitches:
                    events.append([int(p.midi), start, dur])
            events.sort(key=lambda e: (e[1], e[0]))
            return events
    except engine.BuildError:
        return []
    except Exception:  # pragma: no cover - never let viz failure break the build
        return []


# --- measure boxes (for the score overlay) --------------------------------

import xml.etree.ElementTree as ET  # noqa: E402

_SVG_NS = "{http://www.w3.org/2000/svg}"
_TEMPO_RE = re.compile(r"\\tempo\s+(\d+)\s*=\s*(\d+)")

# A top-level \layout that tags every barline with its class + musical moment
# (whole notes). Prepended before \include-ing the song so it needs no edits.
_TAG_LAYOUT = r"""\version "2.24.0"
\layout {
  \context { \Score
    \override BarLine.output-attributes =
      #(lambda (grob)
         (let* ((col (ly:item-get-column grob))
                (mom (ly:grob-property col 'when)))
           (list (cons 'class "mbar")
                 (cons 'data-t (if (ly:moment? mom)
                                   (exact->inexact (ly:moment-main mom)) 0)))))
  }
}
"""


def _seconds_per_whole(ly_text: str) -> float:
    """Whole-note duration in seconds from the song's ``\\tempo D = M``."""
    m = _TEMPO_RE.search(ly_text)
    if not m:
        return 4 * 60 / 120  # default: quarter = 120
    unit, bpm = int(m.group(1)), int(m.group(2))
    return unit * 60 / bpm


def _apply_transform(spec: str | None, sx, sy, tx, ty):
    if not spec:
        return sx, sy, tx, ty
    for kind, body in re.findall(r"(translate|scale)\(([^)]*)\)", spec):
        nums = [float(v) for v in re.split(r"[ ,]+", body.strip()) if v]
        if kind == "translate":
            dx, dy = nums[0], (nums[1] if len(nums) > 1 else 0.0)
            tx, ty = tx + sx * dx, ty + sy * dy
        else:  # scale
            a, b = nums[0], (nums[1] if len(nums) > 1 else nums[0])
            sx, sy = sx * a, sy * b
    return sx, sy, tx, ty


def _walk_svg(el, sx, sy, tx, ty, bars, lines):
    sx, sy, tx, ty = _apply_transform(el.get("transform"), sx, sy, tx, ty)
    if el.get("class") == "mbar":
        # the barline's position lives in this group's child <g transform=...>
        child = next(iter(el), None)
        _, _, bx, by = _apply_transform(
            child.get("transform") if child is not None else None, sx, sy, tx, ty
        )
        bars.append((bx, by, float(el.get("data-t", "0"))))
    if el.tag == _SVG_NS + "line":
        x1 = float(el.get("x1", 0)); x2 = float(el.get("x2", 0))
        y1 = float(el.get("y1", 0)); y2 = float(el.get("y2", 0))
        if abs(y1 - y2) < 0.01 and (x2 - x1) > 15:  # a full staff line
            lines.append((tx + sx * x1, tx + sx * x2, ty + sy * y1))
    for ch in el:
        _walk_svg(ch, sx, sy, tx, ty, bars, lines)


def _systems_from_lines(lines: list[tuple[float, float, float]]):
    """Cluster staff lines into systems (one staff = one system).

    Returns ``[{left, right, y0, y1}, ...]`` top-to-bottom. Lead sheets are
    single-staff, so each 5-line staff is its own system — this stays correct
    for multi-system pieces whether or not later systems are indented.
    """
    if not lines:
        return []
    staves = []
    for left, right, y in sorted(lines, key=lambda l: l[2]):
        if staves and y - staves[-1]["y1"] < 2.0:  # same 5-line staff
            s = staves[-1]
            s["y1"] = y; s["left"] = min(s["left"], left); s["right"] = max(s["right"], right)
        else:
            staves.append({"left": left, "right": right, "y0": y, "y1": y})
    staves.sort(key=lambda s: s["y0"])
    return staves


def extract_measures(ly: Path) -> list[dict]:
    """Return measure highlight boxes for the score image.

    Each box is ``{t0, t1, x, y, w, h}`` where the times are in **seconds** and
    the geometry is a **fraction of the page** (0..1), so it overlays the page-1
    preview PNG directly. Returns ``[]`` if extraction fails.
    """
    try:
        ly_text = ly.read_text(encoding="utf-8", errors="replace")
        # Repeats make the written measure time diverge from the unfolded audio
        # (which plays the repeats out), so the overlay can't be synced. Skip.
        if "\\repeat" in ly_text:
            return []
        spw = _seconds_per_whole(ly_text)
        with tempfile.TemporaryDirectory() as td:
            wrap = Path(td) / "wrap.ly"
            wrap.write_text(_TAG_LAYOUT + f'\\include "{ly.resolve()}"\n', encoding="utf-8")
            stem = Path(td) / "out"
            engine.require_tool("lilypond")
            engine._run(
                ["lilypond", "-dbackend=svg", "-dpoint-and-click=#f",
                 *engine._include_args(ly), "-o", str(stem), str(wrap)],
                what=f"lilypond svg ({ly.name})",
            )
            # single-page -> out.svg; multi-page -> out-1.svg, out-2.svg, ...
            # The preview PNG is page 1, so only page 1's measures are overlaid.
            svg = stem.with_suffix(".svg")
            if not svg.exists():
                svg = stem.parent / (stem.name + "-1.svg")
            if not svg.exists():
                return []
            root = ET.parse(svg).getroot()
            vb = [float(v) for v in re.split(r"[ ,]+", root.get("viewBox", "").strip()) if v]
            if len(vb) != 4:
                return []
            page_w, page_h = vb[2], vb[3]
            bars: list = []
            lines: list = []
            _walk_svg(root, 1.0, 1.0, 0.0, 0.0, bars, lines)
            systems = _systems_from_lines(lines)
            if not systems or not bars:
                return []

            # assign barlines to the nearest system whose x-span contains them
            for sys in systems:
                sys["bars"] = []
            for bx, by, t in bars:
                cand = [s for s in systems if s["left"] - 2 <= bx <= s["right"] + 2]
                if not cand:
                    cand = systems
                sys = min(cand, key=lambda s: abs((s["y0"] + s["y1"]) / 2 - by))
                sys["bars"].append((bx, t))

            boxes: list[dict] = []
            prev_t = 0.0
            # asymmetric padding (viewBox units): extra headroom up top so high
            # ledger-line notes are covered, a little below the staff too.
            pad_top, pad_bot = 3.2, 1.4
            for sys in systems:
                sbars = sorted(sys["bars"])
                box_left = sys["left"]
                for bx, t in sbars:
                    if bx <= box_left:  # skip a barline at the very start
                        box_left = max(box_left, bx)
                        prev_t = t
                        continue
                    boxes.append({
                        "t0": round(prev_t * spw, 3),
                        "t1": round(t * spw, 3),
                        "x": round(box_left / page_w, 5),
                        "y": round((sys["y0"] - pad_top) / page_h, 5),
                        "w": round((bx - box_left) / page_w, 5),
                        "h": round((sys["y1"] - sys["y0"] + pad_top + pad_bot) / page_h, 5),
                    })
                    box_left = bx
                    prev_t = t
            return boxes
    except engine.BuildError:
        return []
    except Exception:  # never let the overlay break the gallery
        return []


# --- model ----------------------------------------------------------------


@dataclass
class SongCard:
    """One song's source, artifacts, metadata, and note timeline."""

    stem: str
    title: str
    composer: str
    poet: str
    pdf: Path | None
    mp3: Path | None
    png: Path | None
    notes: list[list[float]] = field(default_factory=list)
    measures: list[dict] = field(default_factory=list)

    @property
    def duration(self) -> float:
        return max((s + d for _, s, d in self.notes), default=0.0)


def collect_songs(root: Path) -> list[SongCard]:
    """Build a :class:`SongCard` per ``.ly`` in ``root`` (artifacts if present)."""
    cards: list[SongCard] = []
    for ly in engine.discover_songs(root):
        hdr = parse_header(ly)

        def _opt(suffix: str) -> Path | None:
            p = ly.with_name(ly.stem + suffix)
            return p if p.exists() else None

        cards.append(
            SongCard(
                stem=ly.stem,
                title=hdr["title"],
                composer=hdr["composer"],
                poet=hdr["poet"],
                pdf=_opt(".pdf"),
                mp3=_opt(".mp3"),
                png=_opt("_preview-1.png"),
                notes=extract_notes(ly),
                measures=extract_measures(ly),
            )
        )
    return cards


# --- rendering ------------------------------------------------------------

_ASSETS = Path(__file__).parent / "gallery_assets"


def _esc(s: str) -> str:
    return html.escape(s, quote=True)


def _song_page(card: SongCard) -> str:
    payload = {
        "title": card.title,
        "composer": card.composer,
        "notes": card.notes,
        "measures": card.measures,
        "audio": f"{card.stem}.mp3" if card.mp3 else None,
        "duration": round(card.duration, 3),
    }
    data = json.dumps(payload, separators=(",", ":"))
    has_audio = card.mp3 is not None
    has_score = card.png is not None
    score_block = (
        f'<div class="score-stage"><img class="score" '
        f'src="{_esc(card.stem)}_preview-1.png" '
        f'alt="Score preview for {_esc(card.title)}">'
        f'<div id="hl" class="hl"></div></div>'
        if has_score
        else '<p class="muted">No score preview — run <code>build --png</code>.</p>'
    )
    audio_block = (
        f'<audio id="audio" controls preload="metadata" '
        f'src="{_esc(card.stem)}.mp3"></audio>'
        if has_audio
        else '<p class="muted">No audio — run <code>build</code> with a soundfont.</p>'
    )
    pdf_link = (
        f'<a class="btn" href="{_esc(card.stem)}.pdf">Open PDF score ↗</a>'
        if card.pdf
        else ""
    )
    sub = _esc(card.composer) + (
        f" · {_esc(card.poet)}" if card.poet else ""
    )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{_esc(card.title)} — leadsheet gallery</title>
<link rel="stylesheet" href="../assets/style.css">
</head>
<body class="song">
<header class="topbar">
  <a class="back" href="../index.html">← all songs</a>
</header>
<main>
  <section class="hero">
    <h1>{_esc(card.title)}</h1>
    <p class="sub">{sub}</p>
  </section>

  <section class="piano-wrap">
    <canvas id="piano" aria-label="Falling-notes piano visualization"></canvas>
    <div class="controls">
      <button id="play" class="btn play" type="button">▶ Play</button>
      <span id="clock" class="clock">0:00</span>
    </div>
    <div id="now" class="now"><span class="now-label">Now playing</span><span class="now-empty">—</span></div>
  </section>

  <section class="player">{audio_block}</section>

  <section class="score-wrap">{score_block}</section>

  <nav class="actions">{pdf_link}</nav>
</main>
<script>window.SONG = {data};</script>
<script src="../assets/app.js"></script>
</body>
</html>
"""


def _landing_page(cards: list[SongCard], title: str) -> str:
    items = []
    for c in cards:
        thumb = (
            f'<img src="{_esc(c.stem)}/{_esc(c.stem)}_preview-1.png" '
            f'alt="" loading="lazy">'
            if c.png
            else '<div class="noimg">♪</div>'
        )
        badge = (
            f'<span class="badge">{len(c.notes)} notes</span>' if c.notes else ""
        )
        meta = _esc(c.composer) if c.composer else "&nbsp;"
        items.append(
            f'<a class="card" href="{_esc(c.stem)}/index.html">'
            f'<div class="thumb">{thumb}{badge}</div>'
            f'<div class="cap"><strong>{_esc(c.title)}</strong>'
            f'<span>{meta}</span></div></a>'
        )
    cards_html = "\n".join(items) or '<p class="muted">No songs found.</p>'
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{_esc(title)}</title>
<link rel="stylesheet" href="assets/style.css">
</head>
<body class="gallery">
<header class="masthead">
  <h1>{_esc(title)}</h1>
  <p>Engraved scores, verification audio, and a falling-notes piano for every song.</p>
</header>
<main class="grid">
{cards_html}
</main>
</body>
</html>
"""


def build_gallery(
    root: Path,
    *,
    out_dir: Path | None = None,
    title: str = "Leadsheet Gallery",
    open_browser: bool = False,
) -> Path:
    """Generate the gallery under ``out_dir`` (default ``root/gallery``).

    Returns the path to the landing ``index.html``.
    """
    out = out_dir or (root / GALLERY_DIRNAME)
    out.mkdir(parents=True, exist_ok=True)

    # Shared, dependency-free assets.
    assets = out / "assets"
    assets.mkdir(exist_ok=True)
    for name in ("style.css", "app.js"):
        shutil.copyfile(_ASSETS / name, assets / name)

    cards = collect_songs(root)
    for card in cards:
        folder = out / card.stem
        folder.mkdir(exist_ok=True)
        for src in (card.pdf, card.mp3, card.png):
            if src is not None:
                dst = folder / src.name
                # Self-contained layout: the source already lives in this folder,
                # so the build wrote the artifacts here — nothing to copy.
                if src.resolve() != dst.resolve():
                    shutil.copyfile(src, dst)
        (folder / "notes.json").write_text(
            json.dumps(card.notes, separators=(",", ":")), encoding="utf-8"
        )
        (folder / "index.html").write_text(_song_page(card), encoding="utf-8")

    landing = out / "index.html"
    landing.write_text(_landing_page(cards, title), encoding="utf-8")

    if open_browser:
        webbrowser.open(landing.resolve().as_uri())
    return landing
