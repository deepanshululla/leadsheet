---
name: add-song
description: "Add a new song to the leadsheet collection. Use when asked to add, create, transcribe, or import a song / tune / melody / carol / piece as sheet music, or to author a new LilyPond .ly lead sheet. Covers picking a key, writing melody + lyrics + chords, the shared note-name include, and building the PDF + verification audio."
---

# Add a song to the collection

A song is **self-contained in its own folder** `data/gallery/<song>/`: the
LilyPond source `data/gallery/<song>/<song>.ly` plus everything building it
produces — `<song>.pdf` (engraved score), `<song>.mp3` (audio from the same
notes), the preview PNG, and the gallery `index.html` + `notes.json`. The folder
name and the `.ly` stem must match. The only shared file is `data/lead-sheet.ily`
(the letter-note helper), which the engine resolves from the nested folder.

## Steps

1. **Get accurate notes.** For well-known/complex repertoire, prefer an accurate
   public-domain source (e.g. Mutopia Project) over hand-transcription. If you do
   transcribe by eye/ear, say so and have the human ear-check the MP3.
2. **Create `data/gallery/<song>/<song>.ly`** from the template below (make the
   folder). Pick a readable key (C major needs no accidentals; match the source
   otherwise). Write the include as `\include "lead-sheet.ily"` (no path).
3. **Build it:** `task song -- <song>` (or `uv run leadsheet build <song>`) — the
   name resolves to the nested folder and outputs land there.
4. **Verify:** open the PDF and listen to the MP3. Read the letter-note row to
   confirm pitches against the source.

## Template

```lilypond
\version "2.24.0"
\include "lead-sheet.ily"            % shared uppercase-note-name helper

\header { title = "My Song" composer = "Traditional" tagline = ##f }

melody    = { \key c \major \time 3/4 \partial 4
              g'8. g'16 | a'4 g'4 c''4 | b'2. }
words     = \lyricmode { Hap -- py Birth -- day to you }
harmonies = \chordmode { s4 | c2. | g2.:7 | c2. }

\score {
  <<
    \new ChordNames \harmonies
    \new Staff \new Voice = "mel" { \melody }
    \new NoteNames \with { noteNameFunction = #uppercase-note-name } { \melody }
    \new Lyrics \lyricsto "mel" \words
  >>
  \layout {}
  \midi { \tempo 4 = 112 }           % omit to skip audio
}
```

## Notes

- One lyric syllable per note; melismas need a slur in the music, e.g. `b'( a')`.
- For a dense two-hand piano piece, omit the `\new NoteNames …` line (a letter
  under every note is unreadable) — see `the_entertainer.ly`.
- Letter-note formatting lives once in `data/lead-sheet.ily`; don't duplicate it.

## Learnings

Read `LEARNINGS.md` in this folder before starting (accumulated gotchas), and
append a dated bullet whenever you hit a new one.
