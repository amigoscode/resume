---
name: analyse
description: Full analysis of a CV or resume. Scores it against a hiring rubric for the target role (hiring-agent style, intern to senior engineer or engineering manager, or a custom rubric for any other role), scores every experience bullet 0-10, the professional summary, skills, education and format, writes the questions needed to improve each weak bullet, and produces an Amigoscode-branded PDF report of what to improve. Use when someone shares a CV and wants it reviewed, rated, scored, critiqued, "analysed", checked against a role, or asks what to improve, even if they don't say "analyse". First step of /resume:analyse → /resume:improve → /resume:build.
---

# /resume:analyse

Read a CV, score every part of it, and hand the person a branded PDF report that says exactly what to improve and which questions they need to answer.

This step never rewrites the resume. Its output is a judgment plus a plan. `/resume:improve` does the rewriting with the person, and `/resume:build` makes the final PDF.

## Where things are

The plugin root is two directories above this skill's base directory. Paths below are relative to it.

- `references/review-schema.md`: the `review.json` format. Read it before writing the file.
- `references/bullets.md`: the 0–10 bullet rubric and the XYZ/strong balance rules.
- `references/summary.md`: the summary rubric.
- `rubrics/<role>/role.json` and `criteria.md`: hiring rubrics for software_engineering_intern, junior_software_engineer, mid_level_software_engineer, senior_software_engineer and engineering_manager.
- `scripts/make_report.py`: renders the branded report PDF from `review.json`.
- `scripts/render_tex.py` and `scripts/build.sh`: render and build a resume PDF (used here only for the page-count check).

## Steps

### 1. Read the CV and pick the target

Read the CV (PDF with the Read tool, or pasted text). Two-column CVs often extract out of order, so check the page image if the text looks jumbled.

Work out the target role: from what the person says, a job description they paste, or their current title. Pick the closest rubric under `rubrics/`. If none fits (a solutions architect, designer, PM or contact center role, for example), write a custom rubric with the same shape as `role.json`: four categories summing to 100, a bonus up to 15, and a one-line description per category. Put it in `target.custom_rubric` and set `target.rubric` to `"custom"`. Say which rubric you used, and why, in the chat reply.

### 2. Extract faithfully

Fill `basics`, `experience`, `skills` and `education` exactly as the CV says, cleaning only grammar and tense. Don't add facts, numbers or tools. Give bullets stable ids (`e1-b1`, ...). Put phone and email in as written, even if they're placeholders, and flag that in `format_checks`.

### 3. Score

- **Role fit**: apply the rubric's `criteria.md` (or your custom rubric) and fill `role_evaluation`. Every score needs evidence quoted from the resume. Follow the fairness rules: ignore name, age, nationality, school prestige and location.
- **Bullets**: score each one 0–10 with `references/bullets.md` and give a one-line `reason`.
- **Summary**: score it with `references/summary.md` and fill `criteria` with pass, partial or fail and a note for each.
- **Skills**: score 0–10 on relevance to the target, grouping, evidence in bullets, and padding. Give 2–4 notes.
- **Education**: score 0–10 per entry. Check relevance, format, and whether certifications or training belong in their own line. Give notes, plus questions if something is missing.
- **Format checks**: fits on one page (render with `scripts/render_tex.py` and run `scripts/build.sh` to check), consistent dates, one-line role headers, ATS-readable, real contact details.

### 4. Plan the improvements, with a balance

Give every bullet a `plan`:
- `xyz`: it has, or plausibly has, a real number. It gets rewritten as *accomplished X, measured by Y, by doing Z*.
- `strong`: it gets its strength from scope, ownership, specific tech and outcome in words, with no metric.
- `keep`: already 7 or above.
- `merge`: its facts belong in another bullet. Set `merge_into`.
- `cut`: low signal, and cutting it helps the resume fit one page.

Keep `xyz` to roughly 30–40% of the kept bullets (xyz + strong + keep), never more than half. A resume where every line has a percentage reads as fabricated, and the person asked for a balance. The report shows the mix, and warns if it's over 50%.

For every `xyz` and `strong` bullet, write 2–5 short questions that would unlock the rewrite (scope, ownership, tech, result). Only ask for a number when one plausibly exists, and say rough answers are fine. `keep` bullets get at most one optional question. `merge` and `cut` bullets get none.

Write `top_fixes`: the three changes that would move the resume most, in order.

### 5. Write the files and the report

Save to `./<first-last>/review.json`, then run:

```bash
python3 <plugin-root>/scripts/make_report.py ./<first-last>/review.json
```

This writes `<First_Last>_CV_Review.pdf` (and the `.html`) next to `review.json`. It needs Google Chrome, Chromium or Edge. If none is found, the script leaves the HTML for the person to print. Open the PDF on macOS with `open`.

Look at the rendered pages (convert a couple with `pdftoppm -png -r 60` and view them) to catch layout problems before handing it over.

### 6. Reply

Keep it short. Include:
- the report path
- the role fit score and which rubric was used
- the bullet average, with how many bullets are at 7 or above
- the planned mix (e.g. "8 XYZ, 10 strong, 2 keep, 6 merge, 4 cut: 40% XYZ")
- the top three fixes
- the next step: `/resume:improve` to answer the questions one bullet at a time.
