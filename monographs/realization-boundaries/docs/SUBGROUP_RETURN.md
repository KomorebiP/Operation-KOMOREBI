# Subgroup spectrum and unary selector closure

Base checkpoint: `Realization_Boundaries_Lean_v0.6.0_Checked.zip`.
Base archive SHA-256: `032f61f0e176f0f3abfeb3615b8936ebd9edb7c3f9a07b6b8ad25877ec7aef70`.
Owner: subgroup_spectrum agent. Owned production paths: `SubgroupSpectrum.lean`, `UnarySelectors.lean`.

## Exact scope completed

`SubgroupSpectrum.lean` proves the algebraic statement of monograph Theorem 3.1 for the actual `finiteSupport` group, and Corollary 3.2. It does not replace D by an arbitrary abstract family. Its index is `Prime`, which is the same prime-component indexing used throughout the checked companion.

* `spectrumSubgroup B` consists of actual D elements with support contained in B.
* `primeSeed_mem_of_coordinate_ne_zero` isolates a coordinate by actual finite CRT multiplication and normalizes it to the standard seed.
* `finiteSupport_primeSeed_decomposition` reconstructs every D vector by a finite sum of natural scalar multiples of its actual prime seeds.
* `spectrumSubgroup_subgroupSpectrum` proves every subgroup is exactly a support subgroup.
* `subgroupSpectrumOrderIso` is the actual order isomorphism `Set Prime ≃o AddSubgroup finiteSupport`.
* `finiteSupport_subgroup_fullyInvariant` applies to every D subgroup and arbitrary D endomorphism.
* `spectrumSubgroup_hasPrimeTorsion_iff`, `hasPrimeTorsion_equiv`, and `spectrumSubgroup_isomorphic_iff` recover B from intrinsic nonzero p-torsion, without markings or continuity hypotheses.
* `spectrumSubgroup_union`, `spectrumSubgroup_inter`, and `spectrumSubgroup_complement` give literal lattice operations and the complementary internal sum.
* `spectrumObservationFiber_card` proves exactly continuum many extensions of every finite prime observation. `spectrumObservation_not_isomorphic` proves distinct extensions have nonisomorphic actual subgroups. `spectrum_determined_by_all_observations` proves the all-coordinate uniqueness statement.

Empty and finite spectra require no extra assumptions and are covered by all classification theorems. The accompanying unnumbered topological homeomorphism paragraph in the book is not a theorem claimed by this file.

`UnarySelectors.lean` proves monograph Theorem 3.5 with actual finite-state semantics:

* `UnaryMachine` has a finite state type, one transition, a starting state, and an accepting set.
* `UnaryMachine.accepts` runs the transition by actual function iteration on unary input length.
* `unaryMachine_ultimatelyPeriodic` derives eventual orbit repetition by the finite pigeonhole principle.
* `unaryTail_bounded` and `unaryTail_range_finite` prove finitely many tails for an ultimately periodic predicate.
* `unaryTailMachine` constructs the converse finite automaton, and `unaryTailMachine_orbit` identifies its actual state after each input length.
* `unaryRecognizable_iff_ultimatelyPeriodic` is the finite-automaton equivalence.
* `indexedSpectrum` uses the established nth-prime indexing, and `unary_selector_classification` includes abstract group isomorphism using the intrinsic spectrum criterion. A different accepted selector cannot accidentally realize an isomorphic group.

No computability, halting-set, 3.3, or 3.4 claim is made here.

## Verification

Pinned restored Lean 4.34.0-rc2 runtime and original Mathlib cache were used read-only. Both sources compile with `-DwarningAsError=true -DautoImplicit=false` through `scripts/check.py`.

* Final SubgroupSpectrum development compile: `verification/development/SubgroupSpectrum_005.json`, exit 0.
* Final UnarySelectors development compile: `verification/development/UnarySelectors_003.json`, exit 0.
* Kernel replays completed with exit 0: `verification/development/SubgroupSpectrum_replay.log`, `verification/development/UnarySelectors_replay.log`.

Compiler development failures were local type/API/linter corrections, retained in development receipts. No mathematical target was weakened to resolve them. Final shared acceptance audit remains the coordinator's responsibility.

Final source hashes:

* SubgroupSpectrum.lean: `cc4356c4a4f9b8ed1054e39b72fb62c822c6602c4703e3444c4dd4649ca53f69`.
* UnarySelectors.lean: `17a038b272fb2cc22e1d1c3398723c5439a37600f86d98e9fbf54f04b4236fa5`.

## Fresh review of finite root code

I independently read the then-current `RootAlgorithm.lean` (SHA-256 `1672b698b5d4e9d05b3c5ab688d5753cd9169d9af169d261610824d2891300bc`) against printed Theorem 6.1 and appendix A.2. Its exact ambient arithmetic, residual correction, finite extraction equality, root correctness, rejection existence, and support bound match the stated mathematics. The inverse at exceptional primes is zero, so the finite code agrees with the normalized correction used in the proof.

At that reviewed revision, three remaining boundaries were reported to the coordinator: executable return of the rejecting prime rather than `None` plus existential proof; surjectivity of the finite list encoding onto all finite-support normal forms; operational/query cost and literal correspondence to the shipped Python routine. Subsequent revisions require their own review. This review does not certify Python code or claim external peer review.
