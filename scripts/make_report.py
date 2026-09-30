#!/usr/bin/env python3
"""Build the CV review PDF from review.json with the amigoscode-pdf house style.

    python3 make_report.py review.json [--out Jane_Doe_CV_Review.pdf] [--html-only]

Writes the report body as an amigoscode-pdf HTML fragment (<out>-body.html),
then hands it to amigoscode-pdf's build_pdf.py, which adds the cover, the
stylesheet and the guard rails (no dashes, no emoji, palette only) and renders
with WeasyPrint. Uses the installed skill at ~/.claude/skills/amigoscode-pdf
when present, otherwise the copy bundled in vendor/amigoscode-pdf.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUBRICS = ROOT / "rubrics"
BUILDERS = [
    Path(os.environ["AMIGOSCODE_PDF"]) if os.environ.get("AMIGOSCODE_PDF") else None,
    Path.home() / ".claude" / "skills" / "amigoscode-pdf" / "scripts" / "build_pdf.py",
    ROOT / "vendor" / "amigoscode-pdf" / "scripts" / "build_pdf.py",
]

PLAN_LABELS = {
    "xyz": "XYZ rewrite",
    "strong": "Strong, no metric",
    "keep": "Keep as is",
    "merge": "Merge",
    "cut": "Cut",
}
STATUS = {"pass": ("pass", "Pass"), "partial": ("warn", "Needs work"), "fail": ("fail", "Fail")}


def e(s) -> str:
    """Escape, and write dashes the way the print guideline wants them."""
    s = str(s if s is not None else "")
    s = re.sub(r"(\d)\s*[–—]\s*(\d)", r"\1 to \2", s)
    s = re.sub(r"\s*[–—]\s*", ", ", s)
    return escape(s)


def nobreak(s) -> str:
    """Keep ids like e1-b2 and commands like /resume:improve on one line."""
    return e(s).replace("-", "\u2011").replace("/", "/\u2060").replace(":", ":\u2060")


def num(x):
    x = float(x)
    return int(x) if x.is_integer() else round(x, 1)


def verdict(score) -> str:
    """td class for a 0 to 10 score: pass at 7 and above, warn at 5 to 6, fail below."""
    if score is None:
        return ""
    return "pass" if score >= 7 else "warn" if score >= 5 else "fail"


def span(start, end) -> str:
    return " to ".join(e(x) for x in (start, end) if x)


def band_for(pct: float) -> str:
    if pct >= 0.85:
        return "Strong match for the role"
    if pct >= 0.70:
        return "Solid match, with a few gaps to close"
    if pct >= 0.50:
        return "Promising profile, not yet at the bar"
    if pct >= 0.30:
        return "Early for this level"
    return "Not a fit for this role as presented"


def load_rubric(target: dict) -> dict:
    if target.get("rubric") == "custom" or not target.get("rubric"):
        return target.get("custom_rubric") or {"position_title": target.get("position_title", "the target role"), "categories": []}
    return json.loads((RUBRICS / target["rubric"] / "role.json").read_text())


def role_fit(r: dict, rubric: dict) -> dict:
    ev = r.get("role_evaluation") or {}
    cats = []
    for c in rubric.get("categories", []):
        s = ev.get("scores", {}).get(c["key"], {})
        score = float(s.get("score", 0))
        pct = score / c["max"] if c["max"] else 0
        cats.append({"label": c["label"], "max": c["max"], "score": num(score), "pct": pct,
                     "evidence": s.get("evidence", "")})
    bonus = float(ev.get("bonus_points", {}).get("total", 0))
    ded = float(ev.get("deductions", {}).get("total", 0))
    raw = sum(float(c["score"]) for c in cats)
    ceiling = sum(c["max"] for c in cats) or 100
    total = max(0.0, min(100.0, raw + bonus - ded))
    return {"cats": cats, "bonus": num(bonus), "ded": num(ded), "total": num(total),
            "headline": band_for(raw / ceiling), "ev": ev}


def verdict_rows(items, name_key: str) -> str:
    rows = []
    for i, c in enumerate(items, 1):
        cls, word = STATUS.get(c.get("status"), ("", e(c.get("status"))))
        rows.append(f'<tr><td class="num">{i}</td><td>{e(c.get(name_key))}</td><td class="{cls}">{word}</td><td>{e(c.get("note"))}</td></tr>')
    return ('<table><thead><tr><th class="num">#</th><th>Check</th><th>Verdict</th><th>Note</th></tr></thead><tbody>'
            + "".join(rows) + "</tbody></table>")


def build_body(r: dict) -> tuple[str, dict]:
    rubric = load_rubric(r.get("target", {}))
    fit = role_fit(r, rubric)
    name = r["basics"]["name"]
    position = rubric.get("position_title", "the target role")

    bullets = [b for role in r.get("experience", []) for b in role.get("bullets", [])]
    scored = [b["score"] for b in bullets if b.get("score") is not None]
    avg = round(sum(scored) / len(scored), 1) if scored else 0
    at7 = sum(1 for s in scored if s >= 7)
    plans = {k: sum(1 for b in bullets if b.get("plan") == k) for k in PLAN_LABELS}
    kept = plans["xyz"] + plans["strong"] + plans["keep"]
    xyz_share = round(100 * plans["xyz"] / kept) if kept else 0

    summ = r.get("summary") or {}
    summary_off = summ.get("include") is False
    edu = r.get("education", [])
    edu_scores = [x["score"] for x in edu if x.get("score") is not None]
    edu_avg = round(sum(edu_scores) / len(edu_scores), 1) if edu_scores else None
    checks = r.get("format_checks", [])
    passed = sum(1 for c in checks if c.get("status") == "pass")
    skills_rev = r.get("skills_review") or {}
    custom = r.get("target", {}).get("rubric") == "custom"

    out = []

    # 1. Where it stands
    out.append("<h1>1. Where it stands</h1>")
    out.append(f'<p class="meta">Reviewed on {e(r.get("analysed_on", ""))} against the {e(position)} rubric'
               f'{", a custom rubric written for this role" if custom else ""}.</p>')
    out.append(f'<div class="callout"><p><strong>{e(fit["headline"])}.</strong> '
               f'{e(name.split()[0])}\'s CV scores <strong>{fit["total"]} out of 100</strong> for the role. '
               f'The experience bullets average <strong>{avg} out of 10</strong>, with {at7} of {len(scored)} already at 7 or above.</p></div>')
    metrics = [
        ("Role fit", f"{fit['total']} / 100", fit["headline"] + "."),
        ("Experience bullets", f"{avg} / 10 average", f"{at7} of {len(scored)} at 7 or above. Target is 7 or above for every kept bullet."),
        ("Summary", "Left off" if summary_off else f"{summ.get('score', 'n/a')} / 10",
         "Not included on the resume, by choice." if summary_off else "Optional. Written last, after bullets and skills."),
        ("Skills", f"{skills_rev.get('score', 'n/a')} / 10", "Tailored to job descriptions after the bullets."),
        ("Education", f"{edu_avg if edu_avg is not None else 'n/a'} / 10", ""),
        ("Format", f"{passed} of {len(checks)} checks pass", "Page limit is 2."),
        ("Planned bullet mix", f"{plans['xyz']} XYZ, {plans['strong']} strong, {plans['keep']} keep",
         f"{plans['merge']} merge, {plans['cut']} cut. {xyz_share}% of kept bullets get a metric."),
    ]
    out.append('<table><thead><tr><th>Area</th><th>Score</th><th>Read</th></tr></thead><tbody>'
               + "".join(f"<tr><td>{e(a)}</td><td>{e(b)}</td><td>{e(c)}</td></tr>" for a, b, c in metrics)
               + "</tbody></table>")
    out.append("<h3>Top fixes, in order</h3>")
    out.append('<ol class="priority">' + "".join(f"<li>{e(f)}</li>" for f in r.get("top_fixes", [])) + "</ol>")

    n = 2
    # 2. Role fit
    if fit["cats"]:
        ev = fit["ev"]
        out.append(f'<h1 class="fresh">{n}. How a hiring rubric reads it</h1>')
        out.append(f"<p>Scored against the {e(position)} rubric, the same shape an automated screen or a hiring manager uses. "
                   "Only what the resume shows counts.</p>")
        rows = "".join(
            f'<tr><td>{e(c["label"])}</td><td class="{"pass" if c["pct"] >= 0.7 else "warn" if c["pct"] >= 0.5 else "fail"}">'
            f'{c["score"]} / {c["max"]}</td><td>{e(c["evidence"])}</td></tr>' for c in fit["cats"])
        rows += f'<tr><td>Bonus</td><td>+{fit["bonus"]}</td><td>{e(ev.get("bonus_points", {}).get("breakdown", ""))}</td></tr>'
        rows += f'<tr><td>Deductions</td><td>{"-" if fit["ded"] else ""}{fit["ded"]}</td><td>{e(ev.get("deductions", {}).get("reasons", ""))}</td></tr>'
        rows += f'<tr><td><strong>Total</strong></td><td><strong>{fit["total"]} / 100</strong></td><td></td></tr>'
        out.append('<table><thead><tr><th>Category</th><th>Score</th><th>Evidence</th></tr></thead><tbody>' + rows + "</tbody></table>")
        out.append("<h3>Key strengths</h3><ul>" + "".join(f"<li>{e(s)}</li>" for s in ev.get("key_strengths", [])) + "</ul>")
        out.append('<h3>Where to level up</h3><ol class="priority">'
                   + "".join(f"<li>{e(s)}</li>" for s in ev.get("areas_for_improvement", [])) + "</ol>")
        n += 1

    # Experience
    out.append(f'<h1 class="fresh">{n}. Experience bullets</h1>')
    out.append('<div class="callout"><p><strong>How bullets are scored.</strong> Each bullet is scored 0 to 10 on Google\'s XYZ idea: '
               "accomplished X, measured by Y, by doing Z. Not every bullet should be XYZ. About a third get a real number; "
               "the rest get their strength from scope, ownership, specific tech and outcomes in words. "
               f"This plan has <strong>{xyz_share}% XYZ</strong>"
               + (", which is too high, so move a few to strong." if xyz_share > 50 else ", which is a good balance.")
               + "</p></div>")
    out.append("<p>Answer the questions under each bullet in <strong>/resume:improve</strong>. Rough answers are fine, "
               "and \"don't know\" is a fine answer. No number is ever invented.</p>")
    for role in r.get("experience", []):
        out.append(f"<h2>{e(role['role'])}, {e(role['company'])}</h2>")
        rows = []
        for b in role.get("bullets", []):
            plan = PLAN_LABELS.get(b.get("plan"), "")
            if b.get("plan") == "merge" and b.get("merge_into"):
                plan = f"Merge into {b['merge_into']}"
            qs = "".join(f"<li>{e(q)}</li>" for q in b.get("questions", []))
            cell = f"<strong>{e(b['text'])}</strong><br>{e(b.get('reason'))}" + (f"<ol>{qs}</ol>" if qs else "")
            rows.append(f'<tr><td>{nobreak(b.get("id"))}</td><td>{cell}</td><td class="{verdict(b.get("score"))}">{e(b.get("score"))}</td><td>{e(plan)}</td></tr>')
        # Dates live in the table header, so the heading can't be left alone at the foot of a page.
        when = f'{span(role.get("start"), role.get("end"))} | {e(role.get("location"))}'
        out.append(f'<table><thead><tr><th colspan="4">{when}</th></tr>'
                   '<tr><th>ID</th><th>Bullet, why, and questions</th><th>Score</th><th>Plan</th></tr></thead><tbody>'
                   + "".join(rows) + "</tbody></table>")
    n += 1

    # Summary
    out.append(f'<h1 class="fresh">{n}. Professional summary</h1>')
    if summary_off:
        out.append("<p>You chose to leave the summary off the resume. The review below is for reference only.</p>")
    else:
        out.append("<p>A summary is optional, and you will be asked whether you want one. If you do, it is written last in "
                   "<strong>/resume:summary</strong>, after the bullets and skills, so it describes the finished resume.</p>")
    if summ.get("text"):
        out.append(f"<h3>Current summary, {e(summ.get('score'))} / 10</h3><pre>{e(summ['text'])}</pre>")
    if summ.get("criteria"):
        out.append(verdict_rows(summ["criteria"], "name"))
    if summ.get("questions") and not summary_off:
        out.append('<h3>Questions for later</h3><ol class="priority">' + "".join(f"<li>{e(q)}</li>" for q in summ["questions"]) + "</ol>")
    n += 1

    # Skills and education
    out.append(f"<h1>{n}. Skills and education</h1>")
    out.append(f"<h2>Skills, {e(skills_rev.get('score', 'n/a'))} / 10</h2>")
    if r.get("skills"):
        out.append('<div class="skills">' + "".join(
            f"<p><strong>{e(g['label'])}:</strong> {e(', '.join(g['items']))}</p>" for g in r["skills"]) + "</div>")
    if skills_rev.get("notes"):
        out.append("<ul>" + "".join(f"<li>{e(x)}</li>" for x in skills_rev["notes"]) + "</ul>")
    out.append("<p>Skills are tailored after the bullets, in <strong>/resume:skills</strong>, against a job description you paste "
               "or current postings for your target role.</p>")
    out.append(f"<h2>Education, {e(edu_avg if edu_avg is not None else 'n/a')} / 10</h2>")
    for x in edu:
        out.append(f"<p><strong>{e(x['degree'])}</strong>, {e(x['school'])}</p>"
                   f'<p class="meta">{span(x.get("start"), x.get("end"))} | {e(x.get("location"))}</p>')
        if x.get("notes"):
            out.append("<ul>" + "".join(f"<li>{e(t)}</li>" for t in x["notes"]) + "</ul>")
        if x.get("questions"):
            out.append('<ol class="priority">' + "".join(f"<li>{e(q)}</li>" for q in x["questions"]) + "</ol>")
    n += 1

    # Format
    if checks:
        out.append(f"<h1>{n}. Format checks</h1>")
        out.append(verdict_rows(checks, "check"))
        n += 1

    # Next steps
    steps = [
        ("Answer the bullet questions, one bullet at a time", "/resume:improve"),
        ("Tailor the skills to a job description or the market, once the bullets are done", "/resume:skills"),
        ("Decide on a summary and write it last, once the skills are done", "/resume:summary"),
        ("Build the final LaTeX resume and PDF, 2 pages max", "/resume:build"),
    ]
    out.append(f'<h1 class="fresh">{n}. Next steps</h1>')
    out.append('<table class="checklist"><thead><tr><th class="box"></th><th>Task</th><th>Command</th></tr></thead><tbody>'
               + "".join(f'<tr><td class="box"></td><td>{e(t)}</td><td><code>{nobreak(c)}</code></td></tr>' for t, c in steps)
               + "</tbody></table>")
    out.append('<p class="meta">Method. Role fit uses a rubric adapted from HackerRank\'s open source hiring-agent, with '
               "level specific rubrics written by Amigoscode. Bullets and summary are scored against the Amigoscode resume rubric. "
               "Scores are directional: a re-run can move them by a point or two. Name, gender, age, nationality, school prestige, "
               "grades and location are ignored; only what was built, owned and shipped counts.</p>")

    meta = {"title": "CV Review",
            "subtitle": f"A full review of {name}'s CV against the {position.replace(' position', '')} role.",
            "footer": f"CV Review, {name}"}
    return "\n".join(out), meta


def find_builder() -> Path:
    for b in BUILDERS:
        if b and b.exists():
            return b
    sys.exit("amigoscode-pdf build_pdf.py not found (expected ~/.claude/skills/amigoscode-pdf or vendor/amigoscode-pdf).")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("review", type=Path)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--html-only", action="store_true", help="write the HTML, skip the PDF render")
    args = ap.parse_args()

    r = json.loads(args.review.read_text())
    stem = "_".join(r["basics"]["name"].split()) + "_CV_Review"
    pdf = (args.out or args.review.parent / f"{stem}.pdf").resolve()
    body_path = pdf.with_name(pdf.stem + "-body.html")
    body, meta = build_body(r)
    body_path.write_text(body)

    builder = find_builder()
    cmd = [sys.executable, str(builder), "--body", str(body_path), "--title", meta["title"],
           "--subtitle", meta["subtitle"], "--footer", meta["footer"], "--out", str(pdf)]
    if args.html_only:
        cmd.append("--html-only")
    print(f"using {builder}")
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
