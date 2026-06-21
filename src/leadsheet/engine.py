"""Render engine: a LilyPond ``.ly`` -> PDF + MP3 (+ optional PNG) pipeline.

Runs ``lilypond`` -> MIDI -> ``fluidsynth`` (WAV) -> ``lame`` (MP3), auto-finds a
soundfont, handles the FluidSynth arg-order gotcha, and cleans up intermediates.
The pure helpers here (soundfont discovery, song resolution) are unit-tested;
the subprocess steps are verified by running the CLI.
"""

from __future__ import annotations

import glob
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# Where to look for a soundfont, in priority order. MUSIC_SF2 env wins if set.
SOUNDFONT_GLOBS = [
    "/opt/homebrew/Cellar/fluid-synth/*/share/fluid-synth/sf2/*.sf2",
    "/opt/homebrew/share/sounds/sf2/*.sf2",
    "/usr/share/sounds/sf2/*.sf2",
    str(Path.home() / ".local/share/soundfonts/*.sf2"),
]

_BREW_PKG = {"lilypond": "lilypond", "fluidsynth": "fluid-synth", "lame": "lame"}


class BuildError(RuntimeError):
    """A pipeline step failed; the message is user-facing."""


def require_tool(name: str) -> str:
    path = shutil.which(name)
    if not path:
        raise BuildError(
            f"'{name}' not found on PATH. Install it with:  "
            f"brew install {_BREW_PKG.get(name, name)}"
        )
    return path


def rank_soundfonts(candidates: list[str]) -> list[str]:
    """Order soundfonts best-first: ASCII names, GM banks, then the rest."""
    ascii_only = [c for c in candidates if c.isascii()]
    pool = ascii_only or candidates

    def key(path: str) -> tuple[int, str]:
        low = Path(path).name.lower()
        rank = 2 if "gm" in low else 1 if "vintage" in low else 0
        return (-rank, path)

    return sorted(pool, key=key)


def find_soundfont() -> str | None:
    """Locate a ``.sf2`` soundfont, preferring an ASCII-named General-MIDI bank."""
    env = os.environ.get("MUSIC_SF2")
    if env:
        if Path(env).is_file():
            return env
        raise BuildError(f"MUSIC_SF2 points at a missing file: {env}")

    candidates: list[str] = []
    for pattern in SOUNDFONT_GLOBS:
        candidates.extend(glob.glob(pattern))
    ranked = rank_soundfonts(candidates)
    return ranked[0] if ranked else None


def _run(cmd: list[str], *, what: str) -> None:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        tail = (proc.stderr or proc.stdout or "").strip().splitlines()[-8:]
        raise BuildError(f"{what} failed:\n  " + "\n  ".join(tail))


def midi_to_wav(midi: Path, wav: Path, soundfont: str, *, what: str = "audio") -> Path:
    """Synthesize ``midi`` to a WAV file via fluidsynth."""
    fluidsynth = require_tool("fluidsynth")
    # soundfont + MIDI MUST come last or fluidsynth writes nothing.
    _run(
        [fluidsynth, "-ni", "-F", str(wav), "-r", "44100", soundfont, str(midi)],
        what=f"fluidsynth ({what})",
    )
    return Path(wav)


def midi_to_mp3(midi: Path, mp3: Path, soundfont: str, *, what: str = "audio") -> Path:
    """Synthesize ``midi`` to ``mp3`` via fluidsynth (WAV) then lame."""
    lame = require_tool("lame")
    with tempfile.TemporaryDirectory() as tmp:
        wav = Path(tmp) / "render.wav"
        midi_to_wav(midi, wav, soundfont, what=what)
        _run([lame, "--quiet", "-V5", str(wav), str(mp3)], what=f"lame ({what})")
    return mp3


# Songs are self-contained: each lives in its own folder ``<root>/gallery/<song>/``
# holding ``<song>.ly`` plus every built artifact. A flat ``<root>/<song>.ly`` is
# still honored for backward compatibility.
GALLERY_DIRNAME = "gallery"
SHARED_INCLUDE = "lead-sheet.ily"


def _include_args(ly: Path) -> list[str]:
    """LilyPond ``-I`` flags for engraving ``ly``.

    Always the song's own folder, plus the nearest ancestor that holds the shared
    ``lead-sheet.ily`` include — so a nested ``gallery/<song>/<song>.ly`` still
    resolves ``\\include "lead-sheet.ily"`` even though the helper lives up in the
    songs root (not duplicated into every song folder).
    """
    dirs: list[Path] = [ly.parent]
    for anc in ly.parents:
        if (anc / SHARED_INCLUDE).exists() and anc not in dirs:
            dirs.append(anc)
            break
    # Absolute paths: LilyPond chdir's to the input file's folder before
    # processing, so a relative -I would resolve against the wrong directory.
    args: list[str] = []
    for d in dirs:
        args += ["-I", str(d.resolve())]
    return args


