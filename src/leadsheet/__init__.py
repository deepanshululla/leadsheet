"""leadsheet — render LilyPond lead sheets to PDF + audio, compose with music21."""

from .engine import BuildError, build_one, discover_songs, find_soundfont

__all__ = ["BuildError", "build_one", "discover_songs", "find_soundfont"]
__version__ = "0.1.0"
