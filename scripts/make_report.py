#!/usr/bin/env python3
"""Render an Amigoscode-branded CV review PDF from review.json.

    python3 make_report.py review.json [--out "Jane_Doe_CV_Review.pdf"] [--chrome PATH]

Writes <out>.html next to the PDF and prints it to A4 with headless Chrome.
No third-party Python packages needed.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import shutil
import subprocess
import sys
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPORT = ROOT / "report"
RUBRICS = ROOT / "rubrics"

CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    shutil.which("google-chrome"),
    shutil.which("google-chrome-stable"),
    shutil.which("chromium"),
    shutil.which("chromium-browser"),
]

PLAN_LABELS = {
    "xyz": ("XYZ rewrite", "xyz"),
    "strong": ("Strong, no metric", "strong"),
    "keep": ("Keep as is", "keep"),
    "merge": ("Merge", "merge"),
    "cut": ("Cut", "cut"),
}
STATUS = {"pass": ("✓", "ok"), "partial": ("!", "warn"), "fail": ("✕", "bad")}


def e(s) -> str:
    return escape(str(s if s is not None else ""))


def num(x):
    x = float(x)
    return int(x) if x.is_integer() else round(x, 1)


def tone10(score) -> str:
    if score is None:
        return ""
    return "high" if score >= 7 else "low" if score <= 4 else "mid"


def band_for(pct: float) -> tuple[str, str]:
    if pct >= 0.85:
        return "Strong match for the role", "STRONG"
    if pct >= 0.70:
        return "Solid match, a few gaps to close", "SOLID"
    if pct >= 0.50:
        return "Promising profile, not yet at the bar", "DEVELOPING"
    if pct >= 0.30:
        return "Early for this level", "EARLY"
    return "Not a fit for this role as presented", "LOW"


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
        cats.append({
            "label": c["label"], "max": c["max"], "score": num(score), "pct": round(pct * 100),
            "tone": "high" if pct >= 0.7 else "low" if pct < 0.35 else "",
            "evidence": s.get("evidence", ""), "blurb": c.get("description", ""),
        })
    bonus = float(ev.get("bonus_points", {}).get("total", 0))
    ded = float(ev.get("deductions", {}).get("total", 0))
    raw = sum(float(c["score"]) for c in cats)
    ceiling = sum(c["max"] for c in cats) or 100
    total = max(0.0, min(100.0, raw + bonus - ded))
    headline, band = band_for(raw / ceiling)
    return {"cats": cats, "bonus": num(bonus), "ded": num(ded), "total": num(total), "headline": headline,
            "band": band, "ev": ev, "has": bool(cats)}


def all_bullets(r: dict):
    for ri, role in enumerate(r.get("experience", [])):
        for b in role.get("bullets", []):
            yield ri, role, b


def ring(total, size_mm=38) -> str:
    dash = round(276.46 * min(1.0, max(0.0, float(total) / 100)), 2)
    return f"""<div class="ring" style="width:{size_mm}mm;height:{size_mm}mm">
      <svg viewBox="0 0 100 100">
        <circle cx="50" cy="50" r="44" fill="none" stroke="#E4DDF8" stroke-width="9"/>
        <circle cx="50" cy="50" r="44" fill="none" stroke="#7F56D9" stroke-width="9" stroke-linecap="round" stroke-dasharray="{dash} 276.46"/>
      </svg>
      <div class="num"><div class="big">{e(total)}</div><div class="of">/ 100</div></div>
    </div>"""


def topbar(kicker: str) -> str:
    return f'<div class="topbar"><img src="assets/amigoscode-wordmark.svg" alt="amigoscode"/><div class="kicker">{e(kicker)}</div></div>'


def chip(score, cls="") -> str:
    return f'<span class="chip {tone10(score)} {cls}">{e(score)}</span>' if score is not None else ""


def build_html(r: dict) -> str:
    rubric = load_rubric(r.get("target", {}))
    fit = role_fit(r, rubric)
    name = r["basics"]["name"]
    first = name.split()[0]
    position = rubric.get("position_title", "the target role")
    date = dt.date.today().strftime("%d %B %Y")

    bullets = [b for _, _, b in all_bullets(r)]
    scored = [b["score"] for b in bullets if b.get("score") is not None]
    avg = round(sum(scored) / len(scored), 1) if scored else 0
    at7 = sum(1 for s in scored if s >= 7)
    plans = {k: sum(1 for b in bullets if b.get("plan") == k) for k in PLAN_LABELS}
    kept = plans["xyz"] + plans["strong"] + plans["keep"]
    xyz_share = round(100 * plans["xyz"] / kept) if kept else 0

    summ = r.get("summary") or {}
    edu = r.get("education", [])
    edu_scores = [x["score"] for x in edu if x.get("score") is not None]
    edu_avg = round(sum(edu_scores) / len(edu_scores), 1) if edu_scores else None
    checks = r.get("format_checks", [])
    passed = sum(1 for c in checks if c.get("status") == "pass")
    skills_score = (r.get("skills_review") or {}).get("score")

    # ---------- page 1: overview ----------
    cards = [
        ("Role fit", f"{fit['total']}", "/ 100", "" if not fit["has"] else ("high" if float(fit["total"]) >= 70 else "low" if float(fit["total"]) < 50 else "mid")),
        ("Bullets", f"{avg}", f"avg / 10 · {at7} of {len(scored)} at 7+", tone10(avg)),
        ("Summary", "Off", "not included", "") if summ.get("include") is False else ("Summary", f"{summ.get('score', '–')}", "/ 10", tone10(summ.get("score"))),
        ("Education", f"{edu_avg if edu_avg is not None else '–'}", "/ 10", tone10(edu_avg)),
        ("Skills", f"{skills_score if skills_score is not None else '–'}", "/ 10", tone10(skills_score)),
        ("Format", f"{passed}/{len(checks)}", "checks passed", "high" if checks and passed == len(checks) else "mid"),
    ]
    cards_html = "".join(
        f'<div class="stat {t}"><div class="lbl">{e(l)}</div><div class="val">{e(v)}</div><div class="unit">{e(u)}</div></div>'
        for l, v, u, t in cards
    )
    fixes = "".join(f'<li><span class="dot">{i}</span>{e(f)}</li>' for i, f in enumerate(r.get("top_fixes", []), 1))
    overview_line = (
        f"{e(first)}'s resume scores <b>{fit['total']}/100</b> against the {e(position)} rubric. "
        f"Experience bullets average <b>{avg}/10</b>, with {at7} of {len(scored)} already at 7 or above."
    )
    page1 = f"""<section class="page">
  {topbar("CV review")}
  <h1>{e(name)}</h1>
  <p class="sub">Reviewed for <b>{e(position)}</b> &nbsp;·&nbsp; {e(date)}</p>
  <div class="hero">
    {ring(fit['total'])}
    <div><h2>{e(fit['headline'])}</h2><p>{overview_line}</p><span class="band">{e(fit['band'])}</span></div>
  </div>
  <h3>Scorecard</h3>
  <div class="stats">{cards_html}</div>
  <h3>Top fixes, in order</h3>
  <ul class="up">{fixes}</ul>
  <h3>What happens next</h3>
  <div class="steps">
    <div class="step done"><b>1 · /resume:analyse</b><span>This report: every section scored, questions for each weak bullet.</span></div>
    <div class="step"><b>2 · /resume:improve</b><span>Answer the questions one bullet at a time. Claude rewrites each one with you.</span></div>
    <div class="step"><b>3 · /resume:build</b><span>Final LaTeX resume and PDF, 2 pages max.</span></div>
  </div>
