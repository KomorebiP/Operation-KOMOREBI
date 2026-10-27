# Full-edition formalization roadmap

## Current boundary

The first active target is Chapter 2 of the 550-page master. The equation map is in `SOURCE_MAP.md`. The rest of the manuscript has not been exhaustively inventoried or formally checked in this release. There is no defensible denominator for a full-edition completion percentage yet.

| Stage | Source area | Status | Next proof obligation |
|---|---|---|---|
| 1 | Finite orthogonal atlas, energy transfer, coarsening | First block checked in the stated bounded setting | Maintain literal source mapping and reusable theorem interfaces. |
| 2 | Moving atlas and whole-object deformation, Chapter 2.5–2.6 | Finite-matrix upstream results rechecked; new general block pending | Differentiate the actual time-dependent bounded-operator coordinates and corner products; derive every connection term. |
| 3 | Transfer extensions, Chapters 4–5 | Not started in this release | Refinement towers, mixed-state transfer, tensor atlases, information transport, Lindblad jumps, positive/overlapping atlases. Separate positivity hypotheses from conclusions. |
| 4 | Countable atlases and unbounded generators, Chapter 6 | Not started | Domains, graph compatibility, summability, continuity and admissible limit interchanges. Finite algebra does not discharge these. |
| 5 | Finite differential no-go and corner calculus, Chapter 7 | Not started | Formalize the pointwise algebra obstruction, then noncommutative inner-derivation and curvature identities. |
| 6 | Discrete relativity and gauge fields, Chapters 8–12 | Not started | Clifford relations, exact walk unitarity, quasienergy branches, ordered holonomy, covariance and finite-range locality. |
| 7 | Gravitational constraints and strong fields | Not started | Typed canonical variables, actual brackets, constraint propagation, regularity assumptions and continuum-versus-resolved distinctions. |
| 8 | Cosmology, dark sectors and observational interfaces | Not started | Exact model equations, mathematically justified approximations, rejection conditions and corrected-branch bookkeeping. Observational agreement remains evidence, not a Lean theorem about nature. |

## Recommended next block

Complete the literal Chapter 2.6 deformation identities for actual differentiable operator families, reusing the finite-matrix product and adjoint derivatives already recovered. Then connect the existing finite moving-frame theorem to the master’s skew-generator convention. Extend to general bounded operators only with a correct topology and derivative statement.

Do not replace the desired derivative formula by an assumed equality, encode constraint closure as a structure field, or use a numerical residual as a proof. A successfully checked conditional theorem still needs its conditions discharged for a specific physical model.

## Future source inventory

Retain the master and compare later targets with the two-volume research edition and technical supplements before claiming full-edition coverage. Those larger source-reconciliation tasks are not completed here. Preserve the master’s P/N/C/Q/O labels separately from a new Lean status field. The historical additive dark-sector chapters are explicitly superseded by the scale-covariant branch in the master’s revision notes.
