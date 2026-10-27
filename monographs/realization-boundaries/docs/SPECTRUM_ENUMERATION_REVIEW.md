# Independent review of spectrum enumeration and computable copies

## Target and frozen input

Reviewed the frozen `SearchEnumerableSpectrum.lean` SHA-256 `beb34f6a62c4c4a67d37ab1f3d8f3c05259e3f0defad80d1db6264133a236a92` against Monograph 3.3:

> For every oracle X, the actual prime-support group D_B has an X-computable copy iff the prime-index selector B is computably enumerable relative to X.

The review is an independent mathematical read of the exact definitions and proof terms. The observed development receipt `verification/development/SearchEnumerableSpectrum_006.json` has exit code 0, warnings treated as errors, autoImplicit false, and the same frozen source hash. I did not mutate the source or rerun a redundant build; integrated clean audit and kernel replay remain root's responsibility.

## Verdict

The proof establishes the actual computable-copy criterion with standard positive-search (relative Sigma_1) enumeration semantics. I found no mathematical gap, false equivalence, hidden membership oracle, unproved equality computation, or finite-domain exclusion in the reviewed theorem.

`OracleSearchEnumeration` is the standard total-witness-test presentation of relative computable enumerability: its test is proved total and native oracle computable, and membership is equivalent to the existence of a successful natural witness. This is not a weaker notion of enumerability. It does not assume a selector decision procedure or merely declare a classical definition computable.

A literal stage-list emitter is not named in the frozen source. That is a small interface omission, not a gap in the mathematics. Root has assigned a separate literal Option-stage bridge, described below. It is unnecessary to prove equivalence with the separate `OracleEnumerable` partial-domain definition in order to match the book's listing-based notion. A direct bridge between successful total tests and an actual stage listing suffices.

## Actual group and code semantics

1. Raw code c contains a finite stage s and a finite natural residue list. A coordinate at actual prime p is retained only if a successful membership witness for p's actual zero-based prime index has appeared before s.
2. The prime index is `Nat.count Nat.Prime p.val`; the exact identity `primeAt (Nat.count Nat.Prime p.val) = p` is proved from `Nat.nth_count`. The prime-counting and prime enumeration computations are already native primitive/partial-recursive computations.
3. `spectrumDiscoveryValue` returns an element of the actual `spectrumSubgroup B`, a subgroup of the actual infinite finite-support group. Its membership proof extracts a real positive witness from the stage product. It does not replace D_B by an arbitrary group family with a similar cardinality.
4. Surjectivity is exact: a finitely supported selected vector has finitely many nonzero coordinates, each has a positive witness, and the finite supremum of witness stages admits the whole vector. Empty support is handled: the stage zero code denotes zero. The finite-witness choices occur in the surjectivity proof, not as data assumed computable.

## Addition and equality

Addition uses already interpreted raw finite vectors, adds their actual residue values, and moves to the maximum of the two discovery stages. This cannot activate a previously masked nonzero input: the new residue list itself is built from the masked input cells. The monotonicity proof for discovery confirms that every retained input coordinate remains admitted at the output stage.

The exact equality test compares only finitely many natural prime positions below the maximum residue-list length and compares residues modulo those primes. `residuesEqual_iff` identifies that bounded test with literal equality of the actual ambient vectors. Its computational proof uses bounded prime testing and natural arithmetic. No quotient equality or hidden infinite-coordinate equality is treated as a decision procedure.

Both addition and equality have native oracle-computability proofs. The resulting `OracleRawGroupCodes` contains exact semantic surjectivity, zero, addition, and equality contracts.

## From redundant names to an actual copy

The proof does not stop at a redundant presentation. `ComputableQuotientCodes`:

- tests whether a raw code is the least member of its actual equality class by a finite product of proved computable equality tests;
- proves there are infinitely many canonical classes when the represented group is infinite;
- computes the nth successful canonical code by native minimization with a termination witness;
- obtains genuinely bijective Nat names;
- computes the canonical index of the raw sum by another terminating native search.

The semantic naming map is an isomorphism witness and is not assumed independently computable relative to an unspecified external presentation. That matches the conventional meaning of a computable copy. The actual addition algorithm is separately proved oracle computable.

