# review.json

One file per person, at `./<first-last>/review.json`. `/resume:analyse` creates it, `/resume:improve` fills in answers and rewrites, `/resume:build` renders the final resume from it. Everything is plain text; the scripts escape LaTeX and HTML.

```jsonc
{
  "version": 1,
  "basics": {
    "name": "Jane Doe",
    "location": "London, UK",
    "phone": "+44 7000 000000",
    "email": "jane@example.com",
    "links": [{ "label": "linkedin.com/in/janedoe", "url": "https://linkedin.com/in/janedoe" }]
  },

  "target": {
    "rubric": "senior_software_engineer",      // folder name under rubrics/, or "custom"
    "position_title": "Senior Software Engineer position",
    "job_description": null,                    // pasted JD text if the person gave one
    "custom_rubric": null                       // same shape as rubrics/<key>/role.json when rubric = "custom"
  },

  "role_evaluation": {                          // hiring-agent style score against the rubric
    "scores": {
      "production_impact": { "score": 22, "max": 35, "evidence": "..." }
      // one entry per rubric category, keys exactly as in role.json
    },
    "bonus_points": { "total": 3, "breakdown": "..." },
    "deductions": { "total": 2, "reasons": "..." },
    "key_strengths": ["..."],                   // 1-5
    "areas_for_improvement": ["..."]            // 1-3
  },

  "summary": {
    "text": "current summary as written",
    "score": 5,                                 // 0-10, references/summary.md rubric
    "criteria": [
      { "name": "Title + years up front", "status": "pass", "note": "..." }   // pass | partial | fail
    ],
    "questions": ["..."],
    "answers": null,                            // filled by /resume:improve
    "rewrite": null,
    "new_score": null,
    "plan": "rewrite",                          // rewrite | keep | cut
    "include": null                             // does the person want a summary? true | false | null (not asked yet)
  },

  "experience": [
    {
      "role": "Senior Backend Engineer",
      "company": "Acme Payments",
      "location": "London, UK",
      "start": "Jan. 2023",
      "end": "Present",
      "bullets": [
        {
          "id": "e1-b1",                        // e<role index>-b<bullet index>, 1-based
          "text": "Design and develop payment APIs",
          "score": 3,
          "reason": "Task only: no scope, result or ownership.",
          "plan": "xyz",                        // xyz | strong | keep | merge | cut
          "merge_into": null,                   // bullet id, when plan = merge
          "questions": ["...", "..."],          // 2-5, empty when plan = keep or cut
          "answers": null,
          "rewrite": null,
          "new_score": null,
          "format": null                        // after rewrite: "xyz" or "strong"
        }
      ]
    }
  ],

  "skills": [{ "label": "Languages", "items": ["Java", "SQL"] }],
  "skills_review": { "score": 7, "notes": ["..."] },

  "education": [
    {
      "degree": "B.Sc. in Computer Science",
      "school": "University of Leeds",
      "location": "Leeds, UK",
      "start": "2015",
      "end": "2019",
      "score": 7,
      "notes": ["..."],
      "questions": [],
      "rewrite": null                           // improved degree line, if any
    }
  ],

  "extra_sections": [],                         // [{ "title": "Certifications", "items": ["AWS SAA (2024)"] }]

  "format_checks": [
    { "check": "2 pages or fewer", "status": "fail", "note": "Education spills onto page 3" }
  ],

  "top_fixes": ["...", "...", "..."],           // the 3 changes that would move the resume most, in order
  "analysed_on": "2026-09-23"
}
```

## Rules the scripts rely on

- Bullet ids are stable. Don't renumber after analysis; `/resume:improve` and `/resume:build` look bullets up by id.
- `plan: "merge"` means this bullet's facts move into `merge_into`; the merged text goes in the target bullet's `rewrite`, and this bullet is not rendered.
- `plan: "cut"` drops the bullet from the final resume.
- `rewrite` wins over `text` everywhere. A bullet with `plan: "keep"` renders `text` unchanged.
