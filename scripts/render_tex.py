#!/usr/bin/env python3
"""Render a review.json into a LaTeX resume (2 pages max) on the bundled template.

    python3 render_tex.py review.json Out_Resume.tex [--scores]

All text in review.json is plain text; this script does the LaTeX escaping.
For each bullet it uses `rewrite` when present, otherwise `text`, and skips
bullets whose `plan` is "cut" (or "merge", since the merged text lives on the
bullet it was merged into). --scores prefixes every bullet with "[N] -- "
(new_score when rewritten, else score) for a review copy.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "assets" / "template.tex"

_SPECIALS = {
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}


def esc(s: str) -> str:
    s = "".join(_SPECIALS.get(ch, ch) for ch in str(s))
    return re.sub(r"\s+-\s+", " -- ", s)  # spaced hyphen reads as an en dash


def dates(start: str, end: str) -> str:
    return " -- ".join(esc(x) for x in (start, end) if x)


def bullet_text(b: dict, scores: bool) -> str | None:
    if b.get("plan") in ("cut", "merge"):
        return None
    text = b.get("rewrite") or b["text"]
    out = esc(text)
    if scores:
        n = b.get("new_score") if b.get("rewrite") else b.get("score")
        if n is not None:
            out = f"[{n}] -- {out}"
    return out


def header(basics: dict) -> str:
    parts = [esc(x) for x in (basics.get("location"), basics.get("phone")) if x]
    if basics.get("email"):
        e = basics["email"]
        parts.append(rf"\href{{mailto:{e}}}{{\underline{{{esc(e)}}}}}")
    for link in basics.get("links", []):
        url = link["url"] if "://" in link["url"] else "https://" + link["url"]
        label = link.get("label") or re.sub(r"^https?://(www\.)?", "", link["url"]).rstrip("/")
        parts.append(rf"\href{{{url}}}{{\underline{{{esc(label)}}}}}")
    return (
        "\\begin{center}\n"
        f"    \\textbf{{\\Huge \\scshape {esc(basics['name'])}}} \\\\ \\vspace{{1pt}}\n"
        f"    \\small {' $|$ '.join(parts)}\n"
        "\\end{center}\n"
    )


def paragraph_section(title: str, text: str) -> str:
    return (
        f"\\section{{{title}}}\n"
        " \\begin{itemize}[leftmargin=0.15in, label={}]\n"
        f"    \\small{{\\item{{\n     {esc(text)}\n    }}}}\n"
        " \\end{itemize}\n"
    )


def experience(roles: list, scores: bool) -> str:
    out = ["\\section{Experience}", "  \\resumeSubHeadingListStart"]
    for r in roles:
        out.append(
            "    \\resumeSubheading\n"
            f"      {{{esc(r['role'])}}}{{{dates(r.get('start', ''), r.get('end', ''))}}}\n"
            f"      {{{esc(r['company'])}}}{{{esc(r.get('location', ''))}}}"
        )
        items = [t for t in (bullet_text(b, scores) for b in r.get("bullets", [])) if t]
        if items:
            out.append("      \\resumeItemListStart")
            out += [f"        \\resumeItem{{{t}}}" for t in items]
            out.append("      \\resumeItemListEnd")
        out.append("")
    out.append("  \\resumeSubHeadingListEnd")
    return "\n".join(out) + "\n"


def skills(groups: list) -> str:
    lines = [f"     \\textbf{{{esc(g['label'])}}}{{: {esc(', '.join(g['items']))}}}" for g in groups]
    return (
        "\\section{Skills}\n"
        " \\begin{itemize}[leftmargin=0.15in, label={}]\n"
        "    \\small{\\item{\n" + " \\\\\n".join(lines) + "\n    }}\n"
        " \\end{itemize}\n"
    )


_DEGREES = [
    (r"bachelor(?:'?s)? of science|b\.?\s?sc\.?|b\.s\.?", "BSc"),
    (r"bachelor(?:'?s)? of arts|b\.a\.?", "BA"),
    (r"bachelor(?:'?s)? of engineering|b\.?\s?eng\.?", "BEng"),
    (r"bachelor(?:'?s)? of technology|b\.?\s?tech\.?", "BTech"),
    (r"master(?:'?s)? of science|m\.?\s?sc\.?|m\.s\.?", "MSc"),
    (r"master(?:'?s)? of arts|m\.a\.?", "MA"),
    (r"master(?:'?s)? of engineering|m\.?\s?eng\.?", "MEng"),
    (r"master(?:'?s)? of technology|m\.?\s?tech\.?", "MTech"),
    (r"master(?:'?s)? of business administration|m\.b\.a\.?", "MBA"),
    (r"doctor of philosophy|ph\.?\s?d\.?", "PhD"),
]


def short_degree(s: str) -> str:
    """'Bachelor of Science in Computer Science (Honours)' -> 'BSc (Hons) Computer Science'."""
    s = s.strip()
    hons = bool(re.search(r"\(?\b(?:with\s+)?hon(?:ou?r)?s\b\.?\)?", s, re.I))
    for pat, short in _DEGREES:
        m = re.match(rf"(?:{pat})(?=[\s,(]|$)", s, re.I)
        if m:
            rest = s[m.end():]
            if hons:
                rest = re.sub(r"\(?\b(?:with\s+)?hon(?:ou?r)?s\b\.?\)?", "", rest, flags=re.I)
            rest = re.sub(r"^[\s,]*(?:degree\s+)?(?:in|of)\s+", " ", rest, flags=re.I)
            rest = re.sub(r"\s+", " ", rest).strip(" ,")
            return f"{short}{' (Hons)' if hons else ''}{' ' + rest if rest else ''}"
    return s


def education(items: list) -> str:
    out = ["\\section{Education}", "  \\resumeSubHeadingListStart"]
    for e in items:
        degree = short_degree(e.get("rewrite") or e["degree"])
        loc = f", {esc(e['location'])}" if e.get("location") else ""
        out.append(
            "    \\resumeEducation\n"
            f"      {{{esc(e['school'])}}}{{{loc}}}{{{dates(e.get('start', ''), e.get('end', ''))}}}\n"
            f"      {{{esc(degree)}}}{{{esc(e.get('grade') or '')}}}"
        )
    out.append("  \\resumeSubHeadingListEnd")
    return "\n".join(out) + "\n"


def extra(sec: dict) -> str:
    return paragraph_section(esc(sec["title"]), " | ".join(sec["items"]))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("review", type=Path)
    ap.add_argument("out", type=Path)
    ap.add_argument("--scores", action="store_true", help="prefix bullets with their [N] score")
    args = ap.parse_args()

    r = json.loads(args.review.read_text())
    tpl = TEMPLATE.read_text()
    preamble = tpl[: tpl.index("\\begin{document}")]

    body = ["\\begin{document}\n", "%----------HEADING----------", header(r["basics"])]
    summary = r.get("summary") or {}
    if summary.get("include") is not False and summary.get("plan") != "cut" and (summary.get("rewrite") or summary.get("text")):
        body += ["%-----------SUMMARY-----------", paragraph_section("Summary", summary.get("rewrite") or summary["text"])]
    body += ["%-----------EXPERIENCE-----------", experience(r.get("experience", []), args.scores)]
    if r.get("skills"):
        body += ["%-----------SKILLS-----------", skills(r["skills"])]
    for sec in r.get("extra_sections", []):
        body += [extra(sec)]
    if r.get("education"):
        body += ["%-----------EDUCATION-----------", education(r["education"])]
    body.append("\\end{document}\n")

    args.out.write_text(preamble + "\n".join(body))
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
