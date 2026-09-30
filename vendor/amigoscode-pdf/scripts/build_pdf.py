#!/usr/bin/env python3
"""Build a branded Amigoscode PDF to the print guideline.

Usage:
    build_pdf.py --body body.html --title "CV Audit" \
        --subtitle "One sentence under the title on the cover." \
        --footer "CV Audit, Jane Doe" --out /path/to/cv-audit.pdf

The body is an HTML fragment (h1/h2/h3, p, table, pre, .callout, ...).
See references/components.md for every supported block. The script wraps it
in the cover page and stylesheet, runs the guard rails, writes <out>.html
next to the PDF and renders the PDF with WeasyPrint.
"""
import argparse
import base64
import html
import pathlib
import re
import shutil
import subprocess
import sys

SKILL_DIR = pathlib.Path(__file__).resolve().parent.parent
LOGO_PATH = SKILL_DIR / "assets" / "amigoscode-logo.svg"
WEASYPRINT_FALLBACK = pathlib.Path.home() / ".local" / "bin" / "weasyprint"

# --------------------------------------------------- dash strip (guideline rule)
DASHES = {
    "—": ",",  # em dash
    "–": ",",  # en dash
    "‒": ",",  # figure dash
    "―": ",",  # horizontal bar
    "−": "-",  # minus sign
}

PALETTE = {
    "#7F56D9",  # purple, accent
    "#181D2F",  # navy, headings and strong
    "#667085",  # grey, secondary text
    "#344054",  # body text
    "#F9FAFB",  # table header and code background
    "#EAECF0",  # borders
    "#FFFFFF",
    "#F9F5FF",  # callout background
}

FONT = 'Inter, "Helvetica Neue", Arial, sans-serif'


def strip_dashes(text: str) -> str:
    for bad, good in DASHES.items():
        text = text.replace(bad, good)
    return text


def css_string(text: str) -> str:
    return text.replace("\\", "\\\\").replace('"', '\\"')


STYLE = """
  @page {
    size: A4;
    margin: 18mm 20mm 22mm 20mm;
    @bottom-left {
      content: "%(footer)s";
      font-family: %(font)s;
      font-size: 11px; color: #667085; vertical-align: top; padding-top: 8mm;
    }
    @bottom-right {
      content: counter(page);
      font-family: %(font)s;
      font-size: 11px; color: #667085; vertical-align: top; padding-top: 8mm;
    }
  }
  @page cover {
    @bottom-left {
      content: "amigoscode.com";
      font-family: %(font)s;
      font-size: 13px; color: #667085; vertical-align: top; padding-top: 8mm;
    }
    @bottom-right {
      content: "01";
      font-family: %(font)s;
      font-size: 13px; color: #7F56D9; vertical-align: top; padding-top: 8mm;
    }
  }

  html {
    font-family: %(font)s;
    font-size: 11pt;
    line-height: 1.6;
    color: #344054;
  }
  body { margin: 0; }

  /* ---------------------------------------------------------- cover */
  .cover { page: cover; position: relative; height: 257mm; page-break-after: always; }
  .cover-logo { position: absolute; top: 0; left: 0; }
  .cover-logo img { height: 40px; }
  .cover-block { position: absolute; left: 0; right: 0; bottom: 8mm; }
  .cover-rule { width: 80px; height: 4px; background: #7F56D9; margin-bottom: 28px; }
  .cover h1 {
    font-size: 52px; line-height: 1.1; font-weight: 700; color: #181D2F;
    margin: 0; letter-spacing: -0.015em;
  }
  .cover .sub {
    font-size: 21px; line-height: 1.45; font-weight: 400; color: #667085;
    margin: 16px 0 0 0; max-width: 118mm;
  }

  /* ------------------------------------------------------ headings */
  h1 {
    font-size: 28px; line-height: 1.25; color: #181D2F; font-weight: 700;
    margin: 34px 0 14px 0; letter-spacing: -0.01em;
  }
  h2 { font-size: 22px; line-height: 1.3; color: #181D2F; font-weight: 600; margin: 26px 0 10px 0; }
  h3 { font-size: 17px; line-height: 1.35; color: #7F56D9; font-weight: 600; margin: 22px 0 8px 0; }
  h1, h2, h3 { page-break-after: avoid; }
  h1:first-of-type { margin-top: 0; }
  h1.fresh { page-break-before: always; margin-top: 0; }

  p { margin: 0 0 11px 0; }
  strong { color: #181D2F; font-weight: 600; }
  a { color: #7F56D9; text-decoration: none; }
  ul, ol { margin: 0 0 14px 0; padding-left: 20px; }
  li { margin-bottom: 5px; }

  .meta { font-size: 10pt; color: #667085; margin: 0 0 7px 0; }

  /* --------------------------------------------------- code blocks */
  pre {
    background: #F9FAFB; border: 1px solid #EAECF0; border-radius: 6px;
    padding: 12px 14px; margin: 0 0 14px 0;
    font-family: Menlo, "SF Mono", Consolas, monospace;
    font-size: 10pt; line-height: 1.5; color: #344054;
    white-space: pre-wrap; word-wrap: break-word;
  }
  code { font-family: Menlo, "SF Mono", Consolas, monospace; font-size: 0.92em; }

  /* ------------------------------------------------------ callouts */
  .callout {
    border-left: 3px solid #7F56D9; background: #F9F5FF;
    padding: 12px; margin: 0 0 16px 0; page-break-inside: avoid;
  }
  .callout p:last-child { margin-bottom: 0; }

  /* -------------------------------------------------------- tables */
  table { width: 100%%; border-collapse: collapse; margin: 0 0 16px 0; font-size: 10pt; }
  thead { display: table-header-group; }
  th {
    background: #F9FAFB; border: 1px solid #EAECF0; text-align: left;
    font-weight: 600; color: #181D2F; padding: 8px 10px;
  }
  td { border: 1px solid #EAECF0; padding: 8px 10px; vertical-align: top; }
  tr { page-break-inside: avoid; }
  td.num, th.num { width: 34px; text-align: center; color: #667085; }
  td.pass { color: #7F56D9; font-weight: 600; }
  td.warn, td.fail { color: #181D2F; font-weight: 600; }
  td.box { width: 40px; text-align: center; }
  table.checklist td { padding: 6px 10px; }
  td.box::before {
    content: ""; display: inline-block; width: 11px; height: 11px;
    border: 1px solid #667085; border-radius: 2px;
  }

  /* --------------------------------------------------------- lists */
  ol.priority { padding-left: 20px; margin: 0 0 16px 0; }
  ol.priority li { margin-bottom: 7px; padding-left: 4px; }

  .pinned { font-size: 13pt; color: #181D2F; font-weight: 600; }
  .skills p { margin-bottom: 9px; }
"""


