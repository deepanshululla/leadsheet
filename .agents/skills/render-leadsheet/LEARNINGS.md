# Learnings — render-leadsheet

Running log of non-obvious lessons from rendering lead sheets. Append a dated
bullet when you hit a gotcha, a fix, or a discovery worth not re-learning.
Newest first.

## 2026-06-21 — fluidsynth: soundfont + MIDI must be the LAST two args
`fluidsynth -ni -F out.wav -r 44100 <soundfont> <midi>` writes an **empty** file
if the soundfont/MIDI come earlier in the arg list. The order is load-bearing;
`engine.midi_to_wav` encodes it. Don't reorder for "readability".

## 2026-06-21 — LilyPond writes tempo/key on a non-zero MIDI track
Reading a LilyPond-produced `.mid` with `pretty_midi` prints
`RuntimeWarning: Tempo, Key or Time signature change events found on non-zero
tracks`. It is **benign** — pretty_midi still reads the tempo correctly
(verified: 112 bpm and 150 bpm matched raw `mido` set_tempo exactly). Do *not*
"fix" it by rewriting the MIDI; just suppress the warning at the read site (see
`verify.notes_from_midi`).

## 2026-06-21 — MIDI is only emitted when the score has a `\midi` block
No `\midi { … }` → LilyPond produces a PDF but no `.mid`, so audio (and corpus
ground truth) is skipped. `engine.build_one` warns and moves on rather than
failing.

## 2026-06-21 — the auto-discovered soundfont is not a clean grand piano
On this machine discovery lands on `VintageDreamsWaves-v2.sf2`. Fine for
ear-checking, but it colors the audio — relevant if you feed the WAV to piano
transcription (`leadsheet verify --engine piano`). Override with `MUSIC_SF2` or
`--soundfont` for a cleaner General-MIDI grand if transcription quality matters.

## 2026-06-21 — `midi_to_wav` exists for callers that need WAV, not MP3
`engine.midi_to_wav(midi, wav, soundfont)` was extracted from `midi_to_mp3`; the
corpus builder uses it directly so it doesn't pay the `lame` step.
