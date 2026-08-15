# Repository Guidelines

## Project Structure & Module Organization

This repository is a self-contained Windows Chinese-chess application. `server.py` starts the local HTTP server, owns the Pikafish subprocess, and exposes `/api/legal` and `/api/engine`. `web/index.html` contains the complete browser UI, including styles and JavaScript. `tests/` contains standard-library unit tests. `Pikafish/` holds the bundled engine executable, NNUE weights, licenses, and upstream documentation; treat `pikafish.exe` and `pikafish.nnue` as paired runtime assets. `启动象棋.bat` is the end-user launcher, and `使用说明.txt` documents operation.

## Build, Test, and Development Commands

The project has no build step or third-party Python packages; it uses the standard library.

- `启动象棋.bat` — launch the server and open `http://127.0.0.1:8899` on Windows.
- `python server.py` — run the server directly for development.
- `python -m py_compile server.py` — perform a fast Python syntax check.
- `python -m unittest discover -s tests -v` — run the unit test suite.
- `curl.exe -X POST http://127.0.0.1:8899/api/legal -H "Content-Type: application/json" -d "{\"moves\":[]}"` — smoke-test the legal-moves endpoint while the server is running.

Run commands from the repository root so relative engine and web paths resolve consistently.

## Coding Style & Naming Conventions

Use four spaces for Python indentation and follow PEP 8 conventions: `snake_case` for functions and variables, `PascalCase` for classes, and `UPPER_CASE` for constants. Keep request handling thin; engine/UCI behavior belongs in `Engine`. In the single-file frontend, use two-space indentation, `camelCase` JavaScript names, and descriptive DOM IDs. Preserve UTF-8 encoding because the interface and documentation contain Chinese text. No formatter or linter is configured, so match nearby style and keep changes focused.

## Testing Guidelines

Tests use Python's `unittest`; no coverage target is configured. Name files `test_*.py` and keep engine-protocol tests deterministic with fake streams where possible. Before submitting, run the suite, launch the app, start games as both colors, make and undo moves, and exercise changed difficulty controls. For API changes, verify successful JSON responses and an error case.

## Commit & Pull Request Guidelines

Recent commits use concise Chinese summaries such as `新增拖动落子...` and `修复...`; follow that imperative, feature-first style and keep each commit scoped. Pull requests should explain user-visible behavior, list manual verification, and link related issues. Include a screenshot or short recording for UI changes. Call out changes to bundled engine binaries, NNUE weights, ports, or API payloads explicitly.
