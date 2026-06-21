---
name: transcribe-tune
description: "Transcribe a known melody so it is actually RECOGNIZABLE — get pitch, rhythm, and register all right, not just the note letters. Use when adding/transcribing a famous tune (ragtime, jazz, folk, pop hook) and it must sound correct by ear, when a transcription 'doesn't sound like the song', or when fixing a melody that has the right notes but wrong feel. Complements add-song (which covers the .ly mechanics)."
---

# Transcribe a tune so it sounds right

`add-song` covers the LilyPond mechanics. This skill covers the hard part:
making the melody **recognizable**. A transcription fails the ear test when any
one of three dimensions is wrong — getting the note letters right is not enough.

Read `LEARNINGS.md` in this folder first — it's the running log of mistakes that
have actually shipped here and how to avoid repeating them.

## The fidelity triad — all three, or it won't sound like the song

1. **Pitch** — the note letters (C, D, E…) and accidentals.
2. **Rhythm** — durations and, crucially, **syncopation**. This is the #1 thing
   people drop. Ragtime/jazz/swing live on notes that land *off* the beat and
   tie *across* it. Flattening to even eighths makes any rag sound like a scale
   exercise. Match the source's dotted figures, sixteenths, and ties.
3. **Register (octave)** — the same letter at the wrong octave kills the tune.
   Many melodies leap up to an *accented high note* against lower neighbors
   (e.g. The Entertainer jumps to a high C against a lower E). Collapse those
   leaps into one octave and the contour — the thing the ear recognizes — is gone.

## Sourcing — pick a format that encodes rhythm

Choose your source by what it preserves:

| Source | Pitch | Rhythm | Octave | Verdict |
|--------|-------|--------|--------|---------|
| **ABC notation** (abcnotation.com) | ✅ | ✅ | ✅ | **best** — parseable, translate to LilyPond |
| **MusicXML / MIDI** (Mutopia, MuseScore) | ✅ | ✅ | ✅ | great if you can read it |
| Engraved PDF score (IMSLP, Mutopia) | ✅ | ✅ | ✅ | good, but read carefully |
| "Piano letter notes" / kalimba tabs | ✅ | ❌ | ⚠️ | **pitch order only** — never trust for rhythm/octave |

Letter-note lists (`D D# E | C E C E C | …`) are useful to confirm the pitch
*sequence*, but they throw away rhythm and are ambiguous about octave. Use them
to cross-check, not as the primary source.

## Procedure

0. **Clarify the target first.** Many tunes have several well-known versions
   (arrangement, key) and difficulty **levels** (beginner one-hand / easy /
   intermediate / full). These change the notes as much as anything. If more than
   one plausibly fits, **ask the user which version AND what level** before
   transcribing, then record both in the `.ly` header so `verify-notes` diffs
   against the right reference. No preference given → pick the most widely-known
   version at a sensible level, say which, and label it. See `LEARNINGS.md`.
1. **Find a rhythm-bearing source** (ABC ideal). Search `"<tune>" ABC notation`.
2. **Translate to LilyPond**, preserving durations, ties, and octave marks.
   Keep it a single top-line melody so the letter-note row stays readable.
3. **Pick the register deliberately.** Note where the melody leaps to a high
   accent vs. where a run sits low — encode those as real octave changes
   (`c'''` vs `c''`), don't smooth them out.
4. **Build + ear-check.** `uv run leadsheet build <song> --png`. Then *listen to
   the MP3* — this is non-negotiable; the letter-note row only proves pitch.
5. **Read the preview PNG.** Confirm the rhythm shows syncopation (dotted notes,
   ties), not a flat row of eighths.
6. **Log anything new** you learned into `LEARNINGS.md`.

## Be honest about caveats

If you simplified the rhythm, transcribed only the A-strain, or guessed an
octave, say so to the human and ask them to ear-check the MP3. A "recognizable
fragment" is fine — but label it as one.

See also: `add-song` (file template, key choice, chords/lyrics), `render-leadsheet`
(the build pipeline).
