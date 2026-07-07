# Code Review Output Template

Fill in this structure for every review. Omit a section entirely if it has
no findings — don't write "No issues found" filler under every heading.

---

## Context

Brief statement of what the code appears to be doing (from Step 1). One or
two sentences. Include any assumptions made if intent wasn't fully clear.

---

## Findings

Group findings by severity. Within each group, list findings as short,
specific bullets — file/function/line reference where possible, what the
issue is, and why it matters. No padding.

### Critical
- [Issue] — [why it matters]

### Major
- [Issue] — [why it matters]

### Minor
- [Issue] — [why it matters]

### Nitpick
- [Issue]

---

## Verdict

One line: **Mergeable as-is** / **Mergeable with changes** / **Needs rework**

One or two sentences justifying the call, referencing the most important
finding(s) driving it — not a restatement of everything above.

---

## Notes for the agent filling this template
- If a severity group has no findings, delete that heading rather than
  leaving it empty.
- The Verdict must be consistent with the highest severity found (see
  `references/severity-levels.md` — a single Critical finding means the
  verdict cannot be "Mergeable as-is").
- Keep the whole review scannable — a reader should be able to get the gist
  from the Verdict line alone, with Findings available for detail.