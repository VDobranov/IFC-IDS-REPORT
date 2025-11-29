#!/usr/bin/env bash
set -euo pipefail

# Build script for producing a `dist/` folder (preferred) or `docs/` as a fallback.
# Behavior:
# - If `flet` CLI is available, run `flet publish main.py --route-url-strategy hash --base-url <repo>`
#   which typically produces a `dist/` directory ready for GitHub Pages upload.
# - If `flet publish` is not available or doesn't produce `dist/`, the script
#   falls back to creating a minimal `docs/index.html` (legacy behavior).

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DIST_DIR="$ROOT_DIR/dist"
DOCS_DIR="$ROOT_DIR/docs"

echo "Building web assets in repo root: $ROOT_DIR"

# Determine repository name for base-url
# Prefer GITHUB_REPOSITORY (owner/name) when running in Actions; use repo name part.
REPO_NAME=""
if [ -n "${GITHUB_REPOSITORY-}" ]; then
  REPO_NAME="${GITHUB_REPOSITORY##*/}"
else
  # Fallback: try to read git remote URL or directory name
  if command -v git >/dev/null 2>&1; then
    REMOTE_URL=$(git config --get remote.origin.url || true)
    if [ -n "$REMOTE_URL" ]; then
      # extract repo name from URL
      REPO_NAME=$(basename -s .git "$REMOTE_URL")
    fi
  fi
  if [ -z "$REPO_NAME" ]; then
    REPO_NAME=$(basename "$ROOT_DIR")
  fi
fi

echo "Using repository name for base-url: $REPO_NAME"

# Clean previous outputs
rm -rf "$DIST_DIR" "$DOCS_DIR"

# Try to publish with flet (preferred). The CLI command used here follows
# the repository guidance: `flet publish main.py --route-url-strategy hash --base-url {repo}`
if command -v flet >/dev/null 2>&1; then
  echo "Found flet CLI — running publish to produce ./dist/"
  set -x
  flet publish main.py --route-url-strategy hash --base-url "$REPO_NAME" || true
  set +x
fi

if [ -d "$DIST_DIR" ] && [ "$(ls -A "$DIST_DIR")" ]; then
  echo "Found built assets in $DIST_DIR"
  echo "Done. The Pages workflow should upload './dist/'"
  exit 0
fi

# Fallback: produce minimal docs/ (legacy behavior)
echo "Flet publish did not produce ./dist/. Falling back to creating ./docs/index.html"
mkdir -p "$DOCS_DIR"

cat > "$DOCS_DIR/index.html" <<'HTML'
<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Flet App (GitHub Pages)</title>
  </head>
  <body>
    <h1>Flet App</h1>
    <p>This page expects the Flet app to be hosted separately as a web app.</p>
    <p>To run locally, start the Flet web server and open the app URL.</p>
    <p>To produce a full static build, install the Flet CLI and run:</p>
    <pre>flet publish main.py --route-url-strategy hash --base-url $REPO_NAME</pre>
  </body>
</html>
HTML

echo "Created $DOCS_DIR/index.html"
echo "Note: For a full web deployment of a Flet app you may need to use Flet Cloud or a container-based deploy."
echo "Done. If you produced ./dist/, the Pages workflow should upload it; otherwise it will upload ./docs/."
