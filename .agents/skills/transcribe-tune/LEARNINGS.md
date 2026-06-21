# Transcription learnings

A running log of transcription mistakes that have actually shipped in this repo
and how to avoid repeating them. Add to it whenever a tune "doesn't sound right"
and you find out why. Newest entries on top.

---

## Ask which version BEFORE transcribing, if more than one exists

**Symptom:** Spent a full verify pass on `we_wish_you_a_merry_christmas.ly`
discovering it was the popular Warrell arrangement while the reference ABCs were
the traditional folk setting — *then* asked the user which one they wanted. The
answer ("the popular high-chorus version") would have scoped the whole job up
front and saved the back-and-forth.

**Lesson:** Many tunes have more than one well-known version — different
arrangements (Warrell vs. folk), keys, simplified vs. full, A-strain-only vs.
whole piece, regional/lyrical variants. They also come at different **difficulty
levels** (beginner one-hand / easy / intermediate / advanced-full), which changes
the notes as much as the arrangement does — a beginner cut drops the stride bass,
simplifies the rhythm, and narrows the range. The moment you notice (or suspect) a
tune has multiple versions, **clarify with the user which one AND what level they
want before transcribing** — and pin both choices in the `.ly` header comment so
future verification diffs against the *right* reference. "Recognizable" is only
well-defined once you know *which* version, at *what* level, is the target.

**How to apply:** Before writing notes, ask: (1) which arrangement/version, (2)
which **difficulty level** (beginner / easy / intermediate / full), (3) which key,
(4) how complete (whole piece or just the hook/A-strain). If the user has no
preference, pick the most widely-known version at a sensible level, state your
choices, and label them in the header. Then `verify-notes` against a source *of
that version and level*. (This is the kind of choice worth an explicit up-front
question — see the project's `AskUserQuestion` flow.)

---

## Sources disagreeing ≠ you're wrong (arrangement vs. original)

**Symptom:** Running `verify-notes` on `we_wish_you_a_merry_christmas.ly`, two
independent ABC sources (Chambers in G; BBC "Singing Together 1965" in B♭) agreed
with *each other* against our file on ~half the bars — a low-register chorus
(`G G G` for "tid-ings we") and the `G E D D` / `E A F#` verse cadence — while our
file has the high chorus (`C C C …`) and `C B A A` / `A B A`.

**Why it was NOT a bug:** Both ABCs encode the older **traditional English folk**
setting; our file follows the **Arthur Warrell (1935)** arrangement — the
high-"Good TID-ings" version that is by far the most widely sung today. The
signature hook ("We wish you a merry", bars 1/3/5) matched *all three*, confirming
it's the same tune, just a different arrangement. Nothing was internally
inconsistent and there was no inner-voice grab (it was authored as a clean single
line, not extracted from a chordal score).

**Contrast with the Entertainer:** There, two sources agreed against us and we
*were* wrong (a real extraction error). Here, two sources agreed against us and we
were *fine*. The difference: Joplin's Entertainer is a single **published
composition** (one authoritative original); this carol is a **traditional folk
tune** with multiple legitimate arrangements and no single "original" score.

**Generalized lesson:** When external sources disagree with you, first ask *what
kind of piece is this?* For a published composition, disagreement from an
authoritative edition means investigate — you're probably wrong. For a
traditional/folk tune, disagreement may just mean you're tracking a different
(often the more popular) arrangement. Decide which arrangement you're claiming to
reproduce, label it, and verify against a source *of that same arrangement* — a
divergent folk ABC cannot confirm or refute a Warrell-version chorus. And state
the claim precisely: "matches two sources on the hook; matches the popular
arrangement elsewhere, unverified against a same-arrangement source" is honest;
"verified" is not.

---

## Verify against the SOURCE, not your own output (circular self-check)

**Symptom:** A rewrite of `the_entertainer_simple.ly` was "confirmed" by rendering
it to MIDI and reading the MIDI back with music21 — which matched. But bar 3 had
a wrong note: it read `E G C E` where the real tune is `E C D E`.

**Root cause:** The self-check was circular. Rendering your own `.ly` to MIDI and
reading it back only proves *the build is faithful to what you wrote* — it cannot
catch a wrong note, because the wrong note is in both the source and the MIDI.
The error came from mis-reading a chord in the original score (`<c e, c>` →
took `G C` instead of the top-voice `C D`) during extraction.

**How it was caught:** An **independent internet source** — the Colin Hume **ABC
notation** of the tune (`ecde-` = E C D E) — disagreed with our file. Re-reading
the repo's own Mutopia 1902 score (`<e g, e> <c e, c> <d f, d> …`, top voice
= E C D E) confirmed the ABC was right and our file was wrong.

**Generalized lesson:** A round-trip through your own pipeline (ly → MIDI → read
back) is NOT verification — it's a tautology. Real verification compares the
result against an **independent** authoritative source (a second transcription,
an ABC file, the engraved score read note-by-note). When extracting a melody
from a multi-voice score, the trap is grabbing inner-voice or adjacent-chord
notes instead of the true top voice — cross-check the suspicious bar against a
single-line arrangement.

---

## The Entertainer (Joplin) — flat rhythm + collapsed octaves

**Symptom:** The single-line A-strain (`the_entertainer_simple.ly`) had the
correct note *letters* but the human said "it doesn't sound like The Entertainer."

**Root causes (two, compounding):**

1. **No syncopation.** The melody was written as even eighth notes. Ragtime's
   entire identity is the off-beat accent and the tie across the beat. Even
   eighths turn a rag into a finger exercise — same pitches, unrecognizable feel.
2. **Collapsed octave leaps.** The real tune jumps up to an accented **high C
   (C6 / `c'''`)** against a lower **E (E5 / `e''`)**, then the chromatic run
   `C D D# E` walks up in the *lower* octave (C5..E5). The first attempt put
   everything within a single octave (~F#4–E5), so the characteristic leaping
   contour — the part the ear latches onto — was gone.

**Why it happened:** the melody was sourced from a "piano letter notes" blog,
which lists pitch order (`D D# E | C E C E C | …`) but encodes **neither rhythm
nor octave**. The letter-note row in the rendered PDF then *looked* correct,
which masked the problem — the row only verifies pitch.

**Fix:** re-source from a format that carries rhythm (ABC notation / engraved
score), restore the dotted-eighth/sixteenth syncopation and the ties, and encode
the real octave leaps (`c'''` accent vs `e''` neighbor; run in `c''`).

**Generalized lesson → the fidelity triad:** pitch + rhythm + register. A
transcription needs all three to be recognizable. The rendered letter-note row
only proves pitch, so it can give false confidence — always ear-check the MP3.

---

## Template for new entries

```
## <Tune> — <one-line symptom>

**Symptom:** what sounded wrong / what the human said.
**Root cause:** which of pitch / rhythm / register (or sourcing) failed.
**Why it happened:** the trap that led there.
**Fix:** what made it sound right.
**Generalized lesson:** the reusable takeaway.
```