`OracleCopyOperations.lean`, independently inspected at hash `d6db70a3a1f076b71865a647a8406c18249cc545a8fdd80bcf5fa0779b4ddf1d`, supplies explicit native inversion and subtraction algorithms on the bijective Nat names. Its inverse search terminates because group inversion exists and the names are surjective. Thus group inverse is not silently missing from the computational interpretation.

## Finite and infinite cases

`HasOracleGroupCopy` explicitly permits a finite initial-segment copy or a bijective Nat-domain copy. The finite branch uses a fixed finite operation table, with ordinary native computability proved by the finite-domain theorem. This is the correct nonuniform existence statement. It does not claim a procedure for deciding that a finite enumeration has finished.

For the lower direction, finite groups have finitely many possible intrinsic prime-torsion indices, each divisor of their finite cardinality. Such a fixed finite set has a native primitive-recursive membership test. Infinite copies produce actual positive torsion searches. Both branches therefore yield the same explicit positive-search enumeration interface.

For the upper direction, `finite_or_infinite` separates the actual group: finite groups use the fixed finite-table copy, while infinite groups use the raw-code/canonical-name construction. No finite group is required to have bijective names on all of Nat.

## The precise listing interface

For the book's literal program-that-lists wording, add an interface with a total stage function

`stage : Nat -> Option Nat`

whose encoded output is native X-computable and satisfies

`n in A iff exists k, stage k = some n`.

The direct construction from the frozen positive-test interface is

`stage k = if test k = 0 then some k.unpair.1 else none`.

Every pair `(n,t)` occurs at `Nat.pair n t`, so the exact output-range proof is immediate from `test_spec` and the pairing inverse laws. Each stage terminates because the supplied test is total. Repetitions and blank stages are permitted in a list of a computably enumerable set. Finite and empty sets are included.

Conversely, from a total stage listing, the test on input `Nat.pair n t` compares `stage t` with `some n`, returning zero exactly on equality. The encoded Option equality test is ordinary primitive recursive, and composition gives native oracle computability. This obtains the exact positive-search interface from listing without invoking `OracleEnumerable`.

A named equivalence between these two explicit interfaces would make the formal statement literally match the book's selected presentation of computable enumerability. The currently proved minimization map `OracleSearchEnumeration.toOracleEnumerable` is mathematically useful but not required for that direct listing correspondence.

## Boundaries and recommendations

- The reviewed frozen theorem is exact for its explicitly defined standard positive-search c.e. semantics.
- Accept the mathematical 3.3 criterion, with the tiny literal stage-list bridge included before the final release audit if exact interface coverage is required.
- Do not describe a proof of `OracleEnumerable -> OracleSearchEnumeration` as necessary for the printed listing contract. That is a separate optional native normal-form equivalence.
- The read review is not an independent compiler implementation or external peer review. Compiler identity, imported cache pins, source snapshots, axiom audit, negative controls, and kernel replay must still be checked by the integrated acceptance run.

## Reviewed dependency hashes

```json
{
  "RealizationBoundaries/SearchEnumerableSpectrum.lean": "beb34f6a62c4c4a67d37ab1f3d8f3c05259e3f0defad80d1db6264133a236a92",
  "RealizationBoundaries/ComputableQuotientCodes.lean": "1e476f875f0917cdcaf3292c399ddbb83b3dacca080c7cbd2c2faec57da32757",
  "RealizationBoundaries/ComputableNormalCodes.lean": "7d25e320d78e74e3132643c864c43bf427f42fe6fd9d894f90a3691b950cd3c2",
  "RealizationBoundaries/OracleCopyOperations.lean": "d6db70a3a1f076b71865a647a8406c18249cc545a8fdd80bcf5fa0779b4ddf1d",
  "RealizationBoundaries/ComputablePresentations.lean": "f51b96aa3871c4dde05879d132c861f7d8382f82fdcbcb53e7f2276cbb742219",
  "RealizationBoundaries/SpectrumComputability.lean": "5e4f5dbc2b2e3e692c2a94c9cd15a787b5bc8bfebfa7fa8018c1cea8b4464982"
}
```


## Follow-up review: literal listing bridge now completed

