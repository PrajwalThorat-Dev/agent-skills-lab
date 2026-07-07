# Severity Levels

This document defines the four severity levels used when classifying findings
during Step 4 (Readability & Maintainability) and Step 6 (Verdict) of the
code-review skill. Apply these consistently — the same class of issue should
get the same severity label across different reviews.

---

## Critical
The code is broken, unsafe, or will cause real harm if merged as-is.

Examples:
- A logic bug that produces incorrect output for common/expected inputs
- A security vulnerability (injection, hardcoded credentials, missing auth check)
- Data loss or corruption risk
- Code that will crash or throw unhandled exceptions in normal usage paths

**Impact on verdict:** Presence of even one Critical finding means the code
needs rework before it can be merged.

---

## Major
The code works for the common case but has a real, non-trivial problem that
should be fixed before merging — not urgent enough to block everything, but
not safe to ignore either.

Examples:
- An edge case is unhandled (empty input, null, boundary value) but isn't
  likely to occur in the immediate use case
- A performance issue that will matter at realistic scale, even if not today
- Meaningful code duplication that will cause maintenance drift
- A misleading name or structure that could cause a future bug

**Impact on verdict:** Presence of Major findings (without Critical ones)
generally means "mergeable with changes."

---

## Minor
A legitimate improvement, but not something that blocks merging. Fixing it
makes the code better; not fixing it doesn't put anything at risk.

Examples:
- Inconsistent naming conventions
- A function that's a bit long but still readable
- Missing a docstring/comment where one would help but isn't essential
- Slightly redundant logic that isn't causing any real problem

**Impact on verdict:** Doesn't block merging on its own. Can be noted as
"nice to have" or left for a follow-up.

---

## Nitpick
Purely stylistic, subjective, or a matter of personal preference. Worth
mentioning briefly, but should never dominate the review.

Examples:
- Preferring one valid formatting style over another
- Variable name is fine but a different name might be marginally clearer
- Whitespace/spacing preferences not enforced by the project's linter

**Impact on verdict:** No effect. Include at most a couple of these, only if
genuinely worth mentioning — don't pad the review with nitpicks to seem
thorough.

---

## Calibration rule
When in doubt between two adjacent levels, prefer the **lower** severity.
Over-flagging erodes trust in the review; a reviewer who calls everything
"Critical" is as unhelpful as one who calls nothing anything at all.how