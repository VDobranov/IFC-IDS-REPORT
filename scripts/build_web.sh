#!/usr/bin/env bash
set -euo pipefail

# Build script for producing a docs/ folder to publish to GitHub Pages.
# Assumptions:
# - You want the Flet app accessible over the web. Flet does not currently
#   produce a single static bundle like typical JS frameworks; depending on
#   your Flet version you may run it as a web server and proxy it, or use
#   Flet's web deployment tools if available. This script provides a minimal
#   approach to package static assets and a small index that forwards to a
#   local hosted app.
# - This script will create/overwrite the docs/ directory.

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DOCS_DIR="$ROOT_DIR/docs"

echo "Building docs/ in $DOCS_DIR"
rm -rf "$DOCS_DIR"
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
  </body>
</html>
HTML

echo "Created $DOCS_DIR/index.html"

echo "Note: For a full web deployment of a Flet app you may need to use Flet Cloud or a container-based deploy."

echo "Done. Publish the 'docs/' directory to GitHub Pages from repository settings."
