# Root algorithm: focused review and cost correspondence

## Claim and verdict

**Verdict: proved as written**, for the positive-multiplier root procedure of monograph Theorem 6.1 and the exact executable interfaces described below.

For every Boolean prime selector `a`, rational `r`, finite natural-residue list `d`, and positive natural multiplier `m`, the finite solver succeeds exactly when the interpreted element `codedNormalValue a r d` has an `m`-root in its actual selector group. A successful result interprets to such a root at every prime. Rejection has a prime-divisor obstruction, and the certified solver actually returns the offending prime. Every original selector-group element admits the rational/list input representation. The finite correction has the printed support bound.

Reviewed main source: `RealizationBoundaries/RootAlgorithm.lean`.
SHA-256: `84d27324d149f6e220b45f8351073bd8e3879ed0b345863cf0f38bb20898b4bd`.
Clean compiler receipt: `verification/development/RootAlgorithm_009.json`.

The additional cost module proves a finite oracle-query and candidate-visit cost contract, with an executable traced implementation and an erasure theorem to the original solver. It does not claim a bit-complexity bound or verification of a separate Python/native implementation.

Cost source: `RealizationBoundaries/RootAlgorithmCost.lean`.
SHA-256: `b97d0193b659a738a011d7ed4063dcbba3823c2c47c967b8dd3685d3709a1f8c`.
Clean compiler receipt: `verification/development/RootAlgorithmCost_005.json`.

## Dependency graph

1. The existing ambient/preimage root theorem identifies solvability with vanishing at the prime divisors of positive `m`.
2. `finiteRootTest_exact` and `firstRootObstruction_none_iff` identify finite scans with that exact condition; positivity supplies the bound `p ≤ m`.
3. The rational division `t = r/m` makes the defect vanish away from the input correction support and denominator-prime set.
4. `rootCorrectionCode_exact` identifies the finite computed list with the correction at every prime, including primes outside the enumerated bound.
5. `finite_root_algorithm_correct` then proves the original infinite-coordinate root equation.
6. `finiteRootSolver_sound`/`complete` and the certified success/error theorems connect the actual returned data to this equation or obstruction.
7. `finiteCodeValue_represents` and `codedNormalValue_represents` bridge all actual finite-support and selector-group elements to solver inputs.
8. The cost module erases a counted execution to a traced execution, then to the original certified execution; original semantic correctness composes with this erasure.

No proof leaf depends back on the solver statement. The inherited ambient criterion and arithmetic facts are internal Lean dependencies, not conclusions inferred from the runtime examples.

## Obligation matrix

| Obligation | Result | Evidence |
|---|---|---|
| Exact group/domain and interpretation | Passed | `codedNormalValue_mem`; selector-group source/target retained |
| All actual normal forms represented | Passed | `finiteCodeValue_represents`, `codedNormalValue_represents` |
| Finite decision test equivalent to all exceptional coordinates | Passed | `finiteRootTest_exact`, `firstRootObstruction_none_iff` |
| Executable success is a root at every prime | Passed | `rootCorrectionCode_exact`, `finiteRootSolver_sound`, `certifiedRootSolver_ok` |
| Completeness for positive multipliers | Passed | `finiteRootSolver_complete` |
| Actual returned rejection certificate | Passed | `firstRootObstruction_spec`, `certifiedRootSolver_error` |
| Printed exact correction support | Passed | `finiteRootSolver_support_bound` |
| Finite correction loop/output bound | Passed | `rootCorrectionCode_length` |
| Trace erasure to original arithmetic program | Passed | `tracedRootCorrectionCode_erase`, `tracedFirstRootObstruction_erase`, `tracedCertifiedRootSolver_erase` |
| Explicit candidate counter | Passed | `countedFindRootTrace_step_bound`, `countedCertifiedRootSolver_step_bound` |
| Explicit oracle-request count | Passed | `countedCertifiedRootSolver_query_bound` |
| Native/VM instruction or bit-cost correspondence | Out of scope | No such claim; arbitrary-size arithmetic and primality/inversion costs are not unit-time bounds |
| A separate Python implementation | Out of scope | No Python extraction correspondence is asserted |

## Exact cost model

Write `B = rootCorrectionBound r d m = max d.length (r.den * (r/m).den + 1)`.

`tracedSelectorRead` is one explicit oracle operation and appends its queried prime. The traced correction evaluates both section residues from actual oracle reads, and its single-pass sequencing retains the computed values and concatenates those traces. The traced obstruction search queries only at prime divisors of the multiplier and short-circuits at the first obstruction. The counted search also records each candidate integer visited, including composite/nondivisor candidates that make no query.

