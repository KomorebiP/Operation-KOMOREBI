# Independent review: degree variation over a fixed computable finite-observation system

## Claim and verdict

**Verdict: proved as written. No defect found.**

Reviewed sources and SHA-256:

* `RealizationBoundaries/ComputableFiniteObservations.lean`: `7a061e5bda24c19a5c0a8b7aeaeabae741a1bed3ffa32766fc48f3950631afc2`.
* `RealizationBoundaries/DegreeVariation.lean`: `0d6da71763de722a51e323ff2293d0ab582225219ab4ab33170f9dbe9d4ce753`.

Clean compiler receipts are `ComputableFiniteObservations_009.json` and `DegreeVariation_003.json` in `verification/development`.

Every usual Turing degree of a set occurs as the least presentation degree of an actual countable paired-prime group. The group retains reducedness, residual finiteness and the actual common profinite completion. Its unmarked all-finite-quotient observation is represented by one fixed ordinary-computable inverse system, independent of the selector. The comparison is an actual natural isomorphism after categorically initial reindexing, not just agreement of quotient cardinalities.

## Native computation and table semantics

The stage modulus is the product of the first `n` actual primes. The source proves its positive, squarefree value and exact recursion. `computable_observationModulus` derives ordinary Mathlib `Computable` from the previously proved genuine computability of the literal production `primeAt` values and native recursion. It does not assume an oracle for prime products.

The stage-index arrow relation and equality of natural names have explicit ordinary computability theorems. The validity, addition, negation and restriction functions have only natural stage/residue inputs. None takes a selector, source group, dense-source inclusion, named source element or oracle. Their computability proofs use actual native arithmetic/composition after the modulus computation.

The residue domain is exactly `x < modulus(n)`. `observationNames` is a bijection from that finite native domain to the actual group `ZMod(modulus(n))`. The output-validity and semantic-specification theorems identify the native table algorithms with addition, negation and the actual quotient transition homomorphisms.

The subtraction in negation is protected by the residue bound, including stage zero. The empty prefix has modulus one, so it represents the trivial group and never introduces a zero-modulus exception. Every transition is in the inverse-system direction: an arrow from a larger stage to a smaller stage reduces modulo the smaller modulus. The source's functor laws prove exact identities and compositions.

These are genuine mathematical computability proofs in Mathlib's native recursion semantics. The final source additionally contains runnable companions: `observationPrimeProgram` performs actual terminating search through the decidable prime-index relation; `observationModulusProgram` uses ordinary recursion; and the four table programs use that executable modulus. Their equality theorems identify them with the semantic prime labels, stage product and table functions. The search's existence proof is erased at runtime, so the noncomputable mathematical `Nat.nth` does not occur in this executable path.

The independent VM checks in `DegreeObservation_executable_independent_review.log` passed. The first eight executable primes were `[2,3,5,7,11,13,17,19]`; the first six moduli were `[1,2,6,30,210,2310]`. At stage 3 (modulus 30), code 29 is valid and code 30 is invalid, `29+2` returns 1, and negating 1 returns 29. Restriction to stage 2 sends code 29 to 5 modulo 6. Negation at the trivial stage returns zero. The `false` output for validity of code 30 is the expected successful boundary check, not a test failure.

This certifies executable Lean VM programs and their exact mathematical correspondence, not a polynomial-time/bit-cost theorem or a separately packaged standalone binary.

## Cofinal comparison with all finite quotients

