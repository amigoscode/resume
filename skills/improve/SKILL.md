---
name: improve
description: Interactive resume improvement. Walks the person through their CV one bullet at a time, asks the questions from the analysis, and rewrites each bullet with them, keeping a natural balance of Google XYZ bullets and strong non-metric bullets and never inventing numbers. Then does the same for the summary and education. Use after /resume:analyse, or whenever someone wants help rewriting resume bullets, applying the XYZ formula, making experience "stronger", or answering questions to improve their CV. Second step of /resume:analyse → /resume:improve → /resume:build.
---

# /resume:improve

Turn the analysis into better bullets through a short conversation, one bullet at a time. The person knows the facts; your job is to ask the right questions and write the strongest honest line from their answers.

## Where things are

The plugin root is two directories above this skill's base directory.

- `./<first-last>/review.json`: the analysis (see `references/review-schema.md`). If it doesn't exist, run the `/resume:analyse` steps first.
- `references/bullets.md`: rewrite rules and examples. Read it before the first rewrite.
- `references/summary.md`: the summary rewrite pattern.
- `scripts/render_tex.py --scores` and `scripts/build.sh`: build a preview PDF with `[N]` scores on each bullet.

## The loop

Order: current role first, then down the resume. Skip bullets whose plan is `keep` (unless they have an optional question), `merge` or `cut`. If the person names a bullet id, start there. If the file already has rewrites, resume from the first bullet without one.

For each bullet, in one message:
1. Show the id, its score and the current text, with the one-line reason.
2. Show the plan: **XYZ** (we'll add a measure) or **Strong, no metric** (scope, ownership, tech, outcome in words). If it absorbs merged bullets, show their text too.
3. Ask the bullet's questions from `review.json` (2–5). Tell them rough answers are fine, and "don't know" is a fine answer.
4. Show a draft shape with `[placeholders]` so they see where the answers go.

When they answer:
- Write the rewrite and give it a new score. Aim for 7 or above; if the facts only support 6, say so rather than stretching them.
- Use only what they said. Never add or round up a number, a tool, a team size or a client. If they don't have a number for an `xyz` bullet, switch it to `strong` and write it without one.
- Save straight away to `review.json`: `answers`, `rewrite`, `new_score`, `format` (`xyz` or `strong`). This way a stopped session can pick up where it left off.
- Show the new line and its score in one or two lines, then move to the next bullet.

Keep an eye on the balance. After every few bullets, give the running mix (e.g. "so far: 4 XYZ, 5 strong"). If XYZ is heading past about 40% of kept bullets, write the next borderline one as `strong`, and tell the person why: an all-metrics resume reads as padded.

The person can say "skip", "keep", "cut" or "merge with e2-b1" at any time. Update the plan and move on.

## Writing rules (short version of references/bullets.md)

- One line where possible (about 110 characters), never more than two.
- Start with a strong verb: past tense for past roles, present for the current one.
- Put the result first when there is one: "Cut X by Y by doing Z".
- Name real tools and systems instead of "applications" or "solutions".
- Remove weak openers: "Helped", "Involved in", "Responsible for", "Worked on".

## After the bullets

1. **Summary**: if `summary.include` is `null`, first ask whether they want a summary on the resume at all. If not, set `include` to false and skip to the next step. Otherwise ask the summary questions, then propose a two-sentence rewrite (30–45 words) built from the strongest facts that are now in the bullets. Save it once they approve.
2. **Education and skills**: ask the education questions (e.g. certifications), and propose trims for the skills lines from the analysis notes. Apply them once they approve.
3. **Preview**: render a scored preview and open it:

   ```bash
   python3 <plugin-root>/scripts/render_tex.py ./<first-last>/review.json ./<first-last>/<First_Last>_Resume_scored.tex --scores
   <plugin-root>/scripts/build.sh ./<first-last>/<First_Last>_Resume_scored.tex --open
   ```

4. Give the final mix and average (before → after), then point to `/resume:build` for the final version.
