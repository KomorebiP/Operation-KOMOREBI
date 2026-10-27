# Full-edition formalization roadmap

## Current boundary

The checked foundation covers Chapter 2 in the declared finite-atlas/bounded setting and Chapters 4.1, 4.2, 4.3 and 4.5 in the scopes recorded in Block 03. Mixed-state results currently use finite complex matrices. The equation map is in `SOURCE_MAP.md`. The rest of the manuscript has not been exhaustively inventoried or formally checked in this release. There is no defensible denominator for a full-edition completion percentage yet.

| Stage | Source area | Status | Next proof obligation |
|---|---|---|---|
| 1 | Finite orthogonal atlas, energy transfer, coarsening | First block checked in the stated bounded setting | Maintain literal source mapping and reusable theorem interfaces. |
| 2 | Moving atlas and whole-object deformation, Chapter 2.5–2.6 | Block 02 checked: normed-algebra deformation and arbitrary-dimensional bounded Hilbert operators | Maintain the exact source mapping and explicit completeness/unitarity/regularity assumptions. |
| 3 | Transfer extensions, Chapters 4–5 | Block 03 checks nonlinear skew flow, associative refinement, finite-matrix mixed-state transfer, and universal source balance | Next: tensor mixed-state marginals (4.23–4.28), information transport (4.35–4.44), Lindblad jumps (4.45–4.52), then Chapter 5. Positivity-preservation from initial data remains separate. |
| 4 | Countable atlases and unbounded generators, Chapter 6 | Not started | Domains, graph compatibility, summability, continuity and admissible limit interchanges. Finite algebra does not discharge these. |
| 5 | Finite differential no-go and corner calculus, Chapter 7 | Not started | Formalize the pointwise algebra obstruction, then noncommutative inner-derivation and curvature identities. |
| 6 | Discrete relativity and gauge fields, Chapters 8–12 | Not started | Clifford relations, exact walk unitarity, quasienergy branches, ordered holonomy, covariance and finite-range locality. |
| 7 | Gravitational constraints and strong fields | Not started | Typed canonical variables, actual brackets, constraint propagation, regularity assumptions and continuum-versus-resolved distinctions. |
| 8 | Cosmology, dark sectors and observational interfaces | Not started | Exact model equations, mathematically justified approximations, rejection conditions and corrected-branch bookkeeping. Observational agreement remains evidence, not a Lean theorem about nature. |

## Recommended next block

First complete Chapter 4.4, equations (4.23)–(4.28): construct the tensor-product **matrix** atlas and prove actual joint probabilities and marginal trace identities. Reuse the recovered tensor multiplication facts and Block 03's `MatrixAtlas`; do not claim that existing tensor algebra already proves joint-state positivity or marginals. Keep the general joint density matrix, not merely a product-state example.

Then prove actual information derivatives in Chapter 4.6, equations (4.35)–(4.44), with strict packet positivity, q≠1 for Rényi, and the needed power/log hypotheses. Derive symmetrization from the antisymmetric currents; do not assume the target entropy balance. Then derive the diagonal reduction of the actual Lindblad generator in Chapter 4.7, equations (4.45)–(4.52), preserving gain/loss factors and source indices.

Read physical pages 24–25 (printed 11–12) and subsequent pages before extending the scope. Chapter 3's unit, variational and asymptotic targets are not all checked by the current algebra and need their own inventory. The existence/uniqueness of trajectories and preservation of density positivity from initial data remain unproved interfaces, not consequences of a zero trace derivative.

## Future source inventory

Retain the master and compare later targets with the two-volume research edition and technical supplements before claiming full-edition coverage. Those larger source-reconciliation tasks are not completed here. Preserve the master’s P/N/C/Q/O labels separately from a new Lean status field. The historical additive dark-sector chapters are explicitly superseded by the scale-covariant branch in the master’s revision notes.
