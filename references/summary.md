# Scoring and rewriting the professional summary

The summary is written last (`/resume:summary`), after the bullets and skills, because it's built from them.

Based on the guidance at https://www.faangtechleads.com/resume/professional-summary, plus what worked in practice.

## What a good summary does

- **Sums up the background**: title and years of relevant experience in the first sentence.
- **Points out what's unique**: the person's biggest, most specific facts (scale, domain, flagship result). These usually already exist in the Experience section; pull the best one up.
- **Tailors to the role**: uses the target job's keywords and names real tools, which also helps keyword screening.
- **Explains an unusual situation** if there is one (career change, going back to hands-on work, a gap). This is the one place an objective belongs.

## What to avoid

- **Stating an objective** ("seeking a challenging role…"). The application already says what they want.
- **Too many specialties**. "Specializing in cloud, full stack, ML, big data and visualization" means no specialty. Pick the one or two the resume proves.
- **Claims the resume can't back up**. If the summary says "AI-powered", some bullet should show it.
- **Filler anyone could write**: "proven ability to exceed expectations", "passionate about", "team player", "results-driven".

The section is optional: always ask whether the person wants one (stored in `summary.include`). If the resume runs past 2 pages, a weak summary is the first thing to cut.

## Length

Two sentences, about 30–45 words. Sentence one: title, years, domain, concrete stack or scale. Sentence two: how they work or what they're best at, ideally with one result.

## Scoring (0–10)

| Criterion | Points |
|---|---|
| Title + years in the first sentence | 2 |
| At least one specific, unique fact (scale, domain, result) | 3 |
| Names real tools or domain keywords | 2 |
| Every claim is backed up by the resume | 1 |
| No filler or objective | 1 |
| 2 sentences, ≤ 45 words | 1 |

Present the score as a table (criterion, ✅/⚠️/❌, one-line reason), like the bullets review.

## Interview questions

Ask only what's missing:
1. What role are they targeting next? (tailoring and keywords)
2. Which one fact in the resume would they most want a recruiter to remember?
3. Any specialty they want to lead with, or any claim in the current summary they can't back up?
4. Anything unusual to explain (career change, relocation, returning to hands-on work)?

## Rewrite pattern

> **[Title]** with **[N]+ years** [building/designing] **[domain]** ([2–4 real tools]) across **[scale fact]**. [How they work / strength], most recently **[one result]**.

Use only facts from the CV or from the person's answers. Show the rewrite in chat and ask before putting it in the `.tex`.

## Example

Before (4/10):
> Results-driven Software Engineer with 8 years of experience in designing, developing, and delivering high-quality software solutions. Proven ability to work in fast-paced environments and exceed stakeholder expectations. Skilled in cloud, microservices, AI, big data, and DevOps, with a passion for clean code and continuous learning.

Why: title and years are there, but nothing is specific, it claims five specialties, and two sentences are filler.

After (about 40 words):
> Backend Engineer with 8 years building Java and Spring Boot payment services on AWS, handling 5K+ requests per second for 3M customers. Leads service design and on-call for the payments team, most recently cutting checkout latency by 60%.
