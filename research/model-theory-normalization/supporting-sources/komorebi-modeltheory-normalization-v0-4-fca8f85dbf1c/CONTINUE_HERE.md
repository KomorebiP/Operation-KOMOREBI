# Continue from Model-Theory Normalization v0.4

Authoritative successor of the exact v0.3 archive recorded in history. Read
NORMALIZED_CORE.md, FORMALIZATION_COVERAGE.md, RESULTS.md, PROOF_AUDIT.md and
DEVELOPMENT_FAILURES.md before changing source. Preserve the original ZIP.

## Closed in this block

- Actual FIFO discovery loop with complete-root/frontier invariant and terminal exactness.
- Prime-power module-length termination, o+k*r*d+1 fuel, at most r*d accepted rows,
  word horizons strictly below r*d, all degenerate natural-number cases.
- Concrete executable exact membership through finite coefficient enumeration.
- Actual matrices -> successful reference output -> complete logical test code ->
  Mathlib quantifier-free defining formula and definability.
- Oracle-independent literal outputs and certified complete queue-trace/reference equality.
- Four literal fast traces, including the 2^128-state synthetic fixture, kernel-checked
  without evaluating the expensive reference oracle at that scale.

## Current next target

Supply an efficient proof-producing membership backend or formally verify the
chain-ring Smith routine. Its skip witnesses must reconstruct raw accepted rows;
its acceptance witnesses must separate from every preceding row. The present
QueueTrace checker gives a safe bridge for untrusted fast proposals, but all 202
Python traces are not all newly emitted/checked Lean instances (four are).

A separate valuable target is intrinsic test-list/formula-cost optimization. Do
not identify number of accepted rows with minimum generator count or claim the
r*d upper bound is sharp for every system. Single-seed, relational and approximate
profiles require their own contracts.

All new generic proofs and selected traces compiled. The acceptance audit used
23 local modules and 30 tasks with exact hashes across synchronous batches.
Full parent Python replay passed; only 12 parent Lean dependencies were rebuilt.
No new full p-adic or all-202-generated-parent Lean replay is claimed.
