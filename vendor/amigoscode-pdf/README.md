# amigoscode-pdf (bundled)

The Amigoscode print-style PDF builder, bundled so `/resume:analyse` can render the review report
without the `amigoscode-pdf` skill installed. When the skill is installed at
`~/.claude/skills/amigoscode-pdf`, `scripts/make_report.py` uses that copy instead.

- `scripts/build_pdf.py`: wraps a body HTML fragment in the cover and stylesheet, runs the guard rails
  (no em/en dashes, no emoji, palette only) and renders with WeasyPrint.
- `references/components.md`: the body blocks the stylesheet supports.
- `assets/amigoscode-logo.svg`: the cover logo.
