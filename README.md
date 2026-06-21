# leadsheet

A small **uv** package that renders LilyPond lead sheets to **PDF + verification
audio**, and lets you compose/transpose songs in Python with **music21**.

Each song is one LilyPond source (`data/*.ly`). Building it produces:

- `<song>.pdf` — engraved score (staff, chords, lyrics, and a row of letter-notes)
- `<song>.mp3` — audio rendered from the *same* notes, so you can check by ear

## Setup

```bash
brew install lilypond fluid-synth lame   # engraving + audio backends
uv sync                                   # install the package + music21
```

## Use

Via the CLI (or the equivalent `task` shortcuts):

```bash
uv run leadsheet ls                       # list songs in data/
uv run leadsheet build                    # build every song (PDF + MP3)
uv run leadsheet build happy_birthday     # one song
uv run leadsheet build --no-audio         # PDFs only
uv run leadsheet build --png              # also write a page-1 preview
uv run leadsheet build --no-gallery       # skip the automatic gallery refresh
uv run leadsheet gallery --open           # (re)build data/gallery/ and open it
uv run leadsheet demo                     # compose with music21 -> data/demo.*
```

Every `build` automatically refreshes the HTML gallery at `data/gallery/` and
prints a `file://` link to it — a landing grid plus a per-song page with the
score, the audio, and a Synthesia-style **falling-notes piano** synced to the MP3.
Run `leadsheet build --png` first so each card has a score preview.

With [go-task](https://taskfile.dev):

```bash
task                # list tasks
task build          # build all
task song -- we_wish_you_a_merry_christmas
task test           # run unit tests
task clean          # remove regenerable outputs
```

A General-MIDI soundfont is auto-discovered; override with the `MUSIC_SF2`
environment variable or `--soundfont /path/to/bank.sf2`.

## Compose in Python (music21)

```python
from leadsheet.compose import Song

song = Song.from_notation(
    "3/4 g8. g16 a4 g4 c'4 b2.",
    lyrics=["Hap", "py", "Birth", "day", "to", "you"],
    title="Happy Birthday (line 1)", key="C",
)
song.note_names                 # ['G4', 'G4', 'A4', 'G4', 'C5', 'B4']
song.to_midi("out.mid")         # native music21, no external tools
song.transposed("M2").to_midi("up.mid")
song.render_pdf("out")          # via music21 -> LilyPond
```

## Verify transcription (audio → notation, scored)

How well does automatic transcription recover the notes from the audio? Build a
reference corpus and score it:

```bash
uv run leadsheet corpus                 # data/corpus/<song>.mid + .wav pairs
uv run leadsheet verify                 # oracle engine — no ML deps, proves the loop
uv run leadsheet verify --engine piano  # real audio→notation (needs the extra below)
```

Each `.ly` is engraved to MIDI (the **ground truth**) and synthesized to WAV with
the same fluidsynth pipeline. The WAV is handed to a transcriber, whose output is
scored against the ground truth with `mir_eval` (onset+pitch precision / recall /
F1). Because the audio is synthesized *from* the ground truth, alignment is exact
and the F1 is honest — no downloads. Per piece the loop transcribes once, then
sweeps a post-filter (minimum note duration) and keeps the best-scoring setting.

Two engines, both behind a pluggable `Transcriber`:

- **oracle** (default) — degrades the ground truth (drop / jitter / spurious
  notes). Needs nothing extra, so the harness runs and is unit-tested as-is.
- **piano** — real piano transcription via
  [`piano_transcription_inference`](https://github.com/qiuqiangkong/piano_transcription_inference).
  Install the optional extra (pulls in torch; first run downloads a ~170 MB
  checkpoint):

  ```bash
  uv sync --extra transcribe
  uv run leadsheet verify --engine piano
  ```

## Layout

```
music_sheets/
  pyproject.toml          uv project (deps: music21, mir_eval, pretty_midi)
  Taskfile.yml            task runner shortcuts
  src/leadsheet/
    engine.py             render pipeline: .ly -> PDF + MP3/WAV (+ PNG)
    compose.py            music21 song definition / transpose / export
    corpus.py             reference MIDI+WAV pairs from the .ly songs
    verify.py             AMT loop: transcribe + score (mir_eval), pluggable engines
    cli.py                `leadsheet` command (build | ls | corpus | verify | demo)
  tests/                  unit tests (pure helpers + compose + verify)
  data/
    lead-sheet.ily        shared LilyPond include (letter-note formatting)
    *.ly                  one song each (the verifiable note source)
    *.pdf *.mp3           generated outputs
    corpus/               ground-truth MIDI + synth WAV (+ est/ transcriptions)
```

## Authoring a new song

Drop a `data/my_song.ly`:

```lilypond
\version "2.24.0"
\include "lead-sheet.ily"

\header { title = "My Song" tagline = ##f }

melody    = { \key c \major \time 4/4 c'4 d' e' f' | g'1 }
words     = \lyricmode { la la la la laa }
harmonies = \chordmode { c1 | g1 }

\score {
  <<
    \new ChordNames \harmonies
    \new Staff \new Voice = "mel" { \melody }
    \new NoteNames \with { noteNameFunction = #uppercase-note-name } { \melody }
    \new Lyrics \lyricsto "mel" \words
  >>
  \layout {}
  \midi { \tempo 4 = 120 }     % omit to skip audio
}
```

Then `task song -- my_song` (or `uv run leadsheet build my_song`).

`the_entertainer.ly` is the full public-domain piano rag from the
[Mutopia Project](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=263);
it carries no letter-note row (a two-hand rag would be unreadable with one).
