---
name: image-to-song
description: "Turn pasted images of music notation into a full song entry — read the notes off the picture and produce every artifact: the .ly source, the engraved .pdf, the verification .mp3, the page preview .png, and the gallery .html + notes.json. Use when the user pastes / attaches / drops a photo, screenshot, or scan of sheet music, staff notation, 'piano letter notes', numbered/Synthesia tabs, a chord chart, or handwritten notes and wants it built into a playable lead sheet. The image IS the source of truth."
---

# Paste a notes image → get the whole song

The user gives one or more **images of music** (photo of a score, a screenshot,
"piano letter notes", numbered tabs, handwriting). You read the notes off the
image and run them through the existing pipeline so that **one command emits
every file the user wants**.

**Every song is self-contained in its own folder `data/gallery/<song>/`** — the
`.ly` source and every generated file live together, nothing scattered in
`data/` root:

```
data/gallery/<song>/
  <song>.ly                 ← you write this from the image (source of truth)
  <song>.pdf                ← engraved score            (leadsheet build)
  <song>.mp3                ← audio from the same notes  (leadsheet build)
  <song>_preview-1.png      ← page-1 image               (leadsheet build --png)
  index.html                ← score + audio + falling-notes piano (gallery)
  notes.json                ← per-note [midi, start_s, dur_s] timeline (gallery)
```

Plus shared, regenerable `data/gallery/index.html` (landing grid) and
`data/gallery/assets/`. The one file that is **not** copied into each folder is
`data/lead-sheet.ily` (the shared letter-note helper) — it stays at the songs
root and the engine finds it from the nested folder automatically.

So your only real job is **reading the image into an accurate `.ly`**. Everything
downstream is one build. Read the sibling skills `add-song` (the `.ly` template +
key choice), `transcribe-tune` (making it sound right), and `verify-notes`
(checking it) — this skill is the image front-door that feeds them.

## Procedure

1. **Read the image carefully, top to bottom.** Don't guess from the title.
   Identify, in order:
   - **Clef** (treble/bass) — sets the octave. Getting this wrong transposes the
     whole piece.
   - **Key signature** — count sharps/flats; pick the matching `\key`.
   - **Time signature** — sets `\time` and the bar math.
   - **Tempo / feel** — any `♩ = N` marking → `\midi { \tempo 4 = N }`.
   - Then go **note by note, bar by bar**: pitch letter, accidental, octave
     (which staff line/space), and **duration** (note-head fill, stems, flags,
     beams, dots, ties, rests).
2. **Apply the fidelity triad** (`transcribe-tune`): pitch, **rhythm**
   (syncopation/dotted figures/ties — the most-dropped dimension), and
   **register** (octave leaps are part of the tune). The bar lines and beaming in
   the image tell you the rhythm — use them, don't flatten to even eighths.
3. **Clarify only what the image cannot tell you.** If the image has no title,
   ask what to name it (`<song>` becomes the filename, lowercase-with-underscores).
   If notation is ambiguous or cut off, say which bars and ask — don't invent.
4. **Write `data/gallery/<song>/<song>.ly`** (create the folder) from the
   `add-song` template. `<song>` is lowercase-with-underscores; the folder name
   and the `.ly` stem must match. It `\include "lead-sheet.ily"` (the shared
   helper at `data/lead-sheet.ily` — the engine resolves it from the nested
   folder, so write the include exactly as `"lead-sheet.ily"`, no path). For a
   single melody line keep the `\new NoteNames …` row (prints letter notes under
   the staff); for a dense two-hand piece, drop that row. Add per-bar `% C D E`
   comments of what you read so the transcription is auditable.
5. **Build everything:** `uv run leadsheet build <song> --png` (or `task song -- <song>`).
   `<song>` resolves to the nested folder; the PDF/MP3/PNG are written **into that
   folder** and the gallery refresh adds `index.html` + `notes.json` alongside.
   It prints a `file://` link to the gallery — give it to the user.
6. **Verify against the image** (`verify-notes`): open
   `data/gallery/<song>/<song>_preview-1.png` and diff it **bar by bar against the
   original image** — same pitches, same
   rhythm, same octave. Then **listen to the `.mp3`**. The image is the
   independent source here, so this comparison is real verification, not a
   round-trip. For a famous tune, optionally cross-check one external source
   (ABC/Mutopia) to catch errors in the image itself.

## Reading different image types

| Image type | How to read it | Watch out for |
|------------|----------------|---------------|
| **Staff notation** (photo/scan/screenshot) | clef + key + line/space → pitch & octave; note-heads/beams/dots → rhythm | bass clef octave; key-sig accidentals apply all bar; multi-voice → take the **top** line |
| **"Piano letter notes"** (`C D E G…`) | gives pitch **class** order only | **no rhythm, ambiguous octave** — ask for tempo/feel or infer from the tune; never trust for duration |
| **Numbered / Synthesia / piano-roll** | key index or falling-bar position → pitch; bar length → duration | mapping the number system to actual pitches; left-hand vs right-hand split |
| **Chord chart / lead sheet** | chord symbols → `\chordmode` harmonies; melody line if present | a chart may have *no* melody — confirm with the user before inventing one |
| **Handwritten** | same as staff but read conservatively | messy stems/accidentals — flag low-confidence bars |

## Be honest about what you read

Transcribing from a picture is error-prone: blurry scans, cut-off bars, your own
misread of a ledger line. **Flag any bar you were unsure of**, say if you
simplified the rhythm or guessed an octave, and ask the user to ear-check the MP3.
"Recognizable transcription, bars 5–6 uncertain" beats a confident wrong claim.

## Gotchas

- Each song is **self-contained** in `data/gallery/<song>/`; don't write the
  `.ly` or any artifact to `data/` root. `task clean` deletes the generated files
  in each folder but **keeps `<song>.ly`** — the source is safe.
- The build needs `data/lead-sheet.ily` to exist (the `\include` target). The
  engine passes its folder as a LilyPond `-I` path, resolved **absolute** (Lily
  `chdir`s to the song folder, so a relative include path would miss). If a
  `\include "lead-sheet.ily"` "cannot find file" error appears, the helper was
  deleted — recreate it (the `uppercase-note-name` Scheme helper) before building.
- A score needs a `\midi { \tempo … }` block or there's **no MP3 and no
  `notes.json`** (the piano viz reads timing from the MIDI). Always include one.

## Learnings

Read `LEARNINGS.md` in this folder before starting and append a dated bullet when
you hit a new image-reading gotcha.

See also: `add-song`, `transcribe-tune`, `verify-notes`, `build-gallery`.