</section>"""

    # ---------- page 2: role fit ----------
    page2 = ""
    if fit["has"]:
        cats_html = "".join(f"""<div class="cat">
      <div><div class="name">{e(c['label'])}<span>weight {c['max']}</span></div>
      <div class="bar {c['tone']}"><i style="width:{c['pct']}%"></i></div>
      <div class="evidence">{e(c['evidence'])}</div></div>
      <div class="score">{c['score']}<small>of {c['max']}</small></div></div>""" for c in fit["cats"])
        ev = fit["ev"]
        strengths = "".join(f'<li><span class="dot">✓</span>{e(s)}</li>' for s in ev.get("key_strengths", []))
        levels = "".join(f'<li><span class="dot">{i}</span>{e(s)}</li>' for i, s in enumerate(ev.get("areas_for_improvement", []), 1))
        page2 = f"""<section class="page">
  {topbar(f"{name} · role fit")}
  <h3>How a hiring rubric reads this resume</h3>
  <p class="lead">Scored against the {e(position)} rubric, the same shape of rubric an automated screen or a hiring manager applies. Only what the resume shows counts.</p>
  {cats_html}
  <div class="adj">
    <div class="card"><div class="lbl">Bonus points</div><div class="val plus">+{fit['bonus']}</div><p>{e(ev.get('bonus_points', {}).get('breakdown', ''))}</p></div>
    <div class="card"><div class="lbl">Deductions</div><div class="val {'minus' if fit['ded'] else ''}">{'-' if fit['ded'] else ''}{fit['ded']}</div><p>{e(ev.get('deductions', {}).get('reasons', ''))}</p></div>
  </div>
  <div class="two">
    <div><h3>Key strengths</h3><ul class="ok">{strengths}</ul></div>
    <div><h3>Where to level up</h3><ul class="up">{levels}</ul></div>
  </div>
