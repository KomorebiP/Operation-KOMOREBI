# Independent review of native oracle presentations and canonical names

Reviewer: `/root/reachability`, independent of the two reviewed modules' author.
Review scope: raw codes to an actual Nat-domain group copy; native relative recursion; marked and unmarked decoding; completeness of the group-operation contract.

## Pinned reviewed inputs

- `RealizationBoundaries/ComputablePresentations.lean`: SHA-256 `f51b96aa3871c4dde05879d132c861f7d8382f82fdcbcb53e7f2276cbb742219`.
- `RealizationBoundaries/ComputableQuotientCodes.lean`: SHA-256 `1e476f875f0917cdcaf3292c399ddbb83b3dacca080c7cbd2c2faec57da32757`.

The author confirmed these two source states were frozen. The reviewer re-read their actual definitions and proofs and rechecked the hashes after producing the dependent inverse module. Neither reviewed source was edited by the reviewer.

## Verdict and exact limits

No semantic defect was found in the reviewed raw-to-copy construction or native oracle APIs. The Nat naming is proved bijective. Native computability is derived in Mathlib's actual oracle-recursion semantics. The copy's native addition and equality have their actual group interpretation; desired computability of canonical names is not supplied as an assumption.

The raw-code theorem is correctly conditional: a concrete `OracleRawGroupCodes` must still supply genuinely computable raw addition and semantic equality. It does not by itself prove the upper direction for the selector groups. The concrete normal-code module must discharge those fields. The raw-to-Nat-copy theorem also explicitly assumes `Infinite H`; finite groups require the separate finite-domain convention and are not covered by an impossible bijection with Nat.

## Reconstruction of the critical raw-to-copy argument

1. Raw codes `c.names : Nat → H` are only assumed surjective, with actual `zero_spec`, `add_spec`, and `equal_spec`. The equality test returns zero exactly for equality of actual meanings. Its native relative computability is an explicit input, stronger than enumerable relators.
2. `Canonical n` means there is no smaller code with the same actual meaning. Natural well-ordering gives a canonical representative for each element, and two canonical representatives of equal meanings are equal.
3. `previousProduct q n` multiplies the actual zero-equality tests for all prior codes. Its nonzero criterion is proved by finite induction. Therefore `canonicalTest` is a genuinely effective finite equality test, even though an unrelated `DecidablePred Canonical` is supplied classically for mathematical convenience.
4. The classical canonical predicate is not silently used as an oracle. `canonicalTest_computable` is instead derived from the input equality algorithm and native primitive recursion. Its zero set is proved to be exactly the canonical codes.
5. Infinite `H` forces infinitely many canonical codes. `nth_zero_computable` does not tag the mathematical `Nat.nth` as computable by definition: it computes finite zero counts, computes the test for a successful candidate with exactly the requested number of successful predecessors, proves termination, and identifies the resulting native minimization with `Nat.nth` by `Nat.nth_count`.
6. `enumNames_injective` uses uniqueness of canonical representatives and injectivity of the increasing nth enumeration. `enumNames_surjective` uses the canonical representative and its finite predecessor count. Thus `namesEquiv : Nat ≃ H` has both inverse laws from proved bijectivity.
7. Converting a raw output back to a canonical index uses a second genuine search: compare each computed canonical name with the raw output using the input equality algorithm. Surjectivity proves termination. `index_spec` identifies the computed answer with the actual desired element.
8. The copy's addition computes raw addition of canonical representatives and then this computed canonical index. Its correctness is exactly `index_spec` followed by raw `add_spec`. It never assumes that the mathematical inverse `namesEquiv.symm` is computable.

## Native relative semantics and the lower oracle criterion

`OracleComputable X f` is the native `Nat.RecursiveIn` predicate for the total function `Part.some ∘ f`, with the sole oracle `selectorOracle X`. Composition, pairing, primitive recursion and minimization are derived from its constructors. Total minimization always has a separate successful-candidate existence proof. Equality-based congruences only replace extensionally equal total functions; they do not introduce computation assumptions.

`OracleGroupCopy.names` is a bijection onto the actual group. Equality on its domain is ordinary Nat equality, so the naming theorem identifies that decidable equality with actual group equality. Zero is a finite constant. Repeated addition is derived by native primitive recursion, and the prime inputs use the separately proved native computation of the actual `primeAt` values.

The root tests only test a finite candidate equation. They never decide a negative existential root condition. The paired positive search halts because one of the two mutually complementary roots exists; its correctness follows from the exact root equivalences. Using the same enumerated candidate parameter for the two tests is valid: a successful candidate on either side makes their product zero, and the complementary root theorem prevents a false successful side.

The marked result uses a supplied natural name for the marker. The unmarked reducibility result existentially fixes one finite natural name obtained from the mathematical bijection. This is the legitimate nonuniform finite-constant step in Turing reducibility. It does not compute the marker uniformly from an unmarked diagram and does not hard-code its infinite coordinates. The finite-prefix reduction similarly hard-codes only finitely many bits and explicitly makes no uniform prefix-discovery claim.

## Explicit completion of the operation contract

The reviewed `OracleGroupCopy` stores native addition and a zero name, with no stored inverse algorithm. This is mathematically sufficient for computable group inversion on a bijectively named Nat domain, but the reviewer supplied the missing explicit derivation in a separate module:

`RealizationBoundaries/OracleCopyOperations.lean`, SHA-256 `d6db70a3a1f076b71865a647a8406c18249cc545a8fdd80bcf5fa0779b4ddf1d`.

- `inverseTest` is the native finite test `add n t = zero`.
- `inverseTest_total` uses the actual inverse in `H` and surjectivity of `names` only to prove the search terminates.
- `inverse := Nat.find ...` is the resulting actual algorithm.
- `inverse_computable` follows from native oracle minimization.
- `inverse_spec` proves `names (inverse n) = -names n`.
- Both inverse cancellation laws, involution, and the zero inverse are proved from the actual naming equations.
- `subtract` and `subtract_computable` supply native subtraction with literal subtraction semantics.
- `zero_computable` and `names_equal_iff` state the other operation-contract components explicitly.

No inverse-computability assumption was added to the copy definition.

## Checks and review provenance

- `verification/development/OracleCopyOperations_002.json`: final new module compiler exit 0, warnings as errors, autoImplicit false, 2.25 seconds, exact source hash above.
- `verification/development/OracleCopyOperations_replay.log`: kernel replay exit 0.
- `verification/development/OracleCopyOperations_contract.log`: exact type and allowed-axiom checks exit 0, including `OracleRawGroupCodes.toOracleGroupCopy`.
- The checked headline results depend only on `propext`, `Classical.choice`, `Quot.sound`.
- Development compile 001 failed on a pairing simplification in the subtraction computation proof; corrected by the explicit extensional equality proof in 002.

This is independent source-level mathematical review plus native checks of the added dependent module. It is not an independently implemented kernel or external peer review. The coordinator's package-wide clean build/audit/replay remains the integration gate.
