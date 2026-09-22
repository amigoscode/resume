# resume

A Claude Code skill that turns any CV into a clean one-page LaTeX resume, then helps you make it stronger.

[![Sample resume](assets/sample.png)](assets/sample.pdf)

## What it does

1. **Converts your CV** (PDF or pasted text) into a modified [Jake's Resume](https://github.com/jakegut/resume) template:
   - name and one contact line (location | phone | email | LinkedIn)
   - each role on one line: **Role** – *Company* · `Start – End | Location`
   - Summary → Experience → Skills → Education
2. **Builds the PDF locally** with Tectonic (or pdflatex). It warns you when it overflows one page or a line runs past the margin.
3. **Scores every experience bullet 0–10** right in the PDF (`[3] – Design and develop ...`), with a per-role breakdown.
4. **Interviews you one bullet at a time** to rewrite it. You get a natural mix of Google XYZ bullets (*accomplished X, measured by Y, by doing Z*) and strong bullets without metrics. It never makes up numbers.
5. **Scores and rewrites your professional summary** using the [FAANG Tech Leads summary guidance](https://www.faangtechleads.com/resume/professional-summary).

## Install

```bash
git clone https://github.com/amigoscode/resume ~/.claude/skills/resume
brew install tectonic   # LaTeX compiler, ~20 MB
```

Then in Claude Code:

```
Here's my CV: ~/Downloads/my-cv.pdf. Make a LaTeX version and rate my bullets.
```

## Build without Claude

```bash
cp ~/.claude/skills/resume/assets/template.tex My_Resume.tex
# edit My_Resume.tex
~/.claude/skills/resume/scripts/build.sh My_Resume.tex --open
```

The template also works on [Overleaf](https://overleaf.com): paste it in and click Recompile.

## Layout

```
SKILL.md               # the workflow Claude follows
assets/template.tex    # the LaTeX template (sample content)
assets/sample.pdf/.png  # the template, built
scripts/build.sh       # build + page count + margin-overflow check
references/bullets.md  # bullet scoring rubric, interview questions, rewrite rules
references/summary.md  # summary scoring rubric and rewrite pattern
```

## Credits

Template based on [jakegut/resume](https://github.com/jakegut/resume) by Jake Gutierrez, itself based on [sb2nov/resume](https://github.com/sb2nov/resume). MIT licensed.
