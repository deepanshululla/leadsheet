# Project Guidance for AI Coding Agents — `leadsheet`

> **Universal entry point.** This file is the canonical project context for any AI
> coding agent. It is discoverable as both `CLAUDE.md` (Claude Code's convention)
> and `AGENTS.md` (the universal [agents.md](https://agents.md/) convention — read
> by Codex, Cursor's agent mode, Aider, Windsurf, …). `AGENTS.md` is a symlink to
> `CLAUDE.md`; they are the same file. Edit `CLAUDE.md`; `AGENTS.md` follows.

## What this project is

`leadsheet` is a small **uv** package that turns public-domain / original songs
into **engraved PDF lead sheets plus verification audio**, and lets you
compose/transpose melodies in Python with **music21**.

The core idea is *verifiability*: every song's notes exist as readable text (a
LilyPond `.ly` source) and as sound (an `.mp3` rendered from the same notes), so a
sheet can be checked two ways — read it, or listen to it.

## Multi-agent setup (Claude Code + Cursor + AGENTS.md-aware agents)

Each runtime has its own discovery surface; they share one skill registry.

| Layer | Claude Code | Cursor | AGENTS.md-aware (Codex, Aider, …) |
|-------|-------------|--------|-----------------------------------|
| Project context | `CLAUDE.md` (this file) | `instructions.md` | `AGENTS.md` → symlink to `CLAUDE.md` |
| Skill registry | `.claude/INDEX.md` | `.cursor/INDEX.md` | `.agents/skills/*/SKILL.md` |
| Rules | `.claude/rules/*.md` | `.cursor/rules/*.mdc` | reuse `.claude/rules/*.md` |
| Skill surface | `.claude/skills/<name>/` (symlinks) | `.cursor/INDEX.md` references | `.agents/skills/<name>/` (canonical) |
| Subagents | `.claude/agents/<name>.md` | — | — |

**Canonical skills live in `.agents/skills/`** (the portable agents.md location).
`.claude/skills/<name>` are symlinks back to them so Claude Code can discover them.

## Quick start

```bash
brew install lilypond fluid-synth lame   # engraving + audio backends
uv sync                                   # install package + music21 + pytest
task                                      # list task-runner shortcuts
task build                                # render every song in data/
task test                                 # run unit tests
```

CLI: `uv run leadsheet build [song] [--no-audio|--png|--open|--soundfont]`,
`uv run leadsheet ls`, `uv run leadsheet demo`.

## Layout

```
src/leadsheet/   engine.py (render pipeline), compose.py (music21), cli.py
tests/           pytest unit tests (pure helpers + compose)
data/            lead-sheet.ily (shared include)
data/gallery/<song>/   self-contained per song: <song>.ly source + built
                       .pdf/.mp3/_preview-1.png + index.html + notes.json
data/gallery/    index.html (landing) + assets/  (regenerable)
.claude/ .cursor/ .agents/   agent scaffolding (this doc + skills/rules)
```

Each song lives in its **own folder** under `data/gallery/<song>/` — source and
all artifacts together. `task clean` removes the generated files but keeps each
`<song>.ly`. (A legacy flat `data/<song>.ly` is still built, into the matching
gallery folder.)

## Development practices

### Test-driven development (TDD)

For new code (functions, modules, helpers) write a failing test under `tests/`
first, then the minimum code to pass, then refactor. Applies to pure logic in
`engine.py` / `compose.py`. Does **not** apply to: prose (rules, SKILL.md,
README), `.ly` song sources, or one-off scripts. When TDD doesn't fit
(subprocess orchestration, exploring music21's API), say so explicitly and verify
by running the CLI instead — see the existing engine tests, which cover the pure
helpers while the pipeline is verified by `task build`.

### Verify before declaring done

Don't claim a song or feature works on intent alone. Prove it: build the `.ly`
and open the PDF; run `task test`; for melody changes, render the MP3 and confirm
by ear. "I ran `task build` and the PDF/MP3 regenerated" beats "should work".

### Music transcription accuracy

Notes transcribed by eye/ear from a source score are error-prone — flag them and
have a human ear-check the MP3. Prefer downloading an accurate public-domain
LilyPond source (e.g. the [Mutopia Project](https://www.mutopiaproject.org/)) over
hand-transcribing complex pieces; run `convert-ly -e <file>.ly` to update old
sources to the installed LilyPond version.

## Pipeline gotchas (load `.claude/rules/lilypond-pipeline.md`)

- A song's `\score` needs a `\midi { \tempo … }` block to get audio; add
  `\unfoldRepeats` in the midi score so repeats play.
- **fluidsynth needs the soundfont and MIDI paths LAST** in its argument list or
  it silently writes nothing.
- Songs `\include "lead-sheet.ily"`; the engine passes `-I <data dir>` so the
  include resolves regardless of working directory.

## Skills

See `.claude/INDEX.md` for the registry. Current skills: **image-to-song**
(paste a notation image → full song build), **add-song**, **transcribe-tune**,
**verify-notes**, **render-leadsheet**, **build-gallery**, **compose-music21**.