The proved bounds are:

* correction oracle queries at most `2*B`;
* obstruction oracle queries at most `m+1`;
* total oracle queries at most `m+1+2*B`;
* total obstruction/correction candidate visits at most `m+1+B`.

The counted execution erases to the traced execution, which erases to `certifiedRootSolver`; on positive multipliers its successful branch satisfies the original ambient group equation. This is a precise oracle-operation semantics. It is not a claim that an optimizing compiler makes exactly that many function invocations or machine instructions.

## Boundary and normalization checks

The Option-valued `finiteRootSolver` rejects multiplier zero explicitly. The `certifiedRootSolver` success theorem has the public precondition `0 < m`; callers of that routine must retain it. The multiplier-zero boundary is not folded into the positive theorem.

The printed procedure sets the **correction** coordinate `e_p` to zero at primes dividing `m`. It need not set the entire root coordinate to zero, because the returned root is `s(r/m)+e`. It therefore need not equal the previously defined ambient `normalizedRoot`. For example, with every prime selected, `r=2`, empty correction, and `m=2`, the finite solver returns the section of `1`, whose prime-2 coordinate is `1`. This is the correct printed procedure, not a uniqueness failure.

Residue-list positions name prime **values**, with nonprime positions ignored. Input lists need not be sparse/canonical presentations, and residues are reduced by their `ZMod` casts. The coverage proof is existential for arbitrary abstract finite-support functions; the executable engine itself takes actual finite lists and an explicit oracle argument.

## Independent runtime checks

Main solver log: `verification/development/RootAlgorithm_independent_review_final.log` (exit 0, eight Boolean checks all true).

Checked cases:

1. A selected prime 2 obstructs division of the all-one section by 2.
2. The pure torsion element `e3` has the computed correction `2e3` as a 2-root.
3. The same `e3` has no 3-root.
4. The composite test `1+e2+2e3` has a 6-root with rational coordinate `1/6` and zero correction.
5. The Option solver excludes multiplier zero.
6. The certified failure branch actually returns prime 2.
7. The certified successful branch returns the expected torsion correction.
8. The correction-normalization example above returns the section of 1.

Cost runtime log: `verification/development/RootAlgorithmCost_runtime_tests.log` (exit 0).

| Execution | Oracle-prime trace | Candidate visits |
|---|---|---:|
| Selected-prime obstruction, m=2 | `[2]` | 3 |
| Pure torsion success, m=2 | `[2,2,2,3,3]` | 7 |
| Composite success, m=6 | `[2,3,2,2,3,3,5,5]` | 14 |

Each result agrees with the original certified solver. The examples test distinct branches and do not substitute for the universal Lean proofs.

Kernel replay of the final cost module passed: `verification/development/RootAlgorithmCost_kernel_replay.log`. Explicit axiom checks for the main completeness/representation/certificate theorems and cost erasure/bounds/soundness use only `propext`, `Classical.choice`, `Quot.sound`.

## Development failure and correction

An in-progress representation statement initially asserted surjectivity of finite residue lists onto all of `Ambient`. That statement is false for infinitely supported vectors. The review identified the codomain error before any accepted compilation, and the final source instead proves representation only for `finiteSupport`, followed by representation of actual selector-group normal forms. No ambient-surjectivity theorem is shipped.

Other failed development compilations were local proof implementation issues: simplifier unfolding of a successor-length `List.ofFn`, a conditional normalized to `True` requiring its explicit rewrite, and arithmetic goals requiring expansion of multiplication over a successor. They were corrected without weakening the final mathematical contracts.

## Review provenance and integration

The main solver received a separate-agent derivation, source review and runtime checks. The cost extension was implemented by that reviewing agent and therefore has self-review provenance; its formal proof still requires the coordinator's full audit and replay. Neither agent agreement nor runtime examples are treated as proof certificates.

For printed 6.1, the prior algorithm/support/extraction boundary is now closed by a genuine executable rational/list implementation, all-prime interpretation, complete success/rejection interface, returned certificate, representation coverage, and the explicit oracle/candidate cost model above. Retain the bit-cost/native/Python limitations rather than silently extending that completion claim.

Add `RootAlgorithmCost` after `RootAlgorithm` in the production module manifest and root import, then run the full clean release audit before promoting the registry or calling the whole project 1.0.
