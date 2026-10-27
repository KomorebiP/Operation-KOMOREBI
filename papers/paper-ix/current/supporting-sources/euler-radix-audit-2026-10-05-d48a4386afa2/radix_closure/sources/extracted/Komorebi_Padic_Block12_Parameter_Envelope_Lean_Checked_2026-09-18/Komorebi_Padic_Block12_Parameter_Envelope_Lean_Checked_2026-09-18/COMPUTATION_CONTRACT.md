# Computation contract

## Mathematical claims audited

The finite program audits:

- exact elimination of the search-bound radix depth;
- equality of the Block 11 and direct parameter envelopes;
- monotonicity of the envelope core in its cap;
- transport from `coarseK r h` to `r - 1`;
- concrete compiler totals lying below both envelopes.

## Arithmetic domain

Python arbitrary-precision integers with Lean-compatible totalized natural
subtraction, division by zero, and remainder by zero conventions.

## Pass and failure meaning

A pass supports the implementation over the stated finite range.  A mismatch
would indicate a theorem translation error, implementation bug, or valid finite
counterexample requiring analysis.  A timeout is inconclusive.

## Non-claim

No finite run establishes the universal theorem.  Universality comes from the
compiled Lean proof terms.
