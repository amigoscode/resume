---
name: build
description: Build the final one-page LaTeX resume and PDF from a reviewed CV, on a modified Jake's Resume template (name plus one contact line, "Role – Company" with "date | location", Summary → Experience → Skills → Education). Uses the rewrites from /resume:improve, checks the resume fits one page and nothing runs past the margin, and outputs a clean .tex and .pdf. Use when someone wants the final resume, a LaTeX or "lex" version of their CV, a Jake's-template resume, or a PDF of the improved CV. Final step of /resume:analyse → /resume:improve → /resume:build; also works straight from a CV with no review.
---

# /resume:build

Produce the final `.tex` and `.pdf`.

## Where things are

The plugin root is two directories above this skill's base directory.

- `./<first-last>/review.json`: source of truth (see `references/review-schema.md`).
- `assets/template.tex`: the template (preamble and macros).
- `scripts/render_tex.py`: `review.json` → `.tex` (does the escaping; uses `rewrite` over `text` and drops `merge`/`cut` bullets).
- `scripts/build.sh`: `.tex` → `.pdf`; reports page count and lines that run past the margin.

## No review yet?

If there's no `review.json`, the person wants a straight conversion. Extract the CV into `review.json` the same way `/resume:analyse` does in step 2 (faithful, no new facts). Leave out scores and plans, then carry on below. Suggest `/resume:analyse` afterwards if they want feedback.

## Steps

1. Check for unfinished work. If some `xyz` or `strong` bullets have no `rewrite`, say how many and ask whether to build anyway (they'll use the original text) or go back to `/resume:improve`.
2. Render and build:

   ```bash
   python3 <plugin-root>/scripts/render_tex.py ./<first-last>/review.json ./<first-last>/<First_Last>_Resume.tex
   <plugin-root>/scripts/build.sh ./<first-last>/<First_Last>_Resume.tex --open
   ```

   If no LaTeX compiler is installed, suggest `brew install tectonic` (about 20 MB, builds in seconds). Avoid Docker TeX images: the multi-GB download makes the first build slow.
3. Fix what the build script reports:
   - **Text past the margin**: a role, company, degree or skills line is too long. Shorten it in `review.json` (e.g. drop "Faculty of ..." from a university) and rebuild. Tectonic doesn't fail on this, so always check the warning.
   - **More than one page**: say exactly what spills over, and offer options: cut the lowest-scoring remaining bullets in older roles, trim the skills lines, or switch to 10pt (change `11pt` in the `\documentclass` line of the generated `.tex`). Let the person choose; don't cut their content silently.
4. Look at the PDF (`pdftoppm -png -r 80` a page and view it) for anything odd: stray `[N]` prefixes, escaped characters, empty sections.

## Layout rules

These came from real feedback; keep them unless the person asks otherwise:
- **Header**: the name, then one line: `location | phone | email | LinkedIn` (and GitHub). No job title under the name.
- **Role headers**: one line, **Role** – *Company* on the left and `Start – End | Location` on the right.
- **Section order**: Summary, Experience, Skills, then any extra sections (e.g. Certifications), then Education.
- **Leave out**: skill bars, soft-skill grids, Training and Languages sections, unless the person asks for them.

## Reply

Give the `.tex` and `.pdf` paths and the page count. If the person went through `/resume:improve`, also give before → after: bullet average, bullets at 7 or above, and the XYZ/strong mix. Mention they can re-run `/resume:analyse` on the new PDF to see the new role-fit score.
