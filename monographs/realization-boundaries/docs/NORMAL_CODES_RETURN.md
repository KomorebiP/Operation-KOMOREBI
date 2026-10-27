# Native normal-form oracle closure

Base checkpoint: `Realization_Boundaries_Lean_v0.6.0_Checked.zip`, SHA-256 `032f61f0e176f0f3abfeb3615b8936ebd9edb7c3f9a07b6b8ad25877ec7aef70`.
Owner: subgroup_spectrum agent. Production write scope: `RealizationBoundaries/ComputableNormalCodes.lean`.

## Exact result

`paired_oracle_copy_iff (a X : Nat → Bool)` proves

```
Nonempty (OracleGroupCopy X (pairedGroup a)) ↔ SelectorReducible a X
```

This is the exact unmarked oracle criterion, with `SelectorReducible` using Mathlib's native Turing reducibility and `OracleGroupCopy` using actual natural-number names bijective with the original ambient `pairedGroup a`. Addition is proved recursive in the actual membership oracle using `Nat.RecursiveIn`. Equality of names is ordinary natural equality. No arbitrary Lean definition is accepted as a computation without a recursive-semantics proof.

The lower direction is the previously checked positive-search/tail-signature argument from `ComputablePresentations.lean`. This file supplies the full upper direction through `pairedRawCodes` and `pairedOracleCopy`.

## Construction

1. `RationalCode` from `RationalComputability.lean` is a native primitive-codable triple of naturals representing a positive-minus-negative numerator over a positive denominator. Its native gcd normalization and total prime residue operations are proved to match the literal normalized rational and Rat-to-ZMod cast.
2. `NativeNormalCode = RationalCode × List Nat`. `nativeNormalValue` lands in the original paired-prime subgroup; `nativeNormalValue_surjective` covers every actual group element using the checked normal-form theorem and finite residue encoding.
3. `ResiduesEqual` is a bounded prime-coordinate test on two finite lists. `residuesEqual_iff` identifies it with equality of their infinite ambient finite-support vectors. `primrec_residuesEqual` proves its native primitive recursiveness.
4. `nativeNormalEqual_exact` combines rational equality and finite residue equality, using actual unique normal forms. The corresponding raw natural test is ordinary computable.
5. `pairedMask_exact` identifies the prime-counting/parity mask with the literal `pairedSelector`. `pairedMask_oracleComputable` obtains the mask from the supplied genuine reduction of a to X.
6. `normalAddCell_cast` proves every natural residue cell computes the original cocycle correction. `normalAddResidues_exact` proves the finite output list agrees at every prime of the actual infinite product. Its bound includes both input lengths and the denominator primes; no finite truncation replaces the ambient statement.
7. `residueLoop_oracleComputable` proves a parameterized finite loop whose cells can make actual oracle calls. `rawNormalAdd_oracleComputable` wires rational arithmetic, the selector mask, the cocycle cells, and the finite loop into native oracle recursion.
8. `OracleRawGroupCodes.toOracleGroupCopy` from `ComputableQuotientCodes.lean` turns these redundant natural codes into bijective natural names using actual computable equality, canonical least representatives, and terminating native searches. Neither a noncomputable naming equivalence nor its mere existence is used as the algorithm.

The construction proves existence uniformly from the supplied reduction. It does not claim a uniform algorithm for choosing an abstract isomorphism from an arbitrary unknown group copy. The lower unmarked reduction correctly hard-codes the finite exceptional prefix nonuniformly.

## Verified dependencies

* `RationalComputability.lean`: `a912908e18e654ef13c6a267b837480198183af843cb13b13f6b0e6c5ceec788`.
* `ComputableQuotientCodes.lean`: `1e476f875f0917cdcaf3292c399ddbb83b3dacca080c7cbd2c2faec57da32757`.
* `ComputablePresentations.lean`: `f51b96aa3871c4dde05879d132c861f7d8382f82fdcbcb53e7f2276cbb742219`.
* `RootAlgorithm.lean`: `84d27324d149f6e220b45f8351073bd8e3879ed0b345863cf0f38bb20898b4bd`.

Final source SHA-256: `7d25e320d78e74e3132643c864c43bf427f42fe6fd9d894f90a3691b950cd3c2`.

## Verification and incidents

* `scripts/check.py ComputableNormalCodes` final development receipt `_012.json`: exit 0, 2.87 seconds, warnings treated as errors, automatic implicit variables disabled.
* `verification/development/ComputableNormalCodes_replay.log`: leanchecker kernel replay exit 0.
* The finite arithmetic, full ambient correctness, and native primitive-recursion components compiled in earlier iterations before final wiring.
* Two final-wiring attempts encountered deterministic elaborator heartbeat exhaustion. Increasing the limit only exposed a definitional-equality expansion; adding an explicit intermediate type and using the exact product-encoding lemma fixed it. No mathematical claim was weakened. The final source requires no elevated heartbeat limit.
* One failing development source was edited while that failing compiler run was still finishing; only the final clean `_012` receipt and its matching source hash are accepted evidence. Earlier development output is not accepted release evidence.

