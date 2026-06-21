# Rule: Python package conventions

This is a uv-managed package (`pyproject.toml`, `src/leadsheet/` layout).

## Environment

- Manage deps with **uv**: `uv sync` to install, `uv add <pkg>` to add a runtime
  dep, `uv add --dev <pkg>` for a dev dep. Don't hand-edit installed packages.
- Run anything in the project env with `uv run …` (e.g. `uv run pytest`,
  `uv run leadsheet build`). A `VIRTUAL_ENV … does not match` warning appears when
  a parent repo's venv is active — harmless, ignore it.
- Prefer the `task` shortcuts (`task build|test|song|clean|…`) over raw commands.

## Code

- Keep the split: `engine.py` = rendering pipeline (subprocess orchestration),
  `compose.py` = music21 composition, `cli.py` = argparse surface only (thin).
- Pure helpers (soundfont ranking, song resolution, note-name logic) get unit
  tests in `tests/`. Subprocess steps are verified by running the CLI, not mocked.
- Raise `engine.BuildError` for user-facing failures; the CLI prints it and exits
  non-zero. Don't swallow tool errors silently.
- Match the surrounding style: type hints, `from __future__ import annotations`,
  short docstrings, `pathlib.Path` over string paths.
