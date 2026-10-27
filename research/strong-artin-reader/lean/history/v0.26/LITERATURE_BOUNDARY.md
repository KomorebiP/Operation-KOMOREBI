# Literature and imported formal infrastructure

## Formal source used

The exact compiler input is Mathlib commit:

```text
aeb72f1e9981b6d35b426b16dca7759be3e7ba06
Mathlib/RepresentationTheory/Homological/GroupCohomology/LowDegree.lean
```

Its low-degree API supplies genuine `cocycles₂`, `d₁₂`, `H2`, `H2π`, `H2π_eq_zero_iff`, and `H2π_eq_iff`. The degree-two type is cohomology of the inhomogeneous cochain complex, not a project-defined placeholder. The new source proves that the actual representation defect belongs to its cocycle submodule and that its class detects liftability.

Public official documentation checked during this route:

```text
https://leanprover-community.github.io/mathlib4_docs/Mathlib/RepresentationTheory/Homological/GroupCohomology/LowDegree.html
```

The live documentation was used for discovery and confirmation of the API's intended meaning. Compilation and exact source checking use the pinned local revision. Local file hashes are recorded in `FORMAL_SOURCE_PROVENANCE.json`.

## Overlap and priority

This is a formalization of the standard degree-two obstruction mechanism for lifting a representation through a square-zero extension, with a strict fixed-subgroup variant and verified nonvanishing examples. No historical novelty claim is made. No full literature survey, specialist referee review, or assertion of universal Langlands applicability was performed.

No external arithmetic vanishing, local Tate-duality, Chebotarev, automorphy, or Selmer-comparison theorem is imported as an assumed custom Lean axiom. Those arithmetic inputs remain open for the intended application.