## Native executable smoke checks

`/tmp/NormalCodesSmoke.lean` imported the final module and evaluated the actual native addition/equality functions. The returned tuple is normalized positive numerator, normalized negative numerator, normalized denominator, residue at 2, residue at 3.

| Case | Actual output | Expected |
|---|---|---|
| All selector bits false, one-half plus one-half | `(1,0,1,1,0)` | Rational one plus the selected 2-coordinate correction |
| All selector bits true, one-half plus one-half | `(1,0,1,0,0)` | Rational one, no 2-coordinate correction |
| One-half plus negative one-half | `(0,0,1,0,0)` | Zero |
| Twice the 2-torsion seed | `(0,0,1,0,0)` | Zero |
| Empty torsion list versus values only at nonprime indices 0 and 1 | Equality test `0` | Equal ambient vectors |
| Rational one-half versus redundant code two-fourths | Equality test `0` | Equal rationals |

Every smoke result matched its expected value; the compile process returned exit 0. These are examples in addition to the universal exact theorems, not substitutes for them.

## Coverage and remaining coordinator tasks

This closes the actual upper construction needed for 8.1 and the missing upper implication of 8.3. The existing marked lower decoder supplies 8.2. The coordinator should connect the self-oracle instance explicitly if desired and add the 8.4 Turing-degree/common-completion wrapper. Finite-domain copies do not change 8.3 because every pairedGroup is already proved infinite. No external peer-review claim is made.

## Additional exact minimization helper

At the computability agent's request, `OraclePartialMinimizationTraces.lean` supplies `oracle_partial_minimization_trace`: a native partial minimization returns y exactly when the values through y form a finite defined trace, every earlier output is nonzero, and output y is zero. It imposes no definedness beyond the successful bound. The proof uses the literal `Nat.mem_rfind` and `Part.mem_map_iff` contracts.

Source SHA-256: `0166b56a8768bb2539e97eb03f16e9b4f48748229f84e6ac04b33666000a168d`. Development compile `_003` and kernel replay both exit 0. This is a pure semantic lemma for the separate genuine recursive-enumeration trace bridge; it does not itself assert computability of an arbitrary test.

## Exact fixed-operation degree refinement

`CanonicalOperationDegree.lean` fixes `canonicalPairedCopy a := pairedOracleCopy a a (TuringReducible.refl _)` and its actual encoded operation `canonicalPairedAddition a`. The theorem `canonicalPairedAddition_oracle_iff` proves for every X that this fixed addition function is native X-oracle computable exactly when a is Turing reducible to X. Its forward implication reuses the identical naming, zero, and addition as an X-computable copy and applies the checked unmarked lower decoder. The reverse is genuine oracle substitution. This is an exact degree theorem for the fixed operation, beyond merely a least-degree theorem for an isomorphism type.

Source hash: `eadfa32bff8aebc76a5a051be569d3adda06df81728cb26418e0af3024d37c75`. Clean development compile `_002`, 2.21 seconds, and kernel replay exit 0. A proposed extra raw-code variant encountered elaborator expansion and was removed; the requested fixed canonical operation theorem itself compiled cleanly and was not weakened. `AdditionGraphDegree.lean`, owned by the computability agent, expresses the corresponding actual operation-graph Turing equivalence.

## Denominator-local memoized cocycle cells

`LocalCocycleQueries.lean` adds a separate optimized implementation without modifying the frozen normal-code algorithm:

* `localCocycleException` is the primitive predicate that the current natural coordinate is a prime divisor of the product of the two normalized rational denominators.
* `normalAddCellUsingBit` is an oracle-free arithmetic cell with one supplied Boolean bit. `localNormalAddCell` invokes the selector once only on the exceptional branch and otherwise uses the selector-free finite correction sum.
* `localNormalAddCell_same_prime_residue` proves equality with every actual prime residue emitted by the frozen normal-form arithmetic. `localNormalAddResidues_same` lifts this to the full finite correction, and `localNormalAdd_correct` proves the identical actual group addition.
* `localNormalAddCell_oracleComputable` and `localNormalAdd_loop_oracleComputable` certify the native oracle recursion of the optimized implementation.
* `recordedLocalCell` records the prime whose one selector bit is supplied; its query-count theorem is exactly zero or one according to the exceptional predicate. `localCocycleQuerySchedule` is the finite scan schedule. It is nodup, has length at most the correction bound, and its membership at the complete bound is exactly primality plus divisibility of the denominator product. Thus each exceptional prime is scanned once and all other primes require no selector bit.

This is a selector-query locality statement. It does not claim a bit-complexity bound or a query count for an arbitrary reduction of selector a to another oracle X; that reduction can itself make multiple X queries. Distinct exceptional primes in the same prime pair may use the same selector index, so this implementation memoizes within each prime cell, not globally across prime pairs.

Final source hash: `19ffae9ebdc6b887ba6f1ae008288a9e5e7dc7de9202a3af7c12cf2f2b87101e`. Clean development compile `_003`, 2.44 seconds, and kernel replay exit 0. Production sources are frozen after these hashes.
