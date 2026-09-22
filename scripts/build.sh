#!/usr/bin/env bash
# Build a resume .tex into a PDF, report page count and any text running past the margin.
# Usage: scripts/build.sh path/to/Resume.tex [--open]
set -euo pipefail

tex="${1:?usage: build.sh file.tex [--open]}"
dir="$(cd "$(dirname "$tex")" && pwd)"
base="$(basename "$tex" .tex)"
pdf="$dir/$base.pdf"

cd "$dir"

if command -v tectonic >/dev/null 2>&1; then
  tectonic --keep-logs "$base.tex" 2>&1 | grep -iE "^error|error:" || true
elif command -v pdflatex >/dev/null 2>&1; then
  pdflatex -interaction=nonstopmode "$base.tex" >/dev/null || true
else
  echo "No LaTeX compiler found. Install one (fast, ~20 MB):  brew install tectonic" >&2
  exit 1
fi

if [ ! -f "$pdf" ]; then
  echo "Build failed: no PDF produced. See $base.log" >&2
  exit 1
fi

pages="$(pdfinfo "$pdf" 2>/dev/null | awk '/^Pages:/ {print $2}')"
echo "Built: $pdf"
echo "Pages: ${pages:-unknown}"

# Overfull hboxes > 1pt usually mean a role/company/date line or skills line is too long for one row.
if [ -f "$base.log" ]; then
  overfull="$(grep -E "^Overfull \\\\hbox \(([1-9][0-9]*\.?[0-9]*)pt too wide" "$base.log" || true)"
  if [ -n "$overfull" ]; then
    echo "Warning: text runs past the right margin:"
    echo "$overfull" | sed 's/^/  /'
  fi
fi

rm -f "$base.aux" "$base.log" "$base.out"

if [ "${2:-}" = "--open" ] && command -v open >/dev/null 2>&1; then
  open "$pdf"
fi