def build_html(body: str, title: str, subtitle: str, footer: str) -> str:
    logo_b64 = base64.b64encode(LOGO_PATH.read_bytes()).decode()
    style = STYLE % {"footer": css_string(footer), "font": FONT}
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{html.escape(title)}</title>
<style>{style}</style>
</head>
<body>

<section class="cover">
  <div class="cover-logo">
    <img src="data:image/svg+xml;base64,{logo_b64}" alt="Amigoscode">
  </div>
  <div class="cover-block">
    <div class="cover-rule"></div>
    <h1>{html.escape(title)}</h1>
    <p class="sub">{html.escape(subtitle)}</p>
  </div>
</section>

{body}

</body>
</html>
"""


def guard_rails(doc: str) -> list[str]:
    errors = []
    leftover = [d for d in DASHES if d in doc]
    if leftover:
        errors.append(f"dash characters still present: {leftover}")
    emoji = re.findall(r"[\U0001F000-\U0001FAFF☀-➿️]", doc)
    if emoji:
        errors.append(f"emoji present: {sorted(set(emoji))}")
    # Palette applies to the stylesheet and any inline style attributes.
    css = doc.split("</style>")[0].split("<style>")[-1]
    css += " ".join(re.findall(r'style="([^"]*)"', doc))
    used = {c.upper() for c in re.findall(r"#[0-9A-Fa-f]{6}\b", css)}
    off = sorted(used - PALETTE)
    if off:
        errors.append(f"off palette colours: {off}")
    return errors


def find_weasyprint() -> str:
    found = shutil.which("weasyprint")
    if found:
        return found
    if WEASYPRINT_FALLBACK.exists():
        return str(WEASYPRINT_FALLBACK)
    sys.exit("FAIL: weasyprint not found. Install with: pipx install weasyprint")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--body", required=True, help="HTML fragment file for the document body")
    ap.add_argument("--title", required=True, help="Cover title and PDF metadata title")
    ap.add_argument("--subtitle", required=True, help="One sentence under the cover title")
    ap.add_argument("--footer", help="Running footer on inner pages (default: the title)")
    ap.add_argument("--out", required=True, help="Output PDF path")
    ap.add_argument("--html-only", action="store_true", help="Write the HTML, skip the PDF render")
    args = ap.parse_args()

    body = strip_dashes(pathlib.Path(args.body).read_text())
    title = strip_dashes(args.title)
    subtitle = strip_dashes(args.subtitle)
    footer = strip_dashes(args.footer or args.title)

    doc = build_html(body, title, subtitle, footer)
    errors = guard_rails(doc)
    if errors:
        sys.exit("FAIL: " + "; ".join(errors))

    out_pdf = pathlib.Path(args.out).expanduser().resolve()
    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    out_html = out_pdf.with_suffix(".html")
    out_html.write_text(doc)
    print(f"wrote {out_html} ({len(doc):,} bytes)")
    print("checks passed: no en/em dashes, no emoji, palette clean")

    if args.html_only:
        return
    subprocess.run([find_weasyprint(), str(out_html), str(out_pdf)], check=True)
    print(f"wrote {out_pdf}")


if __name__ == "__main__":
    main()
