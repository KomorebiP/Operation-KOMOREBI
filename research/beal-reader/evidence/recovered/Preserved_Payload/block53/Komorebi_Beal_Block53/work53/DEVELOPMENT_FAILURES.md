# Failures, rejected shortcuts, and preserved boundaries

## Environment failure, recovered

The first attempt to start a streaming container session returned
StreamingExecNotEnabledContainerError before the command ran. A normal
subprocess launch then ran the Block52 verifier during this same interaction.
Its completion and report were observed: PASS_DECLARED_CHECKS. The initial
tool failure is not a failed mathematical check or a completed run.

## Mathematical shortcut failures, retained as controls

- Discarding natural upper-entry divisibility is false: at n=2, the nilpotent
  [[-7,1],[-49,7]] has diagonal valuation1, not2.
- Replacing the half-depth conclusion with full-depth triviality is false
  locally: [[-49,7],[-343,49]] at n=3 has diagonal valuation2, not3.
- Local trace identities without residual separation do not identify the
  two characters. The cyclic modulo 49 example lambda8,a15,d43 passes the
  trace/determinant identities on all powers but has the wrong diagonal.
- Characteristic-polynomial congruence at 13 is insufficient. The two matrices
  -13I and diag(169,1) have the same characteristic polynomial mod 49. Using
  this weaker datum instead of the actual scalar would not prove n!=2.

These controls falsify strengthened/under-hypothesized alternatives, not the
stated B53.1--B53.7 results. The original local n=3 sharpness family is retained
as local mathematics, not declared a realized global Frey representation.

## Uncompleted routes

No actual semilinear conjugation map was constructed. No restriction r inF7
or conjugation-stable ramification is asserted. No full global ray-group
calculation with all variable divisors was completed. The new theta_n
coordinate exposes that remaining calculation rather than pretending to do it.
No Lean installation or compilation was performed. No independent proof
reviewer was obtained. The detailed review is explicitly a self-review.

## Historical failures are unchanged

Block50's interrupted independent extension-geometry review remains
interrupted. Block52's defective orbit-representative equation filter remains
failed historical source, with its corrected per-member filter and independent
count replay preserved. This block performs no new point counts and does not
reuse the failed filter.

## Literature retrieval

An initial broad web search did not locate the desired precise source and
returned irrelevant results. Those were not cited as mathematical evidence.
Direct author-hosted Milne documents and exact pages supplied the source check.
