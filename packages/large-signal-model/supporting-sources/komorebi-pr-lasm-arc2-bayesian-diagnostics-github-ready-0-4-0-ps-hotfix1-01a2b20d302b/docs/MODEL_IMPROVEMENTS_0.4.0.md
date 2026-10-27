# Model improvements in 0.4.0

Version 0.4.0 expands the typed proposal grammar and makes failure analysis a
first-class part of the Bayesian Large Signal Model.

## Added operator families

- marker-glyph-conditioned recoloring
- enclosed-background detection and attribute-conditioned filling
- periodic resizing with inferred color transfer
- Kronecker motif variants and complemented masks
- modular affine index tiling
- object-chain packing
- object-shape and hole-conditioned recoloring
- periodic stripe construction from marker pairs

Every family is admitted only after executing it on every demonstration and
checking exact array equality. The new operators are generic, parameterized
families rather than task-ID exceptions.

## Posterior selection changes

Output posterior records now retain:

- total output probability
- exact-fit output probability
- number of exact-fit candidates supporting the output
- best individual candidate probability

Attempt selection prioritizes posterior-supported exact-demonstration outputs
and keeps a distinct second abstraction when one exists. A probability-weighted
diverse fallback is used only when fewer than two exact-fit output hypotheses
are available.

## Diagnostic feedback loop

Each miss is resolved into:

```text
shape residual
added support
missing support
wrong-color support
object-count change
transformation class
posterior exact-fit coverage
selected program family
```

This distinguishes a grammar-coverage failure from a ranking/generalization
failure and creates an auditable queue for the next operator block.
