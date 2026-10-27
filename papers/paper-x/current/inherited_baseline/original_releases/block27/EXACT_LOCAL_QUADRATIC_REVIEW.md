# Independent review of the Block 22 finite local quadratic audit

**Verdict: implementation and finite assertions verified in the stated range.** The reviewer read the complete source, contract, original audit report, and execution manifest, and independently reran the unchanged program. The replay reproduced the scientific result byte for byte. No implementation, contract, serialization, or resource-limit failure was found.

The program was written by the separate `local_computation` agent. This review was performed by `local_inventory`, which did not modify that program or its contract. The computation-audit skill and its implementation checklist were applied. This is a review of the finite computation; the reviewer's other Lean work is not used to authenticate the computation's interpretation.

## Reviewed assertion and domains

The arithmetic variable solves `y^2 = -1` in `Z/(p^m)`, at all 15 primes from 2 through 47 and every depth with `p^m <= 100000`, including depth zero. The coefficient variable solves `x^2 = +1` and describes the generator image of a unit-valued character of `C2`. Its separate ranges are powers of two through depth eight and powers of three through depth five. The code and reports preserve this distinction throughout.

All arithmetic uses exact Python integers and remainder operations. There are no floating-point comparisons, tolerances, external numerical packages, caches, random sampling, or parallel reductions. Python's unbounded integer arithmetic avoids overflow in the squared residues. The zero-ring convention at modulus one is consistent: its unique element is its identity and is a unit, reflected by `gcd(0,1) = 1`.

The local map `C2 -> C2` is deliberately assigned to be zero at arithmetic primes congruent to one modulo four and the identity otherwise. Its homomorphism laws and the consequences for coefficient characters are checked. This assignment is not independently inferred from an executed Galois group. Its arithmetic meaning is a separate Lean/mathematical obligation, and both the contract and original audit explicitly say so.

## Implementation checks

- Prime enumeration uses trial division and is checked against the explicit complete prime list. The proposed splitting criterion is not used to enumerate primes or construct root candidates.
- Arithmetic root enumeration scans every residue. Full consecutive lift fibers are independently reconstructed as `parent + digit * modulus`, with every digit tested. The resulting fibers are compared with the scanned high roots and their union is checked to exhaust the high root set. No branch or fiber is silently discarded.
- The root-count criterion is only an expected assertion checked against exhaustive enumeration. It is not a root-construction shortcut.
- Coefficient polynomial roots and characters use different code paths. The character path independently checks invertibility, the identity value, and all four `C2` multiplication pairs. Characters and direct polynomial roots then agree exactly.
- Every coefficient level pair with `high >= low`, including identities and depth zero, is included in the reduction loop. For every character and every arithmetic prime, both group values are checked for restriction/reduction naturality. The tested descent implication has its correct one-way direction.
- Boundary guards distinguish the arithmetic obstruction `y^2 = -1` modulo two/four from the coefficient behavior `x^2 = +1` modulo two/four. They also check the coefficient character `3 mod 8` has no character lift modulo sixteen.
- Stable iteration order and sorted JSON serialization make the result deterministic in the recorded interpreter. The source SHA-256 is embedded in the output. The replay manifest verifies unchanged input hashes and declared-result completeness.

Independent output checks confirmed the hand-computable root lists modulo 25, 169, and 9 are respectively `[7,18]`, `[70,99]`, and `[]`. Totals of scanned moduli and recorded roots were recomputed from the emitted level data and agree with the summary counters. Every terminal modulus satisfies `p^m <= 100000 < p^(m+1)`.

The terminal arithmetic depths are:

| Prime | Maximum depth |
|---|---:|
| 2 | 16 |
| 3 | 10 |
| 5 | 7 |
| 7 | 5 |
| 11, 13, 17 | 4 |
| 19, 23, 29, 31, 37, 41, 43 | 3 |
| 47 | 2 |

## Replay evidence

The unchanged command was rerun from the project root:

```sh
python3 checks/exact_local_quadratic.py --output checks/local_quadratic_review/results.json
```

The computation-audit bounded runner recorded that command in `checks/local_quadratic_review/manifest.json`, with the original `exact_local_quadratic_contract.json`. The v2 manifest validated against the current project input and output hashes.

- CPython standard library: `3.12.13`.
- Replay runtime: `0.11623` seconds. Exit code: zero.
- Wall limit: 30 seconds. Per-process address-space limit: 512 MiB. Per-process CPU limit: 20 seconds. CPU affinity: one core. Cooperative thread cap: one.
- Scientific output: `checks/local_quadratic_review/results.json`, byte-identical to `exact_local_quadratic.json` and the original bounded-run result.
- Source SHA-256: `a0067c572a23785dc30ee496706b963a5127f92b50e7e67b1e974d3ccbae5bab`.
- Scientific result SHA-256: `c37ffd85faaa61bf22ecee0a75e474433ad016e0ef6c41cf516e927b1efad798`.
- The project has no available Git commit. Exact source hashes supply the recorded revision identity.

The reproduced counts include 88 arithmetic levels, 755,060 arithmetic residue candidates, 52 full root-lift fibers, 998 lift-digit candidates, 39 coefficient root/character matches, 585 local model restrictions, and 6,180 coefficient/local naturality values. All counts agree with the original audit report.

## Limits and interpretation

The exhaustive scans and alternative finite constructions establish the asserted results only for the displayed finite rings. They do not establish an infinite compatible branch, a p-adic root theorem, the prime-congruence criterion for all primes, actual local Galois images, or inertia compatibility. In particular, neither the assigned finite `C2` map nor the observed distinct residues constitutes an implementation of an absolute Galois group or its inertia subgroup.

No Hodge–Tate, Weil–Deligne, or full arithmetic completion claim is proved by this computation. The full five-partial ledger must not change on the strength of this finite result. The structurally useful features are the separate arithmetic/coefficient roles, the exceptional arithmetic prime two, and the exact lift/reduction mechanisms. No larger range is needed to resolve a remaining implementation concern identified in this review.

Residual provenance limits are explicit: the standard-library implementation is trusted as recorded, the thread cap is cooperative, and the CPU-time bound is per process rather than an aggregate descendant bound. They do not affect the completed deterministic, single-process run. No requested range was truncated by a resource bound.
