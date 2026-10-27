# External source checks — v0.11.0

Checked on 27 September 2026. This is a bounded dependency check, not a novelty survey.

## Milne: profinite cohomology and inflation

- Author: J. S. Milne.
- Title: Class Field Theory.
- Version: 4.03, 6 August 2020.
- Primary source: https://www.jmilne.org/math/CourseNotes/CFT.pdf
- Exact locator: Chapter II, Section 4, Proposition 4.2, printed page 87, zero-based PDF page 95.
- Authentication: title/version page and exact theorem page opened from the author's site. The theorem page was also inspected as a screenshot.
- Needed implication: continuous cohomology for a discrete module is a filtered colimit of finite-quotient cohomology with appropriate fixed coefficient modules; equality, including equality to zero, occurs at a finer finite quotient.
- Translation: in the manuscript V is finite discrete, and the indexing open normal subgroups are contained in ker(rho_n), hence act trivially on V. Thus V^U = V and the formula is the stated fixed-V specialization.
- Status: known after translation of notation. The manuscript gives the finite-cochain factorization argument directly.
- Boundary: this does not prove that every obstruction is eventually zero, nor a numerical bound on how fine a source quotient must be.

## Stacks Project: continuous inhomogeneous cochains

- Title: Tate's continuous cohomology.
- Exact source: Section 59.58, Tag 0DVG.
- Primary source: https://stacks.math.columbia.edu/tag/0DVG
- Needed implication: definition of the continuous inhomogeneous cochain complex and its differential.
- Authentication: official tag page opened in full.
- Translation: the new obstruction has coefficients in finite discrete End(F_p^d); the differential is b(g) + g.b(h) - b(gh).
- Status: standard convention. No ambiguous comparison of cohomology with arbitrary topological coefficient modules is imported.

## Results proved directly in the new fragment

Continuous next-step matrix repairs, free pro-p generator lifting, continuous powers, cyclic centralizers, normalized commuting lifts, and the sharp rank-two horizon have direct proofs in the manuscript. The cochain and free-object mechanisms are classical. No claim that the centralizer packaging or horizon is historically new has been verified.

Broad web searches returned unrelated results and were discarded. No backward/forward citation survey or independent novelty reviewer was completed. No external paper full text or font files are distributed with the release.
