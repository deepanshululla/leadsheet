# Learnings — add-song

Running log of non-obvious lessons from authoring `.ly` lead sheets. Append a
dated bullet when you hit a gotcha, a fix, or a discovery worth not re-learning.
Newest first.

## 2026-06-21 — ALWAYS use the internet; NEVER transcribe notes from memory
Hard rule: before writing any `.ly` for a known tune, search the web for a real
source — do not generate notes from recall. Recalled melodies come out plausible
but wrong, and "sounds off" is exactly what the user hears. Run the
`transcribe-tune` / `verify-notes` step 1: prefer ABC notation, then MusicXML/MIDI,
then an engraved score; letter-note blogs are simplified easy-versions (usable but
lowest-trust). Confirm the **key** from the source too (Rush E is A-minor /
Am-Em-Dm-E, not the C/E-minor a guess suggested). If no source can be found, say so
and label the result "transcribed by ear, unverified" — never pass a guess off as
accurate. Copyright affects *labeling and source availability*, not whether you may
transcribe a recognizable version.

## 2026-06-21 — a lead sheet only sounds the MELODY; chords are silent in MIDI
`ChordNames` are printed but never go to MIDI, so the MP3 of a single-line lead
sheet is just the melody — fine for simple tunes, useless for anything whose
identity lives in its harmony/accompaniment (e.g. Rush E's driving left hand).
To put harmony in the audio, score an actual second voice/staff and include BOTH
staves in the `\midi` score (with `\unfoldRepeats`). See `the_entertainer.ly`'s
two-`\score` setup (PianoStaff for layout, a second score feeding `\midi`).

## 2026-06-21 — pickup beats: `\partial` + a matching chord skip
For an anacrusis, use `\partial 4` in the melody and a `s4` (silent skip) at the
front of the `\chordmode` line so chords stay aligned with the bar, not the
pickup. See the template and `happy_birthday.ly`.

## 2026-06-21 — one syllable per note; melismas need a slur
`\lyricsto` assigns exactly one lyric syllable per note. A syllable held across
several notes (a melisma) shifts every later lyric unless those notes are slurred
in the music, e.g. `b'( a')`. Symptom: lyrics drift out from under their notes.

## 2026-06-21 — dense two-hand piano: drop the NoteNames staff
A letter-note under every note is unreadable for a full piano texture. Omit the
`\new NoteNames …` line for those (see `the_entertainer.ly`); keep it for simple
single-line melodies.

## 2026-06-21 — verify transcribability, not just the look
Beyond opening the PDF and ear-checking the MP3, the song can be scored: rebuild
the corpus (`task corpus`) and run `task verify` to get an onset+pitch F1 against
the engraved notes. Note the corpus audio is *synthesized*, so the F1 is
optimistic vs a real recording — it catches gross note errors, not subtle ones.

## 2026-06-21 — prefer an accurate public-domain source over transcribing by ear
For known/complex repertoire, copy from Mutopia/IMSLP rather than hand-
transcribing. If you do transcribe by eye/ear, say so explicitly and have a human
ear-check the MP3 — the letter-note row makes pitch errors easy to spot.
