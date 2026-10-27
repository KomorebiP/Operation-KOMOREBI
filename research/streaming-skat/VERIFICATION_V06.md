# v0.6 Verification Summary

Date: 2026-09-23

## Formal results

- edge-additive leakage majorant: proved;
- polynomial edge-risk certificate: proved;
- query-invisible phase-pair corollary: proved;
- equal-cost cardinality-optimal pruning under the scalar additive certificate: proved;
- exact-envelope refinement: certificate preservation proved, global optimality not claimed;
- unequal-cost schedule: identified exactly as 0-1 knapsack under the additive certificate;
- ideal double-buffer timing and memory model: proved under perfect-overlap assumptions.

## Regression tests

- `test_streaming_skat.py`: 6/6 PASS;
- `test_formal_v02.py`: PASS;
- `test_approximate_lightcone.py`: 5/5 PASS;
- `test_budget_scheduler.py`: 4/4 PASS.

## Exhaustive scheduler audit

A six-phase problem has 15 candidate undirected phase pairs, hence 32768 subsets.
At budgets 0.004, 0.008, 0.012, and 0.020, the sorted-risk equal-cost scheduler
matched the brute-force optimum under the additive certificate in cardinality at
every budget.

The exact-envelope greedy refinement also matched the brute-force exact-envelope
optimum in cardinality at all four tested budgets. This latter agreement is
finite computational evidence only and is not promoted to a universal theorem.

## Twelve-phase scheduler audit

At Krylov depth 5, the 12-phase problem contains 66 undirected phase pairs.
For budgets 0.001, 0.002, 0.005, 0.010:

- additive-optimal retained pairs: 61, 56, 45, 36;
- exact-envelope-refined retained pairs: 58, 50, 36, 30;
- best global norm-threshold retained pairs: 65, 65, 65, 65.

Every reported schedule remained inside its stated certificate budget.

## Unequal-cost audit

With dense symmetric phase-block byte cost as a communication proxy:

- total proxy cost: 9472 bytes;
- greedy saved cost: 5408 bytes;
- additive risk used: 0.011632 under budget 0.012;
- exact transfer envelope: 0.006605;
- fractional relaxation upper bound: 5647.82 bytes;
- greedy gap to fractional upper bound: about 4.25%.

The greedy algorithm is certified feasible but is not claimed integer-knapsack optimal.

## Double-buffer model

The analytical model was checked against uniform block timings. Example:
64 blocks, 4 ms transfer, 4 ms compute gives

- single-buffer model: 512 ms;
- ideal double-buffer model: 260 ms;
- ideal speedup: 1.969x;
- modeled resident memory: 24 MiB single buffer vs 40 MiB double buffer.

These are scheduling-model outputs, not measured GPU timings.

## PDF

- manuscript pages: 32;
- LaTeX compilation successful;
- no undefined references;
- render inspection performed separately.
