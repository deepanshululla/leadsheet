# Skill registry — `leadsheet`

Canonical skills live in `.agents/skills/<name>/SKILL.md` (portable agents.md
location). `.claude/skills/<name>` are symlinks back to them for Claude Code
discovery. Cursor reads the same set via `.cursor/INDEX.md`.

## Skills

| Skill | Use when… |
|-------|-----------|
| [image-to-song](skills/image-to-song/SKILL.md) | the user **pastes/attaches an image** of notation (photo, screenshot, letter notes, tabs, handwriting) and wants the whole song built — `.ly` + `.pdf` + `.mp3` + `.png` + gallery `.html`/`notes.json` |
| [add-song](skills/add-song/SKILL.md) | adding / creating / transcribing a song as sheet music; authoring a new `.ly` lead sheet |
| [transcribe-tune](skills/transcribe-tune/SKILL.md) | a known melody must sound RECOGNIZABLE (pitch + rhythm + register), or a transcription "doesn't sound like the song" |
| [verify-notes](skills/verify-notes/SKILL.md) | checking a transcription has the RIGHT notes against an independent source |
| [render-leadsheet](skills/render-leadsheet/SKILL.md) | building / rendering / regenerating the PDFs and verification audio |
| [build-gallery](skills/build-gallery/SKILL.md) | visualizing/previewing the songs as an HTML gallery with a falling-notes piano |
| [compose-music21](skills/compose-music21/SKILL.md) | defining a melody in Python, transposing / changing key, exporting MIDI |

## Rules

| Rule | Covers |
|------|--------|
| [lilypond-pipeline](rules/lilypond-pipeline.md) | engraving + audio conventions and gotchas (fluidsynth arg order, `\midi`, includes) |
| [python-package](rules/python-package.md) | uv workflow, module split, testing, error handling, style |

## Subagents

| Agent | Role |
|-------|------|
| [song-builder](agents/song-builder.md) | end-to-end: add a song, build it, verify the PDF + audio |