1. `observationPrimes_cofinal` puts every finite set of actual primes into a prefix. Its proof uses the exact prime-counting index and `Nat.nth_count`, not a separate enumeration.
2. `observationPrefixFunctor_initial` proves categorical initiality of this inverse-system reindexing. The direction agrees with the order-dual stage categories.
3. `observationCrtEquiv` is the actual CRT ring equivalence between each fixed cyclic stage and its corresponding finite prime-coordinate product. Distinctness/coprimality of actual primes is checked; the empty stage is retained.
4. `observationCrtEquiv_restriction` proves the coordinate-restriction square commutes for every stage transition.
5. `computableObservationIso` packages those maps into a natural isomorphism of finite-group diagrams.
6. The imported `coordinateIndexFunctor W` indexes the actual finite-coordinate kernels inside **all** finite-index normal additive subgroups of `preimage W`. `finiteCoordinateIndex_cofinal` proves every actual finite quotient is dominated by one of these kernels, using the checked finite-target annihilator/kernel theorem.
7. `computableObservationIndex_initial` composes the two initial functors. `computableObservationQuotientIso` identifies the complete quotient diagram restricted through that composite with the fixed computable diagram.
8. `allFiniteObservation_fixed_computable` supplies the exact `CommonCofinalObservation` witness: a common cofiltered stage category, two initial reindexings, and a natural isomorphism of their diagrams.

Thus no finite quotient is discarded without a proved cofinal comparison. The fixed observation contains no evaluations of named source elements; adding those would be a different, marked input contract.

The native table algorithms are uniform and selector-free. The abstract comparison with an arbitrary source quotient may depend on that source and quotient. No effective recovery of all quotient maps from an arbitrary source presentation is promised or needed for this theorem.

## Degree contract

`selectorTuringDegree` uses the official native `TuringDegree` carrier and the actual total binary membership oracle. `SetTuringDegree` denotes exactly its set-representable degrees, which are the ordinary degrees of sets used by the monograph. The source explicitly avoids claiming a separate totalization theorem for every partial-function representative admitted by the broader library carrier.

`HasLeastPresentationDegree` requires both attainment by an actual oracle-computable copy and the lower bound against every binary oracle admitting a copy. `paired_least_presentation_degree` derives both directions from the checked exact copy criterion, rather than only constructing an upper bound.

`every_set_degree_with_fixed_computable_observation` then chooses an actual selector of the supplied degree and retains countability, infinitude, residual finiteness, the actual canonical completion equivalence to the original ambient product, and the fixed computable observation comparison. Abelian structure is inherited from the actual ambient additive subgroup. The final theorem now explicitly includes `IsReducedAddGroup`. Its witness `paired_isReduced` invokes `paired_degree_reduced`, excluding embeddings from every nontrivial divisible additive group. It is not an additional condition on the degree or chosen selector.

## Obligation matrix

| Obligation | Result |
|---|---|
| Algorithms genuinely native-computable | Passed: explicit native recursion/arithmetic proofs |
| Algorithms independent of selector/source/oracle | Passed: exact signatures and dependency inspection |
| Valid finite table domains and actual group semantics | Passed: names, validity and specification theorems |
| Empty-prefix and negation boundary | Passed |
| Prefix cofinality | Passed |
| Actual CRT maps and all transition squares | Passed |
| Comparison to all finite quotient kernels | Passed |
| Genuine common initial reindexing, not a truncated observation | Passed |
| Least degree attained and lower-bounds every copy | Passed |
| Reduced/countable/residually finite/common-completion properties | Passed |
| Runnable prime/modulus/table programs and exact correspondence | Passed, including VM checks |
| Standalone binary packaging and bit-cost theorem | Out of scope |
| Source-marked observation or effective recovery of quotient maps | Out of scope |

## Verification and provenance

`verification/development/DegreeObservation_independent_review.log` checks the exact native table, naming, validity, transition, cofinality, CRT, degree and final fixed-system theorem interfaces. Explicit axiom inspection of all five computability theorems, the all-finite-quotient comparison and the final degree bundle reports only `propext`, `Classical.choice`, `Quot.sound`.

Independent kernel replays of the final sources passed in `ComputableFiniteObservations_final_independent_replay.log` and `DegreeVariation_final_independent_replay.log`. The earlier ancestor review/replay logs remain preserved; the final-source executable/interface checks are in `DegreeObservation_executable_independent_review.log`.

Review provenance: separate-agent inspection of the raw definitions and derivation, including the source `ObservationSystems.lean` interface and its actual all-quotient cofinality proof. No finite numerical test is substituted for these universal diagram/computability contracts.
