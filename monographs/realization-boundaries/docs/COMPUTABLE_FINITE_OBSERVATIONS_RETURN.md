# Fixed computable finite observations: checked return

Owner: `/root/reachability`. Parent: checked Lean v0.6.0 archive SHA-256 `032f61f0e176f0f3abfeb3615b8936ebd9edb7c3f9a07b6b8ad25877ec7aef70`.

Production artifact: `RealizationBoundaries/ComputableFiniteObservations.lean`.
Final source SHA-256: `7a061e5bda24c19a5c0a8b7aeaeabae741a1bed3ffa32766fc48f3950631afc2`.

## Exact fixed inverse system

Let `observationPrimes n` be the finite set of the first `n` actual prime coordinates, and `observationModulus n` their product. The object at stage `n` is the actual finite cyclic group `ZMod (observationModulus n)`. A map from stage `n` to stage `m ≤ n` is the actual residue-reduction homomorphism. Stage zero has order one, retaining the trivial finite observation.

All the following are proved without any selector or oracle parameter:

- positivity, squarefreeness, and divisibility of stage moduli;
- cofinal containment of every actual finite prime set in a prefix;
- native `Computable` stage sizes;
- native computable validity of natural residue names, ordinary name equality, and the inverse-system order relation;
- native computable addition, additive inversion, and transition tables;
- actual bijective natural finite naming `Fin Q_n ≃ ZMod Q_n`, given by the literal natural cast;
- closure of every table in the valid finite domain;
- exact addition, inverse, and transition semantics in the actual finite groups.

The key algorithm declarations are `computable_observationModulus`, `computable_observationValid`, `computable_observationEquality`, `computable_observationIndexRelation`, `computable_observationAddCode`, `computable_observationNegCode`, and `computable_observationRestrictionCode`.

## Identification with the actual finite quotients

This is not merely a new diagram of finite groups of matching orders.

- `observationCrtEquiv` is the actual CRT ring equivalence from the fixed cyclic stage to its exact finite prime-coordinate group.
- `observationCrtEquiv_natCast` gives its explicit residue interpretation.
- `observationCrtEquiv_restriction` proves compatibility with every actual coordinate restriction.
- `computableObservationIso` is the resulting natural isomorphism to the prefix reindexing of `coordinateObservation`.
- `observationPrefixFunctor_initial` certifies categorical inverse-system cofinality of this prefix system.
- `computableObservationQuotientIso W` identifies the reindexed actual all-finite-quotient diagram of every rational preimage with this one fixed system.
- `computableObservationIndex_initial W` proves the composed index functor is categorically initial.
- `fixedComputableObservation` packages the fixed source-free system as a `FiniteObservation`.
- `allFiniteObservation_fixed_computable W` proves `CommonCofinalObservation (allFiniteObservation W) fixedComputableObservation`.

Thus the computational-observation clause of printed 8.4 has a fixed genuine computable inverse system with a proved cofinal comparison to the entire observation. Neither the algorithms nor their source-free finite diagram take a selector or a named dense-source element as input. Their comparison with a given source uses `W` only mathematically.

## Certified runnable implementation

The mathematical stage labels use existing `Nat.nth`, which is a classically defined function despite its separately proved native computability. Direct Lean `#eval` of those labels therefore failed. That failure is retained in `verification/development/ComputableFiniteObservations_direct_eval_failed.log` and is not passing runtime evidence.

To make the implementation directly runnable as well, the module additionally defines:

- `observationPrimeProgram`: executable terminating search for the prime at a specified index;
- `observationModulusProgram`: executable primitive recursion over that search;
- `observationValidProgram`, `observationAddProgram`, `observationNegProgram`, and `observationRestrictionProgram`.

Each has a checked equality theorem identifying it with its exact mathematical stage or table. The prime-search existence proof is erased at runtime. This supplies both native recursion-theoretic computability and an actual certified executable implementation.

## Verification

- `verification/development/ComputableFiniteObservations_009.json`: compiler exit 0, warnings as errors, autoImplicit false, 6.01 seconds, exact final source hash above.
- `verification/development/ComputableFiniteObservations_final_replay.log`: final kernel replay exit 0.
- `verification/development/ComputableFiniteObservations_contract.log`: exact theorem types, allowed-axiom checks, and executable program evaluations; compiler exit 0.
- Headline native computability and cofinal observation theorems use only `propext`, `Classical.choice`, `Quot.sound`.
- Preliminary compilation/API failures and the initial direct-evaluation failure remain development evidence. None replaces the final receipt.

Runtime evaluations produced:

| Program input | Output |
|---|---|
| stage size 0 | 1 |
| stage size 1 | 2 |
| stage size 4 | 210 |
| add 209 and 2 at stage 4 | 1 |
| inverse of 2 at stage 4 | 208 |
| restrict residue 209 to stage 2 | 5 |
| validity of residue 210 at stage 4 | false |

## Integration

Add `ComputableFiniteObservations` after `ObservationSystems` and `PrimeComputability` in root imports and the serial build/replay list. The degree-family owner can combine `allFiniteObservation_fixed_computable` with the exact least-presentation-degree results to finish the fixed-computable-observations clause of 8.4. No independent claim of the whole project's 1.0 completion is made by this module.