</section>"""

    # ---------- page 3: summary ----------
    crit_rows = "".join(
        f'<tr><td><span class="st {STATUS.get(c.get("status"), ("?", ""))[1]}">{STATUS.get(c.get("status"), ("?", ""))[0]}</span></td>'
        f'<td><b>{e(c.get("name"))}</b></td><td>{e(c.get("note"))}</td></tr>'
        for c in summ.get("criteria", [])
    )
    sq = "".join(f"<li>{e(q)}</li>" for q in summ.get("questions", []))
    page3 = f"""<section class="page">
  {topbar(f"{name} · summary")}
  <h3>Professional summary {chip(summ.get('score'))}<small class="of10">/ 10</small></h3>
  <blockquote>{e(summ.get('text', 'No summary on the current resume.'))}</blockquote>
  <table class="crit">{crit_rows}</table>
  {'<h4>Answer these to rewrite it</h4><ol class="qs">' + sq + '</ol>' if sq else ''}
  <p class="note">{"You chose to leave the summary off the resume. The score is here for reference only." if summ.get("include") is False else "The rewrite will be two sentences, about 30–45 words, built only from facts the resume can back up. Not sure you want a summary? It's optional: you'll be asked before the build."}</p>
</section>""" if summ else ""

    # ---------- experience ----------
    role_blocks = []
    for ri, role in enumerate(r.get("experience", [])):
        items = []
        for b in role.get("bullets", []):
            label, cls = PLAN_LABELS.get(b.get("plan"), ("", ""))
            if b.get("plan") == "merge" and b.get("merge_into"):
                label = f"Merge into {b['merge_into']}"
            qs = "".join(f"<li>{e(q)}</li>" for q in b.get("questions", []))
            items.append(f"""<div class="bullet">
        <div class="bh">{chip(b.get('score'))}<span class="bid">{e(b.get('id'))}</span><span class="plan {cls}">{e(label)}</span></div>
        <div class="bt">{e(b['text'])}</div>
        <div class="why">{e(b.get('reason'))}</div>
        {'<ol class="qs">' + qs + '</ol>' if qs else ''}
      </div>""")
        role_blocks.append(f"""<div class="role">
      <div class="rh"><b>{e(role['role'])}</b> – <i>{e(role['company'])}</i><span>{e(role.get('start'))} – {e(role.get('end'))} | {e(role.get('location'))}</span></div>
      {''.join(items)}
    </div>""")
    mix_warn = "" if xyz_share <= 50 else '<p class="warn">More than half the bullets are planned as XYZ. Move a few to "strong, no metric" so the resume doesn\'t read as padded.</p>'
    total_kept = kept or 1
    page4 = f"""<section class="page flow">
  {topbar(f"{name} · experience")}
  <h3>Experience bullets</h3>
  <p class="lead">Each bullet is scored 0–10 on Google's XYZ idea: <i>accomplished X, measured by Y, by doing Z</i>. Not every bullet should be XYZ. About a third get a number; the rest get their strength from scope, ownership, specific tech and outcomes in words.</p>
  <div class="mix">
    <div class="mixbar">
      <i class="xyz" style="width:{100 * plans['xyz'] / total_kept}%"></i><i class="strong" style="width:{100 * plans['strong'] / total_kept}%"></i><i class="keep" style="width:{100 * plans['keep'] / total_kept}%"></i>
    </div>
    <div class="legend"><span class="xyz">XYZ rewrite · {plans['xyz']}</span><span class="strong">Strong, no metric · {plans['strong']}</span><span class="keep">Keep · {plans['keep']}</span><span>Merge · {plans['merge']}</span><span>Cut · {plans['cut']}</span><span><b>{xyz_share}% XYZ</b></span></div>
    {mix_warn}
  </div>
  {''.join(role_blocks)}
