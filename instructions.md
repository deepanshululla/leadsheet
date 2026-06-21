# leadsheet — Cursor project context

This is the Cursor entry point. The **canonical project guide is `CLAUDE.md`**
(also discoverable as `AGENTS.md`); read it first.

- **What:** a uv package that renders LilyPond lead sheets to PDF + verification
  audio, and composes/transposes songs in Python with music21.
- **Skill registry:** `.cursor/INDEX.md` (shared skills in `.agents/skills/`).
- **Rules:** `.cursor/rules/*.mdc` (engraving pipeline, Python package conventions).
- **Workflow:** `uv sync`, then `task build` / `task test` / `task song -- <name>`,
  or `uv run leadsheet …`.

See `CLAUDE.md` for development practices (TDD, verify-before-done, transcription
accuracy) and pipeline gotchas.
