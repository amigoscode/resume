# Scoring and rewriting experience bullets

## Contents
- The target: a mix, not a wall of metrics
- Scoring rubric (0–10)
- Step 1: Score every bullet in the CV
- Step 2: Interview, one bullet at a time
- Step 3: Rewrite
- Worked examples

## The target: a mix, not a wall of metrics

Google's XYZ format is: **Accomplished [X] as measured by [Y], by doing [Z].**

Use it for roughly 30–40% of bullets, the ones where the person has a real number or a clear result.
If every bullet has a percentage, a recruiter reads the resume as padded or made up.
The other bullets should still be strong, using the levers below instead of numbers.

Strength levers that need no numbers:
- **Scope**: for whom, how big, how many sites/teams/countries, which industry.
- **Ownership**: led, owned end to end, built from scratch, was the sole architect.
- **Specific tech**: name the actual tools (Cisco CVP, Spring Boot, Kafka), not "systems".
- **Outcome in words**: what it made possible ("let callers reset PINs without an agent").

Numbers must come from the person. Never invent, round up, or "estimate" a metric for them.
If they don't know a figure, write the strongest honest bullet without one.

## Scoring rubric (0–10)

| Score | What the bullet has |
|---|---|
| 0–2 | A duty or a vague claim. No scope, no tech, no result. "Helped teams achieve goals." |
| 3–4 | A clear task with specific tech **or** scope, but no result. "Design and develop IVR, CVP applications." |
| 5–6 | Task plus one strong element: a number, clear scope, ownership, or a stated outcome. |
| 7–8 | A clear result plus how it was done. Either a real metric, or strong scope + ownership + specific tech. |
| 9–10 | Full XYZ: meaningful result, real measure, specific method, relevant to the target role. |

Deduct a point for weak openers ("Helped", "Involved in", "Responsible for", "Worked on") when they hide what the person actually did.
Two bullets that are the X and the Z of one story (e.g. "Revamped IVR design" and "Reduced wait time by 90%") should be merged; say so when scoring.

## Step 1: Score every bullet in the CV

1. Prepend the score to each bullet in the `.tex` as `[N] -- ` so the person can see it in the PDF:
   `\resumeItem{[3] -- Design and develop IVR, CVP and contact center applications}`
2. Rebuild and open the PDF.
3. In chat, give the overall average, a per-role table (scores and average), the strongest and weakest bullets with a one-line reason each, and the 2–3 patterns pulling scores down (e.g. "current role is weakest, and it's what recruiters read first").
4. Do not rewrite yet. Ask if they want to start the interview.

## Step 2: Interview, one bullet at a time

Start with the first bullet of the most recent role and go in order, unless the person picks another.
For each bullet:

1. Quote it with its score and say in one line why it has that score.
2. Ask 3–5 short questions, grouped by what they unlock. Say rough answers are fine:
   - **Scope**: who was it for, how big, how many?
   - **Ownership**: led it, or part of a team?
   - **Tech / how (Z)**: what exactly was built, with which tools?
   - **Result (X/Y)**: what changed afterwards? Only ask for a number if one plausibly exists; offer "in words is fine too".
3. Show a draft shape with **[placeholders]**, not invented values, so they see where their answers go.
4. When they answer, write the bullet, give the new score, and move to the next bullet.

Keep each turn to one bullet so the person isn't buried in questions.

## Step 3: Rewrite

- Start with a strong past-tense verb (present tense for the current role): Architected, Built, Cut, Led, Migrated, Automated.
- One line where possible (about 110 characters at 11pt), never more than two.
- Put the result first when there is one: "Cut X by Y by doing Z" reads stronger than "Did Z, which cut X".
- Keep 3–6 bullets per recent role and 2–3 for older ones. Drop or merge the weakest to keep one page.
- Replace the old bullet in the `.tex`, keep the `[N] -- ` prefix with the new score while the review is ongoing, and rebuild.
- When all bullets are done, strip every `[N] -- ` prefix and do a final build.

## Worked examples

**Duty → strong without numbers (3 → 7)**
- Before: `[3] Design and develop IVR, CVP and contact center applications`
- After: `Architected and built Cisco CVP/UCCE IVR applications end to end for a national bank, adding bilingual self-service for balance and card requests`

**Split story → merged XYZ (5 + 7 → 9)**
- Before: `[5] Revamped IVR application design across 3 contact centers` and `[7] Helped reduce customer wait time by more than 90%`
- After: `Cut customer wait times by 90%+ across 3 contact centers by redesigning IVR call flows and routing`

**Vague → honest and concrete (1 → 6)**
- Before: `[1] Helped Business, Workforce and Analytics teams achieve higher goals`
- After: `Built the daily staffing and SLA reports the Workforce and Analytics teams used to plan agent shifts`
