# resume

A Claude Code plugin that reviews your CV like a hiring rubric would, helps you rewrite it one bullet at a time, and builds a clean LaTeX resume of one or two pages.

| Branded review report | Final resume |
|---|---|
| [![Review report](assets/sample-report.png)](examples/jane-doe/Jane_Doe_CV_Review.pdf) | [![Resume](assets/sample.png)](assets/sample.pdf) |

## Commands

Run them in order. `/resume:skills` and `/resume:summary` stay locked until the steps before them are done, because both are built from the finished bullets.

| Step | Command | What it does | Output |
|---|---|---|---|
| 1 | `/resume:analyse` | Scores the whole CV: fit for the target role (hiring-agent style rubric), every experience bullet 0–10, the summary, skills, education and format. Plans each bullet (XYZ, strong without a metric, keep, merge or cut) and writes the questions you need to answer. | `<First_Last>_CV_Review.pdf` (amigoscode-pdf house style) and `review.json` |
| 2 | `/resume:improve` | Goes one bullet at a time: asks the questions, rewrites the bullet from your answers and re-scores it, then covers education. Keeps a balance: about a third of the bullets get XYZ with a real number, and the rest are strong without one. Never invents numbers. | updated `review.json` and a scored preview PDF |
| 3 | `/resume:skills` | Tailors the Skills section to a job description you paste, to current postings for your target role, or both. Shows which keywords your bullets already back up, asks you about the gaps, and only adds skills you confirm. **Needs step 2 done.** | new skills lines and keyword coverage before → after |
| 4 | `/resume:summary` | Asks whether you want a summary at all. If you do, writes it last from the finished bullets and skills. **Needs steps 2 and 3 done.** | a two-sentence summary, or none |
| 5 | `/resume:build` | Renders the final resume on a modified [Jake's Resume](https://github.com/jakegut/resume) template. Checks it's no more than 2 pages and that no line runs past the margin. Can output the `.tex` only. | `<First_Last>_Resume.tex` and `.pdf` |

Everything for one person lives in `./<first-last>/`. `review.json` carries the state between commands, so you can stop and pick up again later.

### How bullets are scored

Bullets are scored against Google's XYZ format: *accomplished [X], as measured by [Y], by doing [Z]*.

| Score | The bullet has |
|---|---|
| 0–2 | A duty or a vague claim ("Helped teams achieve goals") |
| 3–4 | A clear task with specific tech or scope, but no result |
| 5–6 | A task plus one strong element: a number, scope, ownership or an outcome |
| 7–8 | A clear result plus how it was done: a metric, or strong scope, ownership and tech |
| 9–10 | Full XYZ: a meaningful result, a real measure and a specific method |

If every bullet has a percentage, the resume looks fabricated. The plan keeps XYZ bullets to roughly 30–40%. The others get their strength from scope, ownership, specific tools and outcomes described in words.

### Role rubrics

Adapted from HackerRank's open-source [hiring-agent](https://github.com/interviewstreet/hiring-agent):

- `software_engineering_intern`
- `junior_software_engineer`
- `mid_level_software_engineer`
- `senior_software_engineer`
- `engineering_manager`

For any other role (solutions architect, PM, designer, and so on), `/resume:analyse` writes a custom rubric in the same shape and says so in the report.

## Install

In Claude Code:

```
/plugin marketplace add amigoscode/resume
/plugin install resume@amigoscode
```

You'll also need:
- **A LaTeX compiler:** `brew install tectonic`. It's about 20 MB and builds in seconds. `pdflatex` works too.
- **WeasyPrint:** `pipx install weasyprint`. It renders the review report in the [amigoscode-pdf](vendor/amigoscode-pdf) house style.
- **Inter font:** installed locally, for the report.
- **Python 3.10+:** the scripts use only the standard library.

Then:

```
/resume:analyse ~/Downloads/my-cv.pdf, I'm targeting senior backend roles
```

## Layout

```
.claude-plugin/          plugin + marketplace manifests
skills/analyse/          /resume:analyse
skills/improve/          /resume:improve
skills/skills/           /resume:skills
skills/summary/          /resume:summary
skills/build/            /resume:build
references/              bullet and summary rubrics, review.json schema
rubrics/                 hiring rubrics per role (role.json + criteria.md)
vendor/amigoscode-pdf/   the amigoscode-pdf builder (used when the skill isn't installed)
scripts/make_report.py   review.json -> review PDF via amigoscode-pdf
scripts/render_tex.py    review.json -> resume .tex (with --scores for a scored preview)
scripts/build.sh         .tex -> .pdf, page count and margin-overflow check
scripts/progress.py      pipeline status; blocks skills/summary until the steps before are done
assets/template.tex      the LaTeX template
examples/jane-doe/       a sample review.json and its report
```

## Build without Claude

```bash
python3 scripts/render_tex.py examples/jane-doe/review.json Jane_Doe_Resume.tex
scripts/build.sh Jane_Doe_Resume.tex --open
python3 scripts/make_report.py examples/jane-doe/review.json
```

## Credits

- Resume template: [jakegut/resume](https://github.com/jakegut/resume) by Jake Gutierrez, based on [sb2nov/resume](https://github.com/sb2nov/resume). MIT.
- Role rubrics: adapted from [interviewstreet/hiring-agent](https://github.com/interviewstreet/hiring-agent) by HackerRank. MIT, see `rubrics/LICENSE-hiring-agent`.
- Summary guidance: [FAANG Tech Leads](https://www.faangtechleads.com/resume/professional-summary).
- Report style: amigoscode-pdf, the Amigoscode print guideline (bundled in `vendor/amigoscode-pdf`).
