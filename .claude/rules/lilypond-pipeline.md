# Rule: LilyPond + audio pipeline

Conventions and gotchas for engraving and audio in this project. Loaded by the
**render-leadsheet** and **add-song** skills.

## Engraving

- Songs are self-contained per folder: `data/gallery/<song>/<song>.ly` (a legacy
  flat `data/<song>.ly` still works). Each `\include "lead-sheet.ily"` for the
  shared `uppercase-note-name` helper (letter-notes printed as `C`, `F#`, `Bb`).
- `lead-sheet.ily` lives once at `data/` (the songs root), **not** copied into
  each song folder. `engine._include_args(ly)` builds the `-I` flags: the song's
  own folder plus the nearest ancestor holding `lead-sheet.ily`. These must be
  **absolute** paths — LilyPond `chdir`s to the input file's folder, so a relative
  `-I` would resolve against the wrong directory and the include would not be
  found. Write the include as `"lead-sheet.ily"` (no path); route all lilypond
  calls through `_include_args` rather than hand-rolling `-I`.
- Target LilyPond 2.24+ syntax. Update old sources with `convert-ly -e file.ly`.

## Audio

- A score needs a `\midi { \tempo 4 = N }` block to produce MIDI (and thus audio).
  Add `\unfoldRepeats` to the midi score so repeated sections actually play.
- **fluidsynth argument order matters**: `fluidsynth -ni -F out.wav -r 44100
  <soundfont> <midi>` — the soundfont and MIDI must be the final two arguments,
  or fluidsynth exits 0 having written nothing. The engine's `midi_to_wav`
  encodes this; route audio through it rather than calling fluidsynth ad hoc.
- Soundfont: auto-discovered (prefers ASCII-named GM banks); override with
  `MUSIC_SF2` or `--soundfont`. Default is FluidSynth's bundled VintageDreams
  bank — a synth-pad timbre that is fine for ear-checking, not for performance.

## Intermediates

`build_one` deletes the `.midi` after producing the MP3. `render_midi` is the
variant that *keeps* the MIDI (ground truth) and does not clean up — use it when
the MIDI itself is the artifact, not just an audio intermediate.
