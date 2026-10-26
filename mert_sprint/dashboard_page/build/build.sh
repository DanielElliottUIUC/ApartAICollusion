#!/usr/bin/env bash
# Rebuild the standalone HTML from the Page source.
# Needs Node 20. Run from this folder.
set -euo pipefail
cd "$(dirname "$0")"
[ -d node_modules ] || npm i --no-save react@18 react-dom@18 esbuild@0.23
cp ../daniel_experiment_explained.canvas.tsx page.tsx
./node_modules/.bin/esbuild entry.tsx --bundle --minify --format=iife --jsx=automatic \
  --alias:grok/canvas=./grok-canvas-shim.tsx --define:process.env.NODE_ENV=\"production\" --outfile=bundle.js
python3 - <<'PY'
js = open("bundle.js").read().replace("</script", "<\\/script")
head = ('<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        "<title>Daniel's experiment, explained visually</title>\n"
        "<style>body{margin:0;background:#fff}</style></head>\n<body><div id=\"root\"></div><script>")
open("../daniel_experiment_explained.html", "w").write(head + js + "</script></body></html>\n")
PY
rm -f page.tsx bundle.js
echo "wrote ../daniel_experiment_explained.html"
