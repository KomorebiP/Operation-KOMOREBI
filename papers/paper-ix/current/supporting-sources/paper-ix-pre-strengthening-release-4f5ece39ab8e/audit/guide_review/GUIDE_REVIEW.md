# Paper IX independent guide review

The frozen guides pass the fidelity and instructional review. Formal correctness remains conditional on the named inherited Lean/Mathlib compiler evidence; this review does not claim a fresh Lean run.

| Item | Independently checked result |
|---|---|
| Lean guide | 120 physical pages, 119 printed pages; 47 exact source excerpts, 623 raw lines across 38 source identities, each taught once |
| Source catalog | 1,876 source-version rows across 199 identities; all hashes and named commands match |
| Manuscript correspondence | 62 indexed statements and 202 named-source links resolve |
| Dependency map | 55 direct-import proof modules; exact match to raw imports, acyclic |
| Visual guide | 34 pages; 413 original mathematical spans and 28 original vector plates preserved; four new pages/plates |
| Navigation | 62 Lean chapter-page records match aux; 71 visual GoToR links match 58 frozen manuscript labels |
| Independent finite checks | 19 exact integer/Fraction checks, validated v2 bounded manifest; no author-model imports |
| Author checker rerun | 241 named assertions, 31,353 declared case evaluations, 22 false controls rejected |

The review retained factorial normalization loss, packet/degree index conversion, zero and empty-tail cases, positive period/displacement hypotheses, affine depth zero versus nonlinear positive depth, rectangular kernel freedom, and zero finite dimensions. Weighted statements keep `r>2s`, `M>2s`, the full depth-`s+1` uniqueness ball, displacement depths `r−s`/`M−s`, and error depth `2M−3s`. The joint forcing term is `H(a)+Kv`; the analytic derivative is `−J⁻¹K` over the ambient field and on the stated local neighborhoods.

All reported instructional issues are resolved: the direct Hurwitz prime-Leibniz check is now implemented; CRT states its actual dyadic/odd specialization; dyadic rescaling and affine images are explicit; a good selected coordinate split is distinguished from every imposed split; unit uniqueness follows the actual lifted-root argument; and the finite Mahler ring assumption is visible. Preliminary 677 excerpt lines included 54 terminal axiom-print lines. Final range sums, files and metadata consistently give 623.

The complete source/hash pins, corrected page/source locators, obligations, resolved findings and limitations are recorded in `GUIDE_REVIEW.json`. The finite computation manifest and result are separate from catalog/hash inspection. No unresolved mathematical or instructional discrepancy remains within the stated audit scope.

Frozen PDF SHA-256:

- Traditional: `62eea0640e249562e94211724b610b901925e9ee8ea8c5abfdab9a6d04dabe40`
- Visual: `305e5e0775a7135a0b1672ec3ed5a2912c72b9109e76aa7fd819d86225a08df0`
- Lean: `907ca0d581c90613b2967c2f763a15e848d9699c210dddddf7db10f8dc45cb76`
