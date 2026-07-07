---
name: code-review
description: Performs a structured, honest code review covering correctness, security, readability, and performance. Use when the user asks for a code review, feedback, or critique on a snippet, file, or PR, or asks "is this code good" / "what's wrong with this".
version: 2.0.0
tags: code-quality, review, engineering
---

# Code Review Skill

## Tone
Give a direct, technically grounded assessment — the kind a competent senior
engineer would give in a real review, not a customer-service response. Point
out real strengths only where they're actually notable, and spend the
majority of the review on what needs to change.

## Do NOT
- Do NOT invent security issues that aren't actually present in the code shown.
- Do NOT mention performance unless it's meaningful at the code's realistic scale.
- Do NOT praise code just to soften the review — every positive statement
  must point to something specific and non-obvious.
- Do NOT recommend a rewrite or major refactor without justifying why the
  current approach is actually insufficient.
- Do NOT comment on style/formatting unless it genuinely affects readability
  (see `references/severity-levels.md` for what counts as Nitpick vs Minor).
- Do NOT produce a finding without evidence — see "Finding format" below.

## Review process
Perform these steps sequentially. Do not skip a step, and do not jump to a
verdict before completing all of them.

### Step 1: Context and intent
Infer what the code is trying to do from names, comments, and structure. If
intent is unclear, state your assumption explicitly rather than guessing
silently.

### Step 2: Correctness
Look for:
- off-by-one errors
- null/None/undefined handling
- empty collection handling
- incorrect conditionals
- race conditions on shared state
- mutation bugs (unintended side effects)
- resource leaks (unclosed files, connections, handles)

### Step 3: Security
Look for:
- injection risks (SQL, command, template)
- XSS / unsanitized output
- SSRF
- path traversal
- hardcoded secrets/credentials
- missing authentication/authorization checks
- unsafe eval/exec-like constructs

Only flag what's genuinely present — do not pad with generic disclaimers.

### Step 4: Readability and maintainability
Assess naming clarity, function length, nesting depth, and duplication.
Classify severity using `references/severity-levels.md`.

### Step 5: Performance
Only raise a concern if it's consequential given the code's apparent scale
(e.g. an O(n²) loop over data expected to be large). Do not invent concerns
for small or clearly trivial code.

### Step 6: Verdict
Group findings by severity (Critical / Major / Minor / Nitpick — definitions
in `references/severity-levels.md`). The verdict must be consistent with the
highest severity found: a single Critical finding means the code cannot be
"Mergeable as-is."

## Finding format
Every finding must include three parts:

- **Evidence** — the specific line, function, or pattern in question
- **Impact** — why it actually matters
- **Recommendation** — what to do about it

A finding without all three is incomplete. This is what prevents vague
statements like "naming could be better" from making it into a review.

## Optional static analysis
If `scripts/static_check.py` is available and relevant, it can be run against
the file being reviewed to surface objective signals (unused imports, long
functions, deep nesting) as supporting evidence for Step 4 findings — not as
a replacement for manual review.

## Output format
Use `templates/review-template.md` to structure the final output.

## Supporting files (read only when needed)
- `references/severity-levels.md` — read before finalizing Step 4 and Step 6,
  needed to classify findings consistently
- `templates/review-template.md` — read when producing final output
- `references/review-workflow.md` — maintainer documentation only; not
  required reading during a normal review