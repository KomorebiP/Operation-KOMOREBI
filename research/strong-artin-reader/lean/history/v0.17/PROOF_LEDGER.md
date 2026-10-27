# Proof ledger — Strong Artin Lean v0.17

## Evidence label

Every statement listed below is **Lean-checked as written** under the pinned Lean/mathlib environment. The results are algebraic, linearized, and module-theoretic. Arithmetic instantiations explicitly listed in `RESEARCH_BOUNDARY.md` remain open.

## Local Frobenius and tame pairing

### `LocalFrobeniusPerfectPairing.lean`

- perfect trace-pairing map on square matrices;
- Frobenius centralizer as `ker (1 - Ad(A))`;
- centralizer equivalence with the annihilator of Frobenius coboundaries;
- exact equivalence
  ```text
  frobeniusCentralizer A ≃ₗ[k]
    Dual k (Matrix / frobeniusCoboundaries A);
  ```
- unique centralizing representative of every quotient functional.

### `TameLocalPerfectPairing.lean`

- exact tame local pairing on matrix representatives;
- perfectness in both variables;
- every nonzero tame direction detects an unramified quotient class;
- every nonzero unramified quotient class is detected by a tame direction.

### `TameInertiaRelation.lean`

- linearized tame relation operator `Ad(A) - q`;
- relation-space membership criterion;
- at `q = 1`, the relation space equals the Frobenius centralizer.

### `TameTaylorWilesPairingCapstone.lean`

- exact equivalence between the `q = 1` tame relation space and the dual unramified quotient;
- representative formula `trace(P * X)`;
- unique tame-relation representative of every quotient functional.

## Generic-fibre survival and branch support

### `GenericFiberSurvival.lean`

- powers of a regular uniformizer act regularly;
- localization at those powers is injective;
- nonzero special fibre implies a nonzero integral module;
- a nonzero integral module with regular uniformizer action has nonzero generic fibre;
- a class nonzero modulo `pi M` survives in localization.

### `FlatGenericFiberSurvival.lean`

- flatness makes a coefficient nonzerodivisor act regularly;
- flatness makes localization injective;
- flatness plus nonzero special fibre gives nonzero generic fibre;
- a nonzero special-fibre class survives generically.

### `TransitiveGenericBranchSupport.lean`

- finitely many branch scalars summing to one support at least one component of a nonzero module;
- equivariant transport preserves component support;
- support propagates along arbitrary iterates;
- a transitive branch action supports every component.

### `ProductRingBranchSupport.lean`

- coordinate branch idempotents in a finite product ring;
- their sum is one;
- a nonzero module supports some coordinate branch;
- a faithful module supports every branch;
- a transitive equivariant automorphism supports every branch.

### `ResidualOccurrenceToGenericSupport.lean`

- a nonzero special fibre and an injective comparison map force the target generic module to be nontrivial;
- transitive split-product equivariance then forces support on every generic branch.

### `FlatSplitGenericSupportCapstone.lean`

- flat special-fibre occurrence produces a nonzero split generic module;
- transitive generic twist equivariance forces all branches to be supported.

## Linearized finite-depth correction

### `FiniteLinearizedCorrection.lean`

- one affine correction equation is solvable under surjectivity;
- arbitrary indexed and finite families are solvable;
- v0.15/v0.16 exact admissible auxiliary columns solve any finite family of linearized errors.

### `FiniteDepthLinearizedLiftSystem.lean`

- a surjective correction map recursively propagates any explicitly compatible state-dependent lift system to every finite depth;
- exact admissible auxiliary-column selection supplies such a surjective map.

## Split-prime transverse localization

### `SplitPrimeTransverseLocalization.lean`

- if localization kills the cyclic class, it kills its full scalar line;
- localization descends canonically through the transverse quotient;
- raw local probes become quotient functionals;
- those probes are invariant under adding the cyclic class;
- nonzero raw evaluation detects a nonzero transverse quotient class.

### `SplitPrimeAuxiliarySelectionCapstone.lean`

- split-prime raw one-class detection instantiates v0.15’s `OnePrimeSelectionInterface`;
- exactly the transverse dimension many admissible labels are selected;
- simultaneous evaluation is injective;
- selected quotient evaluations equal the original raw local evaluations on representatives.

## Functional-to-column representation and exact count

### `ObstructionFunctionalColumnRepresentation.lean`

- evaluation from equation-space columns to the dual obstruction space is surjective in finite dimension;
- every scalar local functional has a representing column;
- arbitrary families have simultaneous representing columns;
- every v0.15 one-prime interface admits columns and an exact admissible set making the augmented Jacobian surjective;
- the same columns support all compatible finite-depth linearized lift systems.

### `ObstructionColumnQuotient.lean`

- `ker (evaluationColumnMap J) = range J`;
- two columns represent the same obstruction functional iff their difference lies in `range J`;
- pointwise uniqueness modulo `range J`;
- canonical equivalence
  ```text
  W / range J ≃ₗ[k] Dual k (obstructionDual J).
  ```

### `MinimalAuxiliaryColumnCount.lean`

- the dual obstruction dimension equals `finrank k (W / range J)`;
- v0.15 selects exactly this Jacobian codimension many admissible columns;
- the same exact-size set supports every compatible finite-depth lift system.


### `AuxiliaryColumnMinimality.lean`

- surjectivity of an augmented Jacobian forces simultaneous selected-column evaluation to be injective on the dual obstruction space;
- every surjective auxiliary completion has at least `finrank k (W / range J)` columns;
- the exact set produced from a one-prime interface is cardinality-minimal among all surjective completions indexed by the same label type.

## Integrated relative pipelines

### `RelativeLinearizedPipelineCapstone.lean`

- under an explicit Selmer--Jacobian equivalence and a preselected local-column comparison, split-prime one-class detection yields exact admissible columns, augmented surjectivity, and arbitrary finite-depth correction.

### `AutomaticRelativeLinearizedPipeline.lean`

- transports the split-prime one-prime interface across a Selmer--Jacobian equivalence;
- constructs compatible equation columns by double duality automatically;
- selects exactly the Jacobian codimension many admissible labels;
- proves augmented-Jacobian surjectivity;
- propagates every compatible state-dependent linearized lift system through arbitrary finite depth;
- removes the earlier preselected-column and local-column compatibility assumptions.

## Declaration and axiom audit

New v0.17 source:

- theorem declarations: **80**;
- definitions: **23**;
- abbreviations: **4**;
- structures: **0**;
- instances: **0**;
- `sorry`: **0**;
- `admit`: **0**;
- custom `axiom`: **0**;
- custom `opaque`: **0**.

The checked capstones report only ordinary Lean/Mathlib foundations:

- `propext`;
- `Classical.choice`;
- `Quot.sound`.
