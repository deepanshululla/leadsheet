---
name: verify-notes
description: "Verify that a transcribed melody has the RIGHT notes — by comparing it against an independent authoritative source, not by round-tripping it through your own pipeline. Use after transcribing/editing a song's .ly, before declaring it correct, when a tune 'doesn't sound right', or when asked to check/verify/proofread the notes of a lead sheet. Pairs with transcribe-tune."
---

# Verify a transcription's notes

The one rule: **verification means comparing against something independent of
the thing you're verifying.** A check that only consults your own output proves
fidelity, never correctness.

Read `../transcribe-tune/LEARNINGS.md` — it has the real case where a wrong note
(`E G C E` instead of `E C D E`) survived a self-check and was only caught by an
independent source.

## Two kinds of "verification" — don't confuse them

| Check | What it proves | Catches wrong notes? |
|-------|----------------|----------------------|
| **Round-trip** — render `.ly` → MIDI → read it back (music21); or `leadsheet verify` (audio → AMT → score F1 vs. the same MIDI) | the build/synthesis is faithful to **what you wrote** | ❌ **No** — the wrong note is in both sides |
| **External** — diff your notes against an **independent** transcription / engraved score | your notes match the **real song** | ✅ **Yes** |

`leadsheet corpus` + `leadsheet verify` is a useful *pipeline* test (does the
audio reproduce the score?). It is **not** a note-correctness test. For "are
these the right notes?", you must go external.

## Procedure (external verification)

1. **Get your rendered pitch sequence.** Read the letter-note row in
   `data/<song>_preview-1.png`, or the per-note `% C D E` comments in the `.ly`.
   List it **bar by bar** as pitch classes.
2. **Get an independent reference** — ranked by trustworthiness:
   - **ABC notation** (abcnotation.com) — text, encodes exact pitch + octave +
     rhythm; ideal for a literal diff. Search `"<tune>" ABC`.
   - The **engraved public-domain score** (IMSLP / Mutopia), read note by note.
   - A second arrangement, to break ties.
3. **Diff bar by bar.** Line up the two pitch-class sequences per measure. Any bar
   that differs is a finding — investigate, don't hand-wave.
4. **Resolve discrepancies with a SECOND source.** Two independent sources that
   agree beat one. (In the real case, the internet ABC *and* the repo's Mutopia
   score both said `E C D E`; only our file disagreed → our file was wrong.)
5. **Ear-check the MP3.** Catches register/octave and rhythm-feel errors that a
   pitch-class list misses.

## Traps that produce wrong notes

- **Circular self-check** — `ly → midi → read back` is a tautology. So is
  `leadsheet verify` for note-correctness. Always compare to something external.
- **Inner-voice grab** — extracting a melody from a multi-voice/chordal score and
  taking an inner or adjacent-chord note instead of the **top voice**. This is
  exactly how `E C D E` became `E G C E`. Cross-check chordal bars against a
  single-line arrangement.
- **Octave-blind sources** — "piano letter notes" lists give pitch *class* only;
  they can't confirm register. Use them to diff pitch order, not octave.
- **Arrangement vs. original** — a folk/simplified arrangement may legitimately
  differ (octave, passing notes) from the composer's original. Decide which one
  you're claiming to reproduce and verify against *that*, and label it.

## Report honestly

State what source(s) you compared against, list every bar that differed and how
you resolved it, and flag anything you could only confirm by one source or by
ear. "Matches two independent sources" and "matches one, unverified" are
different claims — say which.

See also: `transcribe-tune` (authoring + the fidelity triad), `render-leadsheet`
(the build that produces the audio you ear-check).
