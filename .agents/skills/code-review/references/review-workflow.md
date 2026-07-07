# Code Review Workflow

This document explains how the six review steps connect and depend on one
another. See the accompanying diagram: `references/workflow-diagram.svg`.

## Why the order matters

The steps are sequential, not a checklist to complete in any order. Each step
narrows or informs the next:

- **Step 1 (Context)** establishes what "correct" even means for this code.
  Skipping this leads to Step 2 judging the code against the wrong intent.
- **Step 2 (Correctness)** and **Step 3 (Security)** are both about whether
  the code is *safe to run*, not whether it's *pleasant to read*. These come
  before readability on purpose — a beautifully clean function that corrupts
  data is still a Critical finding, not a Minor one.
- **Step 4 (Readability)** only makes sense once you know the code works.
  Commenting on naming conventions in code that has a Critical bug is a waste
  of the review's attention — fix-worthy issues get surfaced first.
- **Step 5 (Performance)** is deliberately placed last among the analysis
  steps because it's the most context-dependent and easiest to over-apply.
  Performance concerns should never be raised in isolation from Steps 1–4.
- **Step 6 (Verdict)** is the synthesis step — nothing new is discovered
  here, findings from Steps 2–5 are simply organized by severity (see
  `references/severity-levels.md`) and reduced to a single actionable call.

## What "no skipping ahead" means in practice

If Step 2 surfaces a Critical bug, don't let that shortcut Steps 3–5 — the
review should still be thorough. "No skipping ahead" refers to not jumping to
a verdict prematurely, not to stopping analysis early once one issue is found.

## Diagram

The visual flow is captured in `workflow-diagram.svg`:

```
Step 1: Context & Intent
      ↓
Step 2: Correctness
      ↓
Step 3: Security
      ↓
Step 4: Readability & Maintainability   ← calibrated by severity-levels.md
      ↓
Step 5: Performance
      ↓
Step 6: Verdict                          ← groups findings by severity
      ↓
Final Review Output                      ← formatted via review-template.md
```

Each arrow represents "informs," not "replaces" — later steps build on
earlier findings rather than overwriting them.