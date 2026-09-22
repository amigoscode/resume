---
name: resume
description: Turn any CV or resume (PDF, Word export, or pasted text) into a clean one-page LaTeX resume on a modified Jake's Resume template, build the PDF locally, then review and improve it. Scores every experience bullet 0-10 inline in the PDF, interviews the person one bullet at a time to rewrite weak bullets (a natural mix of Google XYZ bullets and strong non-metric ones, never invented numbers), and scores and rewrites the professional summary. Use this whenever someone wants to convert, rebuild, reformat or "LaTeX" a CV, make a "Jake's resume" or ATS-friendly resume, rate or review resume bullets, apply the XYZ formula, improve a resume summary or intro, or get a CV onto one page, even if they just share a CV and say "make this better" or "lex version".
---

# Resume

Convert a CV into a one-page LaTeX resume, build it to PDF, then improve it with the person through scoring and short interviews.

The person usually cares about three things: the resume looks clean and fits on one page, every claim is true, and the bullets read as strong without looking padded. Keep those in mind at every step.

## Files in this skill

- `assets/template.tex`: the template (sample content). Copy it; don't edit it in place.
- `assets/sample.pdf`: what the template looks like when built.
- `scripts/build.sh <file.tex> [--open]`: builds the PDF and reports page count and lines that run past the margin.
- `references/bullets.md`: scoring rubric, interview questions and rewrite rules for experience bullets. Read it before scoring or rewriting bullets.
- `references/summary.md`: the same for the professional summary. Read it before scoring or rewriting the summary.

## 1. Convert the CV

1. Read the CV. For a PDF, use the Read tool; if the text comes out jumbled (two-column CVs often do), ask the person to paste the text, or check the rendered page image to get the reading order right.
2. Copy `assets/template.tex` to `<First>_<Last>_Resume.tex` in the working directory and replace the sample content.
3. Carry over every role and bullet faithfully. Clean up grammar and tense, but don't add facts, numbers or tools that aren't in the CV. Format money as `\$4M+` and percentages as `90\%`.

Layout rules (these came from real feedback; follow them unless the person asks otherwise):
- **Header**: name, then one line with `location $|$ phone $|$ email $|$ LinkedIn` (and GitHub if they have one). No job title line under the name.
- **Roles**: `\resumeSubheading{Role}{Start -- End}{Company}{Location}` renders as one line: **Role** – *Company* on the left, `Start – End | Location` on the right.
- **Section order**: Summary, Experience, Skills, Education (Education last).
- **Skills**: group into 3–6 labelled lines. Leave out skill-level bars, long soft-skill grids, Training and Languages sections unless the person wants them.
- Escape LaTeX specials in content: `& % $ # _`.

## 2. Build and check

Run `scripts/build.sh <file>.tex --open`.

- If neither `tectonic` nor `pdflatex` is installed, suggest `brew install tectonic` (about 20 MB, builds in seconds). Avoid Docker TeX images: the multi-GB download makes the first build slow.
- If the script warns that text runs past the right margin, a subheading or skills line is too long. Shorten it (e.g. drop "Faculty of ..." from a university) and rebuild. Tectonic won't fail on this, so check the warning every time.
- If it's more than one page, say exactly what spills onto page 2 and offer options (10pt font, trimming older roles' bullets, dropping a section). Let the person choose; don't cut their content silently.

Tell the person where the PDF is after every build.

## 3. Score the experience bullets

Read `references/bullets.md`. Prepend `[N] -- ` to every experience bullet, rebuild so the scores are visible in the PDF, and give the overview in chat (average, per-role table, best and worst bullets, patterns). Don't rewrite yet.

## 4. Improve bullets one at a time

Follow the interview loop in `references/bullets.md`: one bullet per turn, 3–5 short questions, a draft with `[placeholders]`, then the rewrite and new score.

Two principles matter most:
- **Mix formats.** Only about a third of bullets should be full XYZ with a metric. The rest get their strength from scope, ownership, specific tech and outcomes in words. A resume where every line has a percentage looks fabricated.
- **Never invent numbers.** Use only figures the person gives. If they don't have one, write the strongest honest version.

When all bullets are done, remove the `[N] -- ` prefixes and do a final build.

## 5. Score and improve the summary

Read `references/summary.md`. Score the summary with its rubric, ask the questions it lists, and propose a two-sentence rewrite built only from facts in the resume. Ask before putting it in the `.tex`.

## Working style

- Wait for the person before moving between steps; they often want to adjust something first.
- Keep chat replies short: what changed, where the PDF is, and the one decision you need from them.
