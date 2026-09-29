---
name: summary
description: Write or rewrite the professional summary (intro) at the top of a resume, as the last writing step, from the finished bullets and skills. It first asks whether the person wants a summary at all. Only runs after the bullets (/resume:improve) and skills (/resume:skills) are done. Use when someone wants to write, improve or tailor their resume summary, profile, intro or "about" section. Step 4 of /resume:analyse → /resume:improve → /resume:skills → /resume:summary → /resume:build.
---

# /resume:summary

The summary goes last because it's a two-sentence version of everything below it. Written earlier, it would describe a resume that no longer exists.

## Where things are

The plugin root is two directories above this skill's base directory.

- `./<first-last>/review.json`: the `summary` block (see `references/review-schema.md`).
- `references/summary.md`: rubric, rewrite pattern, what to avoid. Read it before writing.
- `scripts/progress.py`: pipeline status and gating.

## 1. Gate: bullets and skills first

1. Ask: "Have you finished your bullets (`/resume:improve`) and skills (`/resume:skills`)?"
2. Check with:

   ```bash
   python3 <plugin-root>/scripts/progress.py ./<first-last>/review.json --require summary
   ```

3. If it says BLOCKED, stop. Don't draft a summary. Say which step is missing and point to that command. Offer to start it now.

## 2. Include one at all?

If `summary.include` is `null`, ask: "Do you want a professional summary at the top, or go straight to Experience?"
- **No**: set `include` to false, say it'll be left out of the resume, mark the step done (below) and point to `/resume:build`.
- **Yes**: set `include` to true and carry on.

## 3. Write it

1. Ask only the questions from `summary.questions` (and `references/summary.md`) that the finished resume doesn't already answer. The target role is usually known by now, from `target` and `skills_tailoring`.
2. Draft two sentences, about 30–45 words:
   - Sentence one: title, years, domain, 2–4 real tools, and the scale fact.
   - Sentence two: how they work, or their strength, plus their single best result.
3. Pull the facts from the rewritten bullets and the tailored skills. Don't use anything the resume doesn't show: no new numbers, no specialties the bullets don't back up. If a job description was used in `/resume:skills`, lead with its top keywords where they're true.
4. Score the draft against the rubric in `references/summary.md`. Show the old and new versions with their scores, and offer one alternative angle if there's a real choice (e.g. lead with scale, or lead with the headline result).

Once they pick one, save `rewrite`, `new_score` and `answers`, then mark the step done:

```bash
python3 <plugin-root>/scripts/progress.py ./<first-last>/review.json --mark summary
```

## 4. Next

Point to `/resume:build` for the final `.tex` and PDF.
