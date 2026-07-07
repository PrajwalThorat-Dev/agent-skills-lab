# Code Review Workflow (Maintainer Documentation)

This file is documentation for humans maintaining this skill. It is **not**
required reading during a normal review run — `SKILL.md` contains everything
the model needs to execute the process. This file just explains the design
reasoning behind the step order, for whoever edits this skill later.

See `workflow-diagram.svg` for the visual flow.

## Why this order

- **Context before everything** — Step 1 defines what "correct" means for
  this specific code. Every later step depends on this being right.
- **Safety before style** — Correctness and Security (Steps 2-3) come before
  Readability (Step 4) deliberately. A clean-looking function that corrupts
  data is still worse than an ugly function that works safely.
- **Performance last among analysis steps** — it's the most context-dependent
  and the easiest step to over-apply if raised too early or without the
  grounding from earlier steps.
- **Verdict is synthesis, not discovery** — Step 6 shouldn't surface anything
  new. It only organizes what Steps 2-5 already found.

## If you're modifying this skill

- Changing severity definitions? Edit `references/severity-levels.md` only —
  don't duplicate definitions here or in `SKILL.md`.
- Changing output structure? Edit `templates/review-template.md` only.
- Changing the steps themselves? Edit `SKILL.md`'s Review Process section —
  this file should be updated afterward to reflect *why*, not *what*.