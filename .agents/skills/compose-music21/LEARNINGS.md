# Learnings — compose-music21

Running log of non-obvious lessons from composing with music21. Append a dated
bullet when you hit a gotcha, a fix, or a discovery worth not re-learning.
Newest first.

## 2026-06-21 — music21 offsets are quarterLengths, not seconds
`note.offset` / element offsets are in quarter notes, not real time. To get
seconds (e.g. for MIDI onset scoring with `mir_eval`), write the score to MIDI
and read it back with `pretty_midi` (`note.start` / `note.end` are seconds) —
don't try to convert quarterLengths to seconds by hand. See
`verify.notes_from_midi`.

## 2026-06-21 — music21 is a declared dep but may be missing from the venv
`compose.py` imports music21 lazily, so the engine and other skills work without
it. But `tests/test_compose.py` (and any compose call) fails with
`ModuleNotFoundError: No module named 'music21'` if the shared venv lacks it.
Fix: `uv sync` (or `uv pip install music21`). The lazy import is intentional —
keep it.

## 2026-06-21 — `to_midi` is robust; `render_pdf` is generic
`Song.to_midi` is pure music21 (no external tools) and reliable. `render_pdf`
shells to LilyPond via music21 and produces generic engraving — no chord-symbol
row or letter-notes. For polished lead sheets, hand-write a `.ly` (see the
**add-song** skill) instead of rendering from music21.

## 2026-06-21 — to get an MP3 from a composed song, hand off to the engine
music21 makes MIDI; audio is the engine's job. Pass the MIDI to
`engine.midi_to_mp3(midi, mp3, soundfont)` (or `midi_to_wav` for WAV). `leadsheet
demo` is the worked define → MIDI + MP3 + PDF example.

## 2026-06-21 — cover new pure logic with a test first
New pure helpers on `Song` get a unit test in `tests/test_compose.py` (TDD). The
subprocess/LilyPond paths are verified by running, not unit-tested.
