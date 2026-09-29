#!/usr/bin/env python3
"""Show where a review is in the pipeline, and gate a step on the ones before it.

    python3 progress.py review.json                    # print status
    python3 progress.py review.json --require bullets  # exit 1 unless bullets are done
    python3 progress.py review.json --require skills   # needs bullets + skills
    python3 progress.py review.json --mark bullets     # record a step as done

Order: bullets (/resume:improve) -> skills (/resume:skills) -> summary (/resume:summary).
Bullets count as done when every bullet planned "xyz" or "strong" has a rewrite
(or was switched to keep/merge/cut) and progress.bullets_done is true.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ORDER = ["bullets", "skills", "summary"]
COMMAND = {"bullets": "/resume:improve", "skills": "/resume:skills", "summary": "/resume:summary"}


def pending_bullets(r: dict) -> list[str]:
    return [
        f"{b['id']}: {b['text']}"
        for role in r.get("experience", [])
        for b in role.get("bullets", [])
        if b.get("plan") in ("xyz", "strong") and not b.get("rewrite")
    ]


def status(r: dict) -> dict:
    p = r.get("progress") or {}
    pend = pending_bullets(r)
    summary_off = (r.get("summary") or {}).get("include") is False
    return {
        "bullets": (not pend and bool(p.get("bullets_done")), pend),
        "skills": (bool(p.get("skills_done")), []),
        "summary": (summary_off or bool(p.get("summary_done")), ["summary left off by choice"] if summary_off else []),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("review", type=Path)
    ap.add_argument("--require", choices=ORDER)
    ap.add_argument("--mark", choices=ORDER)
    args = ap.parse_args()

    r = json.loads(args.review.read_text())

    if args.mark:
        if args.mark == "bullets" and pending_bullets(r):
            sys.exit(f"Can't mark bullets done: {len(pending_bullets(r))} still need a rewrite.")
        r.setdefault("progress", {})[f"{args.mark}_done"] = True
        args.review.write_text(json.dumps(r, indent=2, ensure_ascii=False) + "\n")
        print(f"marked {args.mark} done")
        return

    st = status(r)
    for step in ORDER:
        done, notes = st[step]
        print(f"{'✓' if done else '·'} {step:<8} {COMMAND[step]}")
        for n in notes[:12]:
            print(f"    {n}")
        if len(notes) > 12:
            print(f"    ... and {len(notes) - 12} more")

    if args.require:
        needed = ORDER[: ORDER.index(args.require)]
        missing = [s for s in needed if not st[s][0]]
        if missing:
            first = missing[0]
            print(f"\nBLOCKED: {args.require} comes after {', '.join(missing)}. Finish {COMMAND[first]} first.")
            sys.exit(1)
        print(f"\nOK to run {COMMAND[args.require]}.")


if __name__ == "__main__":
    main()