def discover_songs(root: Path) -> list[Path]:
    """All song sources under ``root`` (``.ily`` includes excluded).

    Finds both the flat ``root/*.ly`` layout and the per-song-folder layout
    ``root/gallery/<song>/<song>.ly``.
    """
    found = set(root.glob("*.ly"))
    found.update(root.glob(f"{GALLERY_DIRNAME}/*/*.ly"))
    return sorted(found, key=lambda p: (p.stem, str(p)))


def resolve_song(arg: str, root: Path) -> Path:
    """Turn a user argument into a ``.ly`` path (extension and folder optional)."""
    p = Path(arg)
    if p.suffix != ".ly":
        p = p.with_suffix(".ly")
    if p.exists():
        return p
    if not p.is_absolute():
        # Prefer the self-contained per-song folder, then the flat layout.
        candidates = [root / GALLERY_DIRNAME / p.stem / p.name, root / p.name]
        for c in candidates:
            if c.exists():
                return c
        p = candidates[0]
    raise BuildError(f"no such song: {arg} (looked for {p})")


def render_midi(ly: Path, *, out_stem: Path | None = None) -> Path:
    """Engrave ``ly`` with LilyPond and return the MIDI it produced.

    Unlike :func:`build_one`, the MIDI is kept (not cleaned up) — the corpus
    builder uses it as transcription ground truth. ``out_stem`` redirects output
    (default: alongside ``ly``); a PDF is written there too as a harmless
    byproduct of engraving.
    """
    lilypond = require_tool("lilypond")
    stem = Path(out_stem) if out_stem is not None else ly.with_suffix("")
    _run(
        [lilypond, "--pdf", *_include_args(ly), "-o", str(stem), str(ly)],
        what=f"lilypond ({ly.name})",
    )
    midi = next(
        (m for m in (stem.with_suffix(".midi"), stem.with_suffix(".mid")) if m.exists()),
        None,
    )
    if midi is None:
        raise BuildError(f"{ly.name} produced no MIDI — does it have a \\midi block?")
    return midi


def build_one(
    ly: Path,
    *,
    soundfont: str | None,
    audio: bool = True,
    png: bool = False,
    open_pdf: bool = False,
) -> dict[str, Path]:
    """Build a single song; return the artifacts produced."""
    lilypond = require_tool("lilypond")
    outputs: dict[str, Path] = {}

    # 1. LilyPond -> PDF (+ .midi if the score has a \midi block).
    #    -I lets \include "lead-sheet.ily" resolve from the song's nested folder.
    _run(
        [lilypond, "--pdf", *_include_args(ly),
         "-o", str(ly.with_suffix("")), str(ly)],
        what=f"lilypond ({ly.name})",
    )
    pdf = ly.with_suffix(".pdf")
    if not pdf.exists():
        raise BuildError(f"lilypond produced no PDF for {ly.name}")
    outputs["pdf"] = pdf

    midi = next(
        (m for m in (ly.with_suffix(".midi"), ly.with_suffix(".mid")) if m.exists()),
        None,
    )

    # 2. MIDI -> WAV -> MP3 (verification audio).
    if audio:
        if midi is None:
            print(f"  note: {ly.name} has no \\midi block — skipping audio")
        elif soundfont is None:
            print("  note: no soundfont found — skipping audio "
                  "(set MUSIC_SF2 or pass --soundfont)")
        else:
            outputs["mp3"] = midi_to_mp3(
                midi, ly.with_suffix(".mp3"), soundfont, what=ly.name
            )

    # 3. Optional page-1 preview PNG.
    if png:
        pdftoppm = shutil.which("pdftoppm")
        if not pdftoppm:
            print("  note: pdftoppm not found — skipping PNG preview")
        else:
            stem = str(ly.with_suffix("")) + "_preview"
            _run(
                [pdftoppm, "-png", "-r", "120", "-f", "1", "-l", "1",
                 str(pdf), stem],
                what=f"pdftoppm ({ly.name})",
            )
            preview = Path(stem + "-1.png")
            if preview.exists():
                outputs["png"] = preview

    # 4. Tidy intermediates.
    if midi is not None:
        midi.unlink(missing_ok=True)

    if open_pdf and sys.platform == "darwin":
        subprocess.run(["open", str(pdf)], check=False)

    return outputs