The separately frozen `ListingSearchEquivalence.lean` was read at SHA-256 `c27f0c8381c76167b369ce749ca2ecb6d82d6ca5452cdb2be4f841b6de68fc2c`. It resolves the interface omission identified above. Its stage interface is stronger and equally appropriate to the proposed Option-stage interface: every stage outputs an actual finite List Nat, its ordinary native encoding is proved X-computable, and eventual list membership is exactly set membership. Repeated elements and blank stages are permitted.

`searchStageListing` computes all successful candidate tests with paired indices below the finite stage, positively encodes candidate n as n+1, removes zero blank entries, and decodes n+1 to n. The membership theorem is exact: n occurs at stage s iff some k < s has first unpaired coordinate n and test k = 0. A witness (n,t) is emitted no later than stage Nat.pair n t + 1. The zero-coding and cleanup do not lose the candidate n = 0.

The reverse construction uses bounded membership in the actual finite emitted list. The list output's encoding is native X-computable; decoding and finite list equality/membership are native primitive-recursive operations. Therefore the reverse total witness test is a real oracle procedure, not a classical selection assertion.

The two constructions prove `oracle_searchEnumeration_iff_stageListing` in both directions. `oracle_spectrum_copy_iff_stageListing` then combines that equivalence with the reviewed actual-copy theorem. **The exact book 3.3 listing-based criterion is now formally stated and proved.** No equivalence with the separate partial-domain OracleEnumerable definition is needed to justify that statement. I found no new correctness concern in either conversion or the final criterion.

## Follow-up review: least degrees and fixed observations

The independently read `DegreeVariation.lean` has SHA-256 `674ffbed6408f88bb441da0819ea053aab06c417972c2ee4a00ef4656ce8fcf2` in the reviewed snapshot.

The official Mathlib `TuringDegree` carrier is an antisymmetrization of native Turing reducibility on partial Nat functions, so it is broader than the ordinary set-degree carrier. `selectorTuringDegree` uses the actual total zero/one membership oracle of a selector. `SetTuringDegree` is explicitly the subtype of native degrees having such a total binary representative. This is the correct meaning of ordinary Turing degrees of sets used in the monograph. The source accurately avoids claiming a totalization theorem for all partial-function degrees, which is neither established nor needed for 8.4.

`HasLeastPresentationDegree` has both required components:

1. Attainment: a total membership oracle of degree d computes an actual copy of the group.
2. Lower bound: every total membership oracle computing an actual copy has degree at least d.

`paired_least_presentation_degree` obtains both from the exact native oracle-copy criterion, with reflexive reducibility supplying attainment at the selector's own degree. This establishes the conventional least presentation degree as the minimum oracle degree sufficient to compute a copy. It is not merely a lower bound or an unattained infimum.

`every_set_degree_with_common_observations` picks an actual binary representative supplied by the SetTuringDegree witness and returns an actual paired group of that least degree. Its structural clauses retain Countable, Infinite, residual finiteness, and the canonical completion equivalence to the same actual ambient product. The common-observation comparison is the established source-free cofinal finite-quotient comparison.

`every_set_degree_with_fixed_computable_observation` strengthens this to the literal fixed computable finite-group diagram. The inspected supporting `ComputableFiniteObservations` definitions use selector-free natural stage/residue codes, a natively computable prime-prefix modulus, modular addition/inverse/restriction algorithms, actual finite ZMod names, and cofinality of the prime prefixes. Thus the claim is not merely that each group happens to have isomorphic abstract finite quotients; one fixed native computable diagram is supplied for all degrees.

Reducedness is proved separately by `paired_degree_reduced`: every nontrivial divisible group is excluded from embedding in the actual paired group. This implies the standard reducedness assertion. The final fixed-observation theorem does not syntactically include reducedness in its displayed conjunction, so an exact coverage registry should cite the separate reducedness theorem alongside it. This is a packaging distinction, not an unresolved mathematical obligation.

The group is abelian through its actual AddSubgroup of the ambient product. No separate assumption of abelianness is smuggled into the existence statement. I found no correctness or calibration concern in the degree quantifiers, least-degree attainment, lower-bound direction, or fixed-observation bundle.
