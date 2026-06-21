---
name: compose-music21
description: "Compose, transpose, and export songs in Python with music21. Use when asked to define a melody in Python (not LilyPond), transpose a song to another key, change keys, generate or manipulate notes programmatically, or export MIDI from Python. Backs the `leadsheet demo` command."
---

# Compose with music21

`src/leadsheet/compose.py` wraps [music21](https://web.mit.edu/music21/) so a song
can be defined and manipulated in Python rather than written as LilyPond text.
music21 sits on the same backends (LilyPond for engraving, a synth for audio) — it
does not replace them.

## API

```python
from leadsheet.compose import Song

song = Song.from_notation(
    "3/4 g8. g16 a4 g4 c'4 b2.",          # music21 tinyNotation (incl. time sig)
    lyrics=["Hap", "py", "Birth", "day", "to", "you"],
    title="Happy Birthday (line 1)", key="C",
)

song.note_names                  # ['G4', 'G4', 'A4', 'G4', 'C5', 'B4']
song.to_midi("out.mid")          # pure music21 — no external tools
song.transposed("M2").to_midi("up.mid")   # interval strings: M2, -P5, m3, …
song.render_pdf("out")           # via music21 -> LilyPond
```

## Notes

- `to_midi` is native music21 (robust, no LilyPond). To get an MP3 from it, pass
  the MIDI to `engine.midi_to_mp3`.
- `render_pdf` shells to LilyPond through music21; its engraving style is generic
  (no chord-symbol row / letter-notes). For polished lead sheets, prefer a
  hand-written `.ly` (see the **add-song** skill).
- `leadsheet demo` is a worked example: define → MIDI + MP3 + PDF.
- Cover new pure logic with a unit test in `tests/test_compose.py` (TDD).

## Learnings

Read `LEARNINGS.md` in this folder before starting (accumulated gotchas), and
append a dated bullet whenever you hit a new one.
