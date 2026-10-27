# Proof ledger — Strong Artin Lean v0.23

## Evidence label

Every result listed below is **Lean-checked as written** under the pinned
Lean/mathlib environment.  The arithmetic existence of the Selmer-to-cotangent
comparison datum and the one-prime interface remains open.

## `SyzygyCorrectedAuxiliarySelection.lean`

Definitions:

- `pullbackLocalFunctional`;
- `rawEvaluationMap`.

Checked theorems:

1. `pullbackLocalFunctional_apply`;
2. `rawEvaluationMap_apply`;
3. `rawEvaluationMap_eq_evaluationMap_pullback`;
4. `ker_rawEvaluationMap_eq_relationSyzygies`;
5. `selectedKernel_pullback_eq_relationSyzygies`;
6. `rawEvaluationMap_surjective`;
7. `exact_relationSyzygies_rawEvaluation`;
8. `exists_syzygy_corrected_TaylorWiles_set`.

### Mechanism

The raw map factors as

```text
raw obstruction → intrinsic Selmer H → selected coordinate space.
```

The first map is surjective with kernel equal to relation syzygies.  If the
intrinsic selected evaluation is injective, the kernel of the composite is
therefore exactly the syzygy kernel.  Equal source/target finite dimensions make
the intrinsic selected evaluation surjective, and hence the raw composite is
surjective.

## `SyzygyCorrectedAuxiliaryMinimality.lean`

Checked theorems and definitions:

9. `intrinsicEvaluation_injective_of_ker_raw_eq_syzygies`;
10. `finrank_le_card_of_syzygy_corrected_family`;
11. `exists_cardinality_minimal_syzygy_corrected_set`;
12. `rawEvaluationEquiv_of_relationIndependent`.

### Mechanism

Conversely, if the raw selected kernel is exactly the relation-syzygy module,
then the intrinsic evaluation is injective.  Dimension comparison forces any
such scalar family to contain at least the intrinsic Selmer dimension many
labels.  The v0.15 construction attains that lower bound.

Under conormal independence the syzygy module is zero, so the exact raw
evaluation becomes a linear equivalence with the selected coordinate space.

## `IntrinsicAuxiliaryRank.lean`

Checked theorems:

13. `finrank_selmer_eq_finrank_cotangentH1`;
14. `exists_intrinsic_rank_auxiliary_set`;
15. `card_add_finrank_syzygies_eq_finrank_raw`;
16. `exists_intrinsic_rank_decomposition`.

### Mechanism

The comparison datum identifies intrinsic cotangent `H1` with Selmer, so their
finranks agree.  Rank-nullity for the surjective raw evaluation yields

```text
intrinsic auxiliary rank + syzygy rank = raw obstruction rank.
```

## `PresentationIndependentAuxiliarySet.lean`

Checked theorems and definitions:

17. `exists_common_syzygy_corrected_set`;
18. `rawObstructionEquivOfIndependent`;
19. `rawObstructionEquivOfIndependent_preserves_evaluation`.

### Mechanism

Selection occurs once on the common intrinsic Selmer space.  Pullback through
each presentation comparison gives the same selected set, with the appropriate
presentation-specific syzygy kernel.  When both presentations have independent
relations, their raw obstruction spaces are compared through the common
coordinate equivalences, and the comparison preserves evaluation.

## `IntrinsicSyzygyCorrectedCapstone.lean`

Checked capstone:

20. `exists_intrinsic_minimal_exact_auxiliary_set`.

This packages admissibility, intrinsic cotangent-H1 cardinality, exact syzygy
kernel, surjectivity, exactness, and scalar-cardinality minimality in one theorem.

## Declaration audit

New v0.23 source contains:

- theorem declarations: **18**;
- definitions: **4**;
- lemmas: **0**;
- abbreviations: **0**;
- structures: **0**;
- instances: **0**;
- source lines: **583**;
- `sorry`: **0**;
- `admit`: **0**;
- custom `axiom`: **0**;
- custom `opaque`: **0**.

The numbered ledger has twenty entries because two definitions are listed
alongside the eighteen theorem declarations.  The two additional definitions
in the first module are recorded separately above.  The machine count in `RESULT.json` is authoritative for syntax
categories.

Axiom reports are confined to:

- `propext`;
- `Classical.choice`;
- `Quot.sound`.
