# Severity Levels

Definitions for classifying findings during Step 4 (Readability &
Maintainability) and Step 6 (Verdict) of the code-review skill. Apply these
consistently across reviews.

---

## Critical
The code is broken, unsafe, or will cause real harm if merged as-is.

**Example:**
- **Evidence:** `def get_user(id): return db.query(f"SELECT * FROM users WHERE id={id}")`
- **Impact:** Directly interpolates user input into SQL — a classic injection vulnerability.
- **Recommendation:** Use parameterized queries (e.g. `db.query("SELECT * FROM users WHERE id=?", (id,))`).

**Impact on verdict:** Presence of even one Critical finding means the code
needs rework before it can be merged.

---

## Major
The code works for the common case but has a real problem worth fixing
before merging.

**Example:**
- **Evidence:** `def average(nums): return sum(nums) / len(nums)`
- **Impact:** Raises `ZeroDivisionError` if `nums` is empty; not handled anywhere upstream in the code shown.
- **Recommendation:** Add an explicit check for an empty list and decide the intended behavior (return 0, raise a clear error, etc.).

**Impact on verdict:** Presence of Major findings (without Critical ones)
generally means "mergeable with changes."

---

## Minor
A legitimate improvement, not something that blocks merging.

**Example:**
- **Evidence:** `def calc(x, y, z): ...`
- **Impact:** Parameter names give no indication of what they represent, making the function harder to use correctly without reading its body.
- **Recommendation:** Rename to something descriptive, e.g. `base, tax_rate, discount`.

**Impact on verdict:** Doesn't block merging. Can be noted as "nice to have."

---

## Nitpick
Purely stylistic or subjective. Mention briefly, never let it dominate the review.

**Example:**
- **Evidence:** Mixed use of single and double quotes across the file.
- **Note:** Inconsistent but not a functional issue; only worth a passing mention if a project style guide is otherwise implied.

**Impact on verdict:** No effect. Include at most a couple, only if genuinely
worth mentioning.

---

## Calibration rule
When in doubt between two adjacent levels, prefer the **lower** severity.
Over-flagging erodes trust in the review as much as under-flagging does.