# .github/copilot-instructions.md

Purpose
- Quickly onboard AI coding agents to this repo: architecture, workflows, integration points, and repo-specific patterns.

Quick overview
- Browser-based UI that runs Python validation via Pyodide to check IFC files against IDS specs and produce reports.
- Key files: `index.html`, `main.js`, `style.css`, `app.py`, `wheels/`.

Architecture & dataflow
- On load: browser loads Pyodide (v0.26.0) and runs `init_packages()` from `app.py` via `pyodide.runPythonAsync()` to install packages with `micropip`.
- User uploads IFC/IDS -> `main.js` converts to `Uint8Array`, sets Pyodide globals (`ifc_bytes_global`, `ids_bytes_global`).
- Preview: `validate_and_show_html()` in `app.py` builds IFC model with `ifcopenshell`, parses IDS via `ifctester.ids.from_string`, runs `my_ids.validate(model)`, and returns HTML + stats.
- Download: `generate_report(ifc_bytes, ids_bytes, format)` must return raw bytes for the frontend to `Blob()` and download (Html/Json/Ods/Bcf).

Project-specific conventions & gotchas
- `app.py:init_packages()` installs wheels via remote raw GitHub URLs. `wheels/` contains offline wheel references but is not used unless `init_packages()` is changed.
  - Note: recent edits make init_packages() prefer ./wheels/*.whl (served by the local static server) before falling back to remote URLs.

- Binary report path: `generate_report()` may call `rep.to_file(tmp_path)` and read `/tmp` — ensure the target Python environment supports this (Pyodide has a different FS model).
  - Pyodide caveat: prefer returning bytes from generate_report() instead of relying on writing to /tmp. The front-end expects a bytes-like object (Uint8Array) named report_bytes when calling generate_report(); avoid OS-specific temp paths where possible.

- Encoding: uploaded bytes are decoded with `errors="ignore"` and outputs are UTF-8; JSON uses `ensure_ascii=False` for Cyrillic.
- Pyodide globals lifecycle: `main.js` sets and deletes globals. Follow that pattern to avoid memory leaks.

Dev tips
- If you add or update wheels, run a local static server and clear browser cache or append a cache‑busting query to pyodide/app imports.
- For debugging, always log full exception objects in the browser console (console.error) — Pyodide stack traces are printed there.
- Test report download flow with small sample files first (Html/Json), then ODS/BCF to validate binary handling.

Debugging & developer workflows
- Serve locally for testing:

  ```bash
  python3 -m http.server 8000
  # open http://localhost:8000/index.html
  ```

- Inspect browser console and the on-page `#output` for runtime logs; use `console.error()` to capture full Pyodide exceptions.
- When updating wheels or Pyodide, clear browser cache or add cache-busting query strings.
- To reproduce logic locally (native Python): run similar flows in a virtualenv, but expect differences (no `micropip`, different FS semantics).

Files to check first when editing
- `main.js` — UI ↔ Pyodide interaction, global variables, download mapping.
- `app.py` — package installation, validation API, report generation.
- `index.html` — DOM ids and script order.
- `wheels/` — add/update wheel files if switching to local installs.

Common edits (examples)
- Adding a report format: add option in `index.html`, implement format branch in `generate_report()` in `app.py`, map MIME/extension in `main.js`.
- Using local wheels: change `init_packages()` to `await micropip.install("./wheels/your.whl")` and ensure files exist in `wheels/`.
- Improve error reporting: raise clear exceptions in `app.py`; ensure `main.js` logs the error object (not just message).

Security & privacy
- Files are processed client-side in the browser (no server upload by default).
- Remote wheel URLs should be pinned and trusted.

Maintainer questions
- Do you want `init_packages()` to install from local `wheels/` instead of remote URLs?
- Are large IFC files expected (if yes, add streaming/progress and memory handling)?

Contact
- Maintainer shown in UI: vy.dobranov@yandex.ru

