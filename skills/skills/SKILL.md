---
name: skills
description: Tailor the Skills section of a resume to a specific job description the person pastes, to the overall market of job descriptions for their target role, or both. Finds which keywords the resume already backs up, which are missing, and which are padding, then rewrites the skills lines in the employers' own terms. Only runs after the experience bullets have been improved with /resume:improve. Use when someone wants to tailor or improve their resume skills, match a job description, add ATS keywords, or check what skills employers ask for. Step 3 of /resume:analyse → /resume:improve → /resume:skills → /resume:summary → /resume:build.
---

# /resume:skills

Rewrite the Skills section so it matches what employers are asking for, using only skills the person actually has.

## Where things are

The plugin root is two directories above this skill's base directory.

- `./<first-last>/review.json`: see `references/review-schema.md` (`skills`, `skills_tailoring`, `progress`).
- `scripts/progress.py`: pipeline status and gating.

## 1. Gate: bullets first

The skills step comes after the bullets for a reason. The bullets are the evidence for each skill, and a skill the bullets don't back up is weak. The final bullets decide which skills the resume can honestly claim.

1. Ask the person: "Have you finished improving your experience bullets with `/resume:improve`?"
2. Whatever they answer, check with:

   ```bash
   python3 <plugin-root>/scripts/progress.py ./<first-last>/review.json --require skills
   ```

3. If it says BLOCKED (or they say they haven't finished), stop. Don't propose or write any skills changes. Tell them how many bullets are still pending (the script lists them) and to run `/resume:improve` first. Offer to start it now.
4. If they say they're done but the script disagrees, show the pending bullets. Offer two ways forward: finish them, or mark them keep or cut in `/resume:improve`. Don't skip the gate.

## 2. Choose the source

Ask which one they want (if `target.job_description` is already set, suggest it):
- **A specific job**: they paste the job description. Save it to `skills_tailoring.job_description`.
- **The overall market**: typical postings for their target role and level, and region if they have one.
- **Both**: the specific job first, with market keywords as a secondary check.

For the market option, find 6–10 current postings (last 60 days or so) for the same title, level and region. Use a web search tool or any installed research skill. If there's no web access, ask the person to paste 2–3 postings instead. Record each posting's title, company and URL in `skills_tailoring.market_sources`. Never present made-up postings as real.

## 3. Extract and compare

From the job description(s), pull out the skills and keywords: languages, frameworks, platforms, tools, methods and certifications. Mark each as required or nice-to-have, and count how many postings mention it (for the market). Merge synonyms (e.g. "AWS" and "Amazon Web Services"), but keep the employers' wording for display.

Then compare each keyword with the resume:

| Status | Meaning | Action |
|---|---|---|
| `evidenced` | In skills and shown in a bullet | Keep, and put it near the front |
| `listed_only` | In skills, but no bullet shows it | Keep if relevant; mention it's weak |
| `in_bullets_only` | A bullet shows it, but skills doesn't list it | Add it to skills |
| `missing` | The job wants it, and the resume has no trace | Ask the person (below) |
| `irrelevant` | On the resume, but no posting asks for it | Suggest cutting, if it's filler |

Save the table to `skills_tailoring.keywords`. Also save `coverage_before`: the share of required keywords that are `evidenced` or `listed_only`.

## 4. Ask about the gaps

For the `missing` keywords, ask quick yes/no questions, grouped in a single message: "Have you used Kubernetes at work or on a real project?" Add a skill only when they say yes. Never add a skill the person doesn't have, even if the job asks for it. If they say yes, note that no bullet shows it. They can go back to `/resume:improve` to work it into a bullet, but that's their choice.

## 5. Rewrite the Skills section

- 3–6 labelled lines (e.g. Languages, Frameworks, Cloud & DevOps, Data, or domain groups like Contact Center & CX).
- Order lines and items by relevance to the job: required and evidenced skills first.
- Use the job description's exact terms where they mean the same thing, which helps keyword screening.
- Cut filler: skills no posting asks for, very old tools, soft skills (these belong in bullets), and anything the person said they don't have.
- Keep each line to about two lines of text at most.

Show before and after side by side, plus `coverage_before` → `coverage_after`. Save once they approve: move the old list to `skills_tailoring.skills_before`, write the new `skills`, and set `skills_tailoring.mode`. Then mark the step done:

```bash
python3 <plugin-root>/scripts/progress.py ./<first-last>/review.json --mark skills
```

## 6. Next

Point to `/resume:summary`. The summary comes last because it's built from the final bullets and skills.
