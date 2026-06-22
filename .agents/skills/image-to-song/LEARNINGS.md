# image-to-song — learnings

Running log of image-reading gotchas. Append a dated bullet when you hit a new one.

- **2026-06-21** — Skill created. The `data/` song sources and the shared
  `data/lead-sheet.ily` include had been removed (only built `gallery/`+`corpus/`
  outputs remained), so a fresh `\include "lead-sheet.ily"` would have failed.
  Recreated `lead-sheet.ily` (the `(pitch context) -> markup` `uppercase-note-name`
  helper) and verified the full chain end-to-end: a one-line melody `.ly` builds to
  PDF + MP3 + preview PNG and the gallery emits per-song `index.html` + `notes.json`.
  If `\include "lead-sheet.ily"` errors in future, recreate that file first.

- **2026-06-21** — Moved to a **self-contained per-song layout**: each song now
  lives in `data/gallery/<song>/<song>.ly` with all its artifacts in the same
  folder (no more scattering into `data/` root). Code changes: `discover_songs`
  finds `gallery/*/*.ly`, `resolve_song` prefers the nested folder,
  `build_gallery` skips copying artifacts onto themselves, and a new
  `_include_args(ly)` walks up to find the shared `lead-sheet.ily`.
  **Gotcha that cost a build:** LilyPond `chdir`s into the input file's folder, so
  the `-I` path to the (now non-adjacent) `lead-sheet.ily` MUST be **absolute** —
  a relative `-I data` resolved against the song folder and the include vanished
  with `cannot find file: lead-sheet.ily`. `_include_args` resolves to absolute.

- **2026-06-21** — **Keep the source images.** When the user feeds notation
  images, copy them into the song folder (`data/gallery/<song>/source-page-N.png`)
  alongside the built artifacts — the user wants the originals retained as the
  verifiable source of truth, not just consumed and discarded.

- **2026-06-21** — **Zoom before you read.** Reading a full two-hand piano page
  by eye in one shot produces confident-but-wrong notes (rhythm flattens to even
  values, interior pitches drift to whatever the tune is "supposed" to be). Far
  more reliable: crop the page into one-system and even one-measure images and
  upscale ~3× with PIL (`Image.LANCZOS`), then read each crop. Include the band
  *above* the staff so fingerings/dynamics/segno/coda marks come along. Watermarks
  (e.g. a "Free" banner) can obscure a measure — re-crop neighbours to infer it.

- 2026-06-21 (entertainer_musescore): a horizontal watermark band ("All About
  Piano book by Mark Harrison Free") sat at a FIXED y across the page and landed
  squarely on the treble melody in the top system — the most information-dense
  row. Re-cropping neighbours doesn't recover it when the obscured bars ARE the
  melody. For a famous tune, cross-check the buried bars against the canonical
  melody/contour rather than guessing pixel-by-pixel. Also: a number printed
  above the very first note (here "4") was a FINGERING, not a measure number —
  don't mistake it for a bar count. And ragtime D.S./Coda navigation (Segno at
  the A-strain, "To Coda", "D.S. al Coda", final Coda bars) is best written
  LINEARLY as printed with \mark text rather than as functional volta repeats;
  \unfoldRepeats then just plays it straight through and still compiles clean.

- 2026-06-21 (entertainer_musescore) — **layout + overlay gotchas on a long
  piece.** (1) A 38-bar two-hand piece engraves onto one over-wide system unless
  you force breaks; the gallery measure-overlay then computed boxes with x up to
  ~4.1 (way past the 0..1 page fraction) and the score looked squished. Fix:
  cap measures-per-line. Do it with a parallel skip-voice of breaks
  (`lineBreaks = { s1*4 \break s1*4 \break ... }`) fed via `\new Dynamics
  \lineBreaks` between the staves — keeps the note staves single-voice (no forced
  stem flips). (2) `gallery.extract_measures` does a plain substring test
  `if "\repeat" in ly_text: return []` — so it bails on `\repeat unfold` used for
  the breaks AND, surprisingly, on the literal word `\repeat` appearing in a
  COMMENT. Write the breaks out explicitly and keep the token out of comments, or
  the playback overlay silently vanishes (0 boxes). (3) `\easyHeadsOn` +
  `\override NoteHead.note-names = #(vector "C".."B")` gives letters-in-heads on a
  dense two-hand piece too; bump `set-global-staff-size` (~21) so the letters stay
  legible.
