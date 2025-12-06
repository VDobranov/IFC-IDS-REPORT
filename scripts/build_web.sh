#!/usr/bin/env bash
set -euo pipefail

# Build script for producing a `dist/` folder.
# Behavior:
# - If `flet` CLI is available, run `flet publish main.py --route-url-strategy hash --base-url <repo>`
#   which typically produces a `dist/` directory ready for GitHub Pages upload.

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DIST_DIR="$ROOT_DIR/dist"

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
rm -rf "$DIST_DIR"

# Try to publish with flet (preferred). The CLI command used here follows
# the repository guidance: `flet publish main.py --route-url-strategy hash --base-url {repo}`
if command -v flet >/dev/null 2>&1; then
  echo "Found flet CLI — running publish to produce ./dist/"
  set -x
  flet publish main.py --route-url-strategy hash --base-url "$REPO_NAME" || true
  set +x
fi

if [ -d "$DIST_DIR" ] && [ "$(ls -A "$DIST_DIR")" ]; then
  cp "$ROOT_DIR/odfpy-1.4.2-py2.py3-none-any.whl" "$DIST_DIR"
  echo "Found built assets in $DIST_DIR"
  echo "Done. The Pages workflow should upload './dist/'"
  exit 0
fi