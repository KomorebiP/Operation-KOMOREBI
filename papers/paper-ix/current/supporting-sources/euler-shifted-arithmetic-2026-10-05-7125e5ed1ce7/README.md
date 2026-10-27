# Euler shifted arithmetic checkpoint

**The actual-index nonvanishing target is still open.**

Start with [the focused continuation](shifted_obstruction/README.md), then
[the independent review](shifted_obstruction/review/INDEPENDENT_REVIEW.md).
The exact target, proved results, failed implications, and resumption inputs
are in `shifted_obstruction/RESEARCH_STATE.json`.

This package includes the immutable parent checkpoint in
`Euler_Arithmetic_Nonvanishing_Attempt_2026-10-05/`. The few inherited engine
files also present under `recovered/` are exact copies needed by the current
actual-packet checker. No parent proof or result has been changed.

The continuation proves the full regularized moment valuation laws, a uniform
transformed derivative valuation, and exact obstructions to the proposed
measure and derivative transfer arguments. The finite local arithmetic
certificate is explicit, but its nonzero remainder is not proved uniformly.
There is no actual singular Euler example in this package.

See `REPRODUCE.md` for current validation and replay commands. The current
sources use only Python's standard library. No Lean compilation was performed.
