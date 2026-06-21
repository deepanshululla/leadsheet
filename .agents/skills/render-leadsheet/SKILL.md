---
name: render-leadsheet
description: "Render LilyPond lead sheets to PDF and verification audio (MP3). Use when asked to build, render, compile, regenerate, or export the sheet music / PDFs / audio for songs in this project, or to produce a preview image. Wraps the lilypond -> MIDI -> fluidsynth -> lame pipeline."
---

# Render lead sheets to PDF + audio

The engine (`src/leadsheet/engine.py`, exposed as the `leadsheet` CLI) runs
`lilypond` → MIDI → `fluidsynth` (WAV) → `lame` (MP3), auto-discovers a soundfont,
and cleans up intermediates.

## Commands

```bash
task build                    # render every song in data/
task song -- happy_birthday   # one song
task pdf                      # PDFs only, skip audio
uv run leadsheet build <song> --png      # also write a page-1 preview PNG
uv run leadsheet build --soundfont X.sf2 # override the soundfont
```

## How it works

- LilyPond is invoked with `-I data/` so each song's `\include "lead-sheet.ily"`
  resolves. A PDF is always produced; MIDI only if the score has a `\midi` block.
- Audio: `fluidsynth -ni -F out.wav -r 44100 <soundfont> <midi>` — the **soundfont
  and MIDI must be the last two arguments** or fluidsynth writes an empty file —
  then `lame` to MP3.
- Soundfont discovery prefers an ASCII-named General-MIDI bank; override via the
  `MUSIC_SF2` environment variable or `--soundfont`.

## Verifying

After building, confirm the PDF renders (open it or `--png`) and the MP3 plays the
intended tune. Don't report success without one of these checks.

## Learnings

Read `LEARNINGS.md` in this folder before starting (accumulated gotchas), and
append a dated bullet whenever you hit a new one.