</section>"""

    # ---------- education, skills, format ----------
    edu_html = "".join(f"""<div class="bullet">
      <div class="bh">{chip(x.get('score'))}<b>{e(x['degree'])}</b> – <i>{e(x['school'])}</i><span class="right">{e(x.get('start'))} – {e(x.get('end'))} | {e(x.get('location'))}</span></div>
      {''.join(f'<div class="why">{e(n)}</div>' for n in x.get('notes', []))}
      {'<ol class="qs">' + ''.join(f'<li>{e(q)}</li>' for q in x.get('questions', [])) + '</ol>' if x.get('questions') else ''}
    </div>""" for x in edu)
    skills_notes = "".join(f"<li>{e(n)}</li>" for n in (r.get("skills_review") or {}).get("notes", []))
    check_rows = "".join(
        f'<tr><td><span class="st {STATUS.get(c.get("status"), ("?", ""))[1]}">{STATUS.get(c.get("status"), ("?", ""))[0]}</span></td>'
        f'<td><b>{e(c.get("check"))}</b></td><td>{e(c.get("note"))}</td></tr>'
        for c in checks
    )
    page5 = f"""<section class="page flow">
  {topbar(f"{name} · education, skills & format")}
  <h3>Education {chip(edu_avg)}<small class="of10">/ 10</small></h3>
  {edu_html or '<p class="note">No education listed.</p>'}
  <h3>Skills {chip(skills_score)}<small class="of10">/ 10</small></h3>
  <ul class="plain">{skills_notes}</ul>
  <h3>Format checks</h3>
  <table class="crit">{check_rows}</table>
  <div class="method">
    <b>Method.</b> Role fit uses a rubric adapted from HackerRank's open-source <b>hiring-agent</b>, with level-specific rubrics written by Amigoscode.
    Bullets and summary are scored against the Amigoscode resume rubric. Scores are directional: a re-run can move them by a point or two.
    <b>Fairness:</b> name, gender, age, nationality, school prestige, grades and location are ignored; only what was built, owned and shipped counts.
    <div class="meta">rubric: {e(r.get('target', {}).get('rubric'))} · generated {e(date)}</div>
  </div>
  <div class="endfoot">Prepared with <b>amigoscode</b> · amigoscode.com</div>
</section>"""

    css = (REPORT / "report.css").read_text()
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"/>
<title>{e(name)} · CV Review · Amigoscode</title><style>{css}</style></head>
<body>{page1}{page2}{page3}{page4}{page5}</body></html>"""


def find_chrome(explicit: str | None) -> str | None:
    for c in [explicit, *CHROME_CANDIDATES]:
        if c and Path(c).exists():
            return c
    return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("review", type=Path)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--chrome")
    args = ap.parse_args()

    r = json.loads(args.review.read_text())
    stem = "_".join(r["basics"]["name"].split()) + "_CV_Review"
    pdf = (args.out or args.review.parent / f"{stem}.pdf").resolve()
    html_path = pdf.with_suffix(".html")
    html_path.write_text(build_html(r))

    assets = pdf.parent / "assets"
    if not assets.exists():
        shutil.copytree(REPORT / "assets", assets)

    chrome = find_chrome(args.chrome)
    if not chrome:
        print(f"wrote {html_path}\nNo Chrome/Chromium/Edge found: open the HTML and print to PDF (A4, no margins).", file=sys.stderr)
        sys.exit(2)
    subprocess.run(
        [chrome, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--virtual-time-budget=8000",
         f"--print-to-pdf={pdf}", html_path.as_uri()],
        check=True, capture_output=True,
    )
    print(f"wrote {pdf}")


if __name__ == "__main__":
    main()
