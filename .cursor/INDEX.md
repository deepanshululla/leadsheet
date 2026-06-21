# Skill registry (Cursor surface) — `leadsheet`

Cursor's project context is `instructions.md` (points back to `CLAUDE.md`).
Skills are canonical in `.agents/skills/<name>/SKILL.md`; rules for Cursor's agent
mode live in `.cursor/rules/*.mdc` (MDC frontmatter).

## Skills

| Skill | Use when… |
|-------|-----------|
| [image-to-song](../.agents/skills/image-to-song/SKILL.md) | the user pastes an image of notation and wants the whole song built (`.ly`+`.pdf`+`.mp3`+`.png`+gallery `.html`/`.json`) |
| [add-song](../.agents/skills/add-song/SKILL.md) | adding / transcribing a song; authoring a new `.ly` lead sheet |
| [transcribe-tune](../.agents/skills/transcribe-tune/SKILL.md) | making a known melody sound recognizable (pitch + rhythm + register) |
| [verify-notes](../.agents/skills/verify-notes/SKILL.md) | checking a transcription's notes against an independent source |
| [render-leadsheet](../.agents/skills/render-leadsheet/SKILL.md) | building / regenerating PDFs + audio |
| [build-gallery](../.agents/skills/build-gallery/SKILL.md) | visualizing the songs as an HTML gallery with falling-notes piano |
| [compose-music21](../.agents/skills/compose-music21/SKILL.md) | composing / transposing in Python, exporting MIDI |

## Rules

- [lilypond-pipeline.mdc](rules/lilypond-pipeline.mdc) — engraving + audio pipeline
- [python-package.mdc](rules/python-package.mdc) — uv workflow, module split, testing
