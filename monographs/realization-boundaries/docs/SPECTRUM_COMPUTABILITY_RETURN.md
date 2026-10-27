# Spectrum computability and presentation return

Base: checked Realization Boundaries Lean v0.6.0. Owner: structural agent, with separate assigned write scope `SpectrumComputability.lean`, `DirectSumPresentation.lean`, and this note. The original publication is unchanged.

## Exact accepted candidate results

- `oracle_any_spectrum_copy_implies_enumerable` proves the lower direction of 3.3 for both finite and infinite coded domains. Finite copies have an actual Fin n domain, equality by names, and a natively computable addition table. Infinite copies use the preceding agent's native Nat-domain oracle copy. `HasOracleGroupCopy` is the explicit finite-or-infinite convention.
- `diagonalHalting_complement_not_enumerable` proves that the complement of the actual diagonal self-input halting set is not native computably enumerable. It extracts a real program code for the hypothetical semidecider and applies its own domain equivalence to that code.
- `haltingPrimeSpectrum_not_enumerable`, `haltingSpectrum_no_any_computable_copy`, and the retained-even-coordinate injection establish the actual infinite group H in 3.4 and its absence of a computable copy, under the broad finite-or-infinite convention. This is not a vacuous finite-domain exclusion.
- `haltingRelatorIndexStage` is a native primitive-recursive Option Nat emitter using Mathlib's bounded universal evaluator. Its outputs denote exactly the actual odd primeSeed relators for halting program indices.
- `haltingRelatorQuotientEquiv` identifies the actual quotient D / closure(extra relators) with the actual subgroup H. This uses the literal coordinate projection and its literal kernel, not just isomorphism invariants.
- `finiteSupport_prime_order_presentation` proves the universal presentation of the actual D by commuting prime-order generators. It constructs the universal map through the actual dependent direct sum and ZMod's universal map, and uniqueness follows from the checked finite primeSeed decomposition.
- `haltingGroup_prime_order_presentation` proves the full universal generators-and-relators property for the actual H, including the standard relations and the extra odd-halting relations. Thus there is no unproved standard-D presentation assumption.
- `computable_primeOrderRelatorLabel` is the native computable standard relator label list, paired with the natively enumerable extra relation list above.

Together, the two modules close the exact no-copy and effective-presentation assertions of **3.4**. The abelian presentation category encodes commutativity as part of the target structure (AddCommGroup), and the universal property fixes all remaining relations. The countable prime indexing is actual and surjective.

## Scope still delegated

The upper direction of **3.3** is being implemented separately by the categorical agent in `SearchEnumerableSpectrum.lean`. It is not claimed by these files. The new finite-domain convention is available for its finite branch. Native enumeration in these files uses the computability agent's `OracleEnumerable`, i.e. the domain of a genuine function in Mathlib's oracle-recursion semantics.

## Compiler receipts

```json
{
  "SpectrumComputability": {
    "receipt": "verification/development/SpectrumComputability_010.json",
    "exit": 0,
    "hash": "5e4f5dbc2b2e3e692c2a94c9cd15a787b5bc8bfebfa7fa8018c1cea8b4464982",
    "seconds": 3.070422887802124
  },
  "DirectSumPresentation": {
    "receipt": "verification/development/DirectSumPresentation_004.json",
    "exit": 0,
    "hash": "9fa911e44728f8e5dd226ba0fc09f74e6506b398aaf2d4acfc4666793aecd667",
    "seconds": 3.978531837463379
  }
}
```

These are clean development compiles with warnings treated as errors and autoImplicit false. Earlier failures are preserved in development receipts. They were API/namespace/cast/transparency issues and were corrected without admits. Root must run integrated audits, kernel replay, positive contracts, and rejection controls before accepting the candidate checkpoint.

## SHA-256

```json
{
  "RealizationBoundaries/SpectrumComputability.lean": "5e4f5dbc2b2e3e692c2a94c9cd15a787b5bc8bfebfa7fa8018c1cea8b4464982",
  "RealizationBoundaries/DirectSumPresentation.lean": "9fa911e44728f8e5dd226ba0fc09f74e6506b398aaf2d4acfc4666793aecd667",
  "RealizationBoundaries/ComputablePresentations.lean": "f51b96aa3871c4dde05879d132c861f7d8382f82fdcbcb53e7f2276cbb742219",
  "RealizationBoundaries/PrimeComputability.lean": "55bc437c950eafb805b8ad812d00250f268d3f95ad3d42336b30f430ff379511",
  "RealizationBoundaries/SubgroupSpectrum.lean": "cc4356c4a4f9b8ed1054e39b72fb62c822c6602c4703e3444c4dd4649ca53f69"
}
```

## SpectrumComputability declarations

- `diagonalHalting`
- `oracleEnumerable_computable_preimage`
- `recursiveIn_empty_selector_partrec`
- `diagonalHalting_complement_not_enumerable`
- `haltingIndexSpectrum`
- `haltingPrimeSpectrum`
- `haltingPrimeSpectrum_not_enumerable`
- `haltingSpectrum_no_computable_copy`
- `primeAt_surjective`
- `haltingSpectrumEvenSeed`
- `haltingSpectrumEvenSeed_injective`
- `diagonalHalting_re`
- `killedHaltingPrimes`
- `haltingPrimeSpectrum_complement`
- `spectrumProjection`
- `spectrumProjection_surjective`
- `spectrumProjection_ker`
- `spectrumQuotientEquiv`
- `spectrumSubgroup_eq_seedClosure`
- `haltingSeedRelators`
- `haltingSeedRelators_eq`
- `haltingRelatorQuotientEquiv`
- `haltingRelatorIndexStage`
- `primrec_haltingRelatorIndexStage`
- `haltingRelatorIndexStage_correct`
- `haltingRelatorIndexStage_exact`
- `FiniteGroupCopy`
- `finiteGroupCopy`
- `HasOracleGroupCopy`
- `hasOracleGroupCopy_of_finite`
- `finiteGroupCopy_false_of_infinite`
- `haltingSpectrum_no_any_computable_copy`
- `finite_set_primrec_membership`
- `oracleEnumerable_of_finite`
- `finite_group_primeSpectrum_indices`
- `oracle_any_spectrum_copy_implies_enumerable`

## DirectSumPresentation declarations

- `finiteSupportDirectSumEquiv`
- `finiteSupportDirectSumEquiv_primeSeed`
- `primeSeed_prime_order_relation`
- `coordinatePresentationHom`
- `directSumPresentationHom`
- `finiteSupport_hom_ext_primeSeed`
- `finiteSupport_prime_order_presentation`
- `directSumToHaltingGroup`
- `directSumToHaltingGroup_surjective`
- `haltingPresentedGenerator`
- `directSumPresentationHom_kills_halting_relators`
- `haltingGroupPresentationHom`
- `haltingGroup_prime_order_presentation`
- `primeOrderRelatorLabel`
- `computable_primeOrderRelatorLabel`

## Independent mathematical read review

The subgroup-spectrum agent separately reviewed SpectrumComputability's diagonal-code contradiction, odd-index nonenumerability pullback, infinite retained-even subgroup, finite-domain lower implication, literal projection kernel, and bounded-evaluator extra relator emitter. They found no correctness concern. The standard-D universal presentation was subsequently proved in DirectSumPresentation as described above. This read review does not replace the integrated compiler/axiom audit.
