"""Define songs in Python with music21, then export MIDI / render a PDF.

music21 is a Python API on top of the same backends the engine uses (LilyPond
for engraving, a synth for audio) — it lets a song be built and manipulated
(transpose, analyze) in Python rather than written as LilyPond text.

    from leadsheet.compose import Song
    song = Song.from_notation("3/4 c4 d e", lyrics=["do", "re", "mi"], title="Scale")
    song.to_midi("scale.mid")          # native music21, no external tools
    song.transposed("M2").to_midi("scale_up.mid")
    song.render_pdf("scale")           # via music21 -> LilyPond
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Sequence


def _music21():
    """Import lazily so the engine works even if music21 isn't installed."""
    import music21  # noqa: PLC0415

    return music21


class Song:
    """A melody (optionally with lyrics) backed by a music21 score."""

    def __init__(self, score, *, title: str = "", composer: str = "") -> None:
        self.score = score
        self.title = title
        self.composer = composer

    @classmethod
    def from_notation(
        cls,
        notation: str,
        *,
        lyrics: Sequence[str] = (),
        title: str = "",
        composer: str = "Unknown",
        key: str | None = None,
    ) -> "Song":
        """Build a Song from music21 tinyNotation, e.g. ``"3/4 g8. g16 a4 g c'4 b2."``."""
        m21 = _music21()
        score = m21.converter.parse(f"tinyNotation: {notation}")

        for note, syllable in zip(score.recurse().notes, lyrics):
            note.addLyric(syllable)

        if key is not None:
            score.measure(1).insert(0, m21.key.Key(key))

        md = m21.metadata.Metadata()
        md.title = title
        md.composer = composer
        score.insert(0, md)
        return cls(score, title=title, composer=composer)

    @property
    def note_names(self) -> list[str]:
        """Pitch names in order, e.g. ``['G4', 'G4', 'A4', ...]``."""
        return [n.nameWithOctave for n in self.score.recurse().notes]

    def transposed(self, interval: str) -> "Song":
        """Return a new Song transposed by an interval like ``"M2"`` or ``"-P5"``."""
        return Song(
            self.score.transpose(interval), title=self.title, composer=self.composer
        )

    def to_midi(self, path: str | Path) -> Path:
        """Write a MIDI file (pure music21, no external tools)."""
        path = Path(path)
        self.score.write("midi", fp=str(path))
        return path

    def render_pdf(self, path: str | Path) -> Path:
        """Render a PDF via music21's LilyPond backend. Returns the PDF path."""
        m21 = _music21()
        lily = shutil.which("lilypond")
        if lily:
            m21.environment.set("lilypondPath", lily)
        path = Path(path)
        out = self.score.write("lilypond.pdf", fp=str(path.with_suffix("")))
        return Path(out)


def demo_song() -> Song:
    """A recognizable example: the first line of 'Happy Birthday' in C major."""
    return Song.from_notation(
        "3/4 g8. g16 a4 g4 c'4 b2.",
        lyrics=["Hap", "py", "Birth", "day", "to", "you"],
        title="music21 demo — Happy Birthday (line 1)",
        composer="leadsheet.compose",
        key="C",
    )
