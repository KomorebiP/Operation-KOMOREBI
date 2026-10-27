# Komorebi KZFC Residual Reflection v0.2.0

Formal checkpoint for a Komorebi-style ZFC expansion program based on residual reflection.

## Machine-checked results

### Generic residual layer

- `ResidualSystem.KRR`: global failure implies an admissible local residual witness at some finite depth.
- `ResidualSystem.KRR0`: depth-zero specialization.
- `ResidualSystem.krr_iff_krr0_of_flattenable`: **Residual Flattening Theorem**.
- `ResidualSystem.exists_positive_depth_obstruction_of_krr_not_krr0`: if KRR holds but KRR0 fails, some obstruction occurs at a strictly positive depth.
- `ResidualSystem.not_flattenable_of_krr_not_krr0`: any strict separation is necessarily non-flattenable.

### Cardinal-bounded layer

- `SizedResidualSystem.KRRAt S κ` and `KRR0At S κ` formalize `< κ` witness bounds.
- `krrAt_mono` and `krr0At_mono`: enlarging the witness cardinal preserves the corresponding principle.
- Cardinal-bounded flattening and positive-depth necessity are proved.
- `KRRClass κ C` and `KRR0Class κ C` state the candidate principles over a specified admissible class `C`.

### First-order baseline

- `FirstOrderResidual.schema_iff_compactness`: depth-zero residual reflection over all finitary first-order theories is equivalent to ordinary first-order compactness.
- `sizedSystem_krr0_aleph0`: the first-order residual system satisfies KRR0 at `aleph0`.
- `sizedSystem_krr_of_aleph0_le`: because first-order counterexamples have finite witnesses, the same system satisfies KRR at every `κ >= aleph0`.

### Logic-independent compactness theorem

- `AbstractLogic.krr0Schema_iff_kappaCompact` proves, for any abstract logic whose residual pieces are subtheories,

      KRR0_κ  <->  κ-compactness.

- `FirstOrderResidual.abstractLogic_kappaCompact_aleph0` instantiates this for ordinary first-order logic using Mathlib's compactness theorem.

## Interpretation

Depth zero is now classified: when residual pieces are subtheories, `KRR0_κ` is exactly the corresponding `< κ` compactness principle. Therefore a genuinely new Komorebi foundational axiom cannot come merely from renaming compactness.

Novelty must occur in at least one of two places:

1. positive residual depth that is not uniformly flattenable to depth zero, or
2. a stronger logic/class of systems, such as an `L_{κ,κ}` instantiation whose depth-zero compactness has large-cardinal strength.

## What is not claimed

This checkpoint does **not** prove a new axiom beyond ZFC, nor a consistency theorem for one. It formalizes the candidate schema, proves its basic metatheory, classifies the depth-zero case, and isolates the exact condition under which higher residual depth could add strength.

## Verified environment

- Lean 4.34.0-rc2
- Lake 5.0.0
- Mathlib revision `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`
- Full Lake build: PASS, 1041 jobs
- Source scan: no `axiom`, `sorry`, or `admit` declarations/tactics
