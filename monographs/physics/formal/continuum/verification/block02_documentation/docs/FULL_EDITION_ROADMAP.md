# Full-edition formalization roadmap

## Current boundary

The checked foundation is Chapter 2 of the 550-page master in the declared finite-atlas/bounded setting. The equation map is in `SOURCE_MAP.md`. The rest of the manuscript has not been exhaustively inventoried or formally checked in this release. There is no defensible denominator for a full-edition completion percentage yet.

| Stage | Source area | Status | Next proof obligation |
|---|---|---|---|
| 1 | Finite orthogonal atlas, energy transfer, coarsening | First block checked in the stated bounded setting | Maintain literal source mapping and reusable theorem interfaces. |
| 2 | Moving atlas and whole-object deformation, Chapter 2.5–2.6 | Block 02 checked: normed-algebra deformation and arbitrary-dimensional bounded Hilbert operators | Maintain the exact source mapping and explicit completeness/unitarity/regularity assumptions. |
| 3 | Transfer extensions, Chapters 4–5 | Not started in this release | Refinement towers, mixed-state transfer, tensor atlases, information transport, Lindblad jumps, positive/overlapping atlases. Separate positivity hypotheses from conclusions. |
| 4 | Countable atlases and unbounded generators, Chapter 6 | Not started | Domains, graph compatibility, summability, continuity and admissible limit interchanges. Finite algebra does not discharge these. |
| 5 | Finite differential no-go and corner calculus, Chapter 7 | Not started | Formalize the pointwise algebra obstruction, then noncommutative inner-derivation and curvature identities. |
| 6 | Discrete relativity and gauge fields, Chapters 8–12 | Not started | Clifford relations, exact walk unitarity, quasienergy branches, ordered holonomy, covariance and finite-range locality. |
| 7 | Gravitational constraints and strong fields | Not started | Typed canonical variables, actual brackets, constraint propagation, regularity assumptions and continuum-versus-resolved distinctions. |
| 8 | Cosmology, dark sectors and observational interfaces | Not started | Exact model equations, mathematically justified approximations, rejection conditions and corrected-branch bookkeeping. Observational agreement remains evidence, not a Lean theorem about nature. |

## Recommended next block

Chapter 4.1, equations (4.1)–(4.5): derive state-dependent skew-flow balances by applying the existing pointwise derivative interface to the actual current generator. Chapter 4.3, equations (4.16)–(4.22): prove associativity of coarsening for projectors, energies, and currents, including address-map and incidence-matrix formulations.

Then address Chapter 4.2, equations (4.6)–(4.15), mixed-state trace dynamics, with an actual matrix-valued derivative and cyclicity/conjugation proofs. Distinguish finite matrices from infinite-dimensional trace-class operators and their domains. The conjugation bar in (4.14) must be read from the page image.

Chapter 3 contains independent unit, variational, and asymptotic targets. They are not all checked by the Chapter 2 results; a separate inventory is still needed. Do not encode later field-equation or constraint-closure conclusions as hypothesis fields.

## Future source inventory

Retain the master and compare later targets with the two-volume research edition and technical supplements before claiming full-edition coverage. Those larger source-reconciliation tasks are not completed here. Preserve the master’s P/N/C/Q/O labels separately from a new Lean status field. The historical additive dark-sector chapters are explicitly superseded by the scale-covariant branch in the master’s revision notes.
