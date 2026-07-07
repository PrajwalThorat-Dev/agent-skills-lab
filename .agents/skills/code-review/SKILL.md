---
name: code-review
description: Performs a structured, honest code review covering correctness, security, readability, and performance. Use when the user asks for a code review, feedback, or critique on a snippet, file, or PR, or asks "is this code good" / "what's wrong with this".
tags: code-quality, review, engineering
---

# Code Review Skill

## Tone
Give a direct, technically grounded assessment — the kind a competent senior
engineer would give in a real review, not a customer-service response. Point
out real strengths only where they're actually notable (e.g. a genuinely clean
abstraction, a well-handled edge case), and spend the majority of the review
on what needs to change. Avoid throwaway compliments that don't inform any
decision the author would make.

## Review process

Work through these steps in order. Don't skip ahead to a verdict before
completing the earlier steps — each one informs the next.

### Step 1: Understand context and intent
Before judging anything, figure out what the code is trying to do. Read
function/variable names, comments, and structure to infer the intended
behavior. If intent is unclear from the code alone, state your assumption
explicitly in the review rather than guessing silently.

### Step 2: Correctness
Check for logic errors, incorrect conditionals, off-by-one errors, unhandled
edge cases (empty input, null/None, boundary values), and whether the code
actually does what Step 1 determined it's supposed to do.

### Step 3: Security
Look for the obvious classes of issues: injection risks, unsanitized input,
hardcoded secrets/credentials, unsafe deserialization, missing auth/permission
checks, and unsafe use of eval/exec-like constructs. Only flag what's
genuinely relevant to the code shown — don't pad the review with generic
security disclaimers.

### Step 4: Readability & maintainability
Assess naming clarity, function/method length, nesting depth, duplication,
and whether someone unfamiliar with this code could maintain it six months
from now. Reference `references/severity-levels.md` to calibrate how serious
a given issue is before including it.

### Step 5: Performance
Only raise performance concerns if they're actually consequential for the
code's apparent context (e.g. an O(n²) loop over a large expected dataset).
Don't invent performance concerns for trivial or clearly small-scale code.

### Step 6: Verdict
Summarize findings grouped by severity (Critical / Major / Minor / Nitpick —
see `references/severity-levels.md` for definitions). End with a one-line
overall assessment: is this mergeable as-is, mergeable with changes, or does
it need rework.

## Output format
Format the final review using the structure in `assets/review-template.md`.

## Supporting resources
- `references/review-workflow.md` — full visual workflow diagram and
  explanation of how the six steps connect
- `references/severity-levels.md` — definitions for Critical/Major/Minor/Nitpick
  classification used in Steps 4 and 6
- `assets/review-template.md` — output template to fill in for the final review
- `scripts/static_check.py` — optional helper script that can be run against
  a file to surface objective signals (unused imports, basic complexity
  metrics) before or during Step 4

## Notes for the agent
This skill activates fully once selected — all six steps and referenced files
are relevant to producing a complete review. Read `references/severity-levels.md`
before finalizing Step 4 and Step 6 output, since severity language should be
consistent across reviews.