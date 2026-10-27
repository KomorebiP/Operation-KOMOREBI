# Riemann conjecture monograph source map

Prepared 2026-10-08. Author/release name: Komorebi P.

## Primary public dependencies

| Reference | Exact dependency | Verified source |
|---|---|---|
| DLMF 25.4 | Completed xi normalization and functional equation | https://dlmf.nist.gov/25.4 equations 25.4.3 and 25.4.4 |
| DLMF 25.10(i) | Nontrivial zero strip and symmetries, RH statement | https://dlmf.nist.gov/25.10 |
| DLMF 5.7.6 | Digamma series used to derive a linear vertical growth bound | https://dlmf.nist.gov/5.7.E6 |
| Báez Duarte 2005 | c_K criterion for every epsilon>0 and exact Mobius series | https://www.maths.tcd.ie/EMIS/journals/IJMMS/Volume2005_21/141565.pdf, Theorem 1.1 and equation 3.6 |
| Bondarenko, Radchenko, Seip 2023 | Unconditional Guinand-Weil explicit formula with multiplicities and zero counting asymptotic | https://link.springer.com/article/10.1007/s00365-022-09599-w, equations 1.1 and 2.11 |

The literature agent authenticated and read these sources. The article claims no priority for the classical c_K coefficient or its criterion.

## Recovered saved project sources

| Exact filename | Library identity | Role and boundary |
|---|---|---|
| FINAL_GAP_ATTACK_REPORT.md | libfile_1c5614b9f958819188dadb403c8f5e5e | v0.13 report. Focused historical Lean verification, analytic reductions, explicit failure modes. Does not assert RH. |
| PRIME_CUBE_PARITY_BARRIER_REPORT.md | libfile_305819eb53448191a7f82a7e7ef470b7 | v0.14 report. Exact cube decomposition and positive-tail idea, finite diagnostics. Corrected support and majorant proof in new manuscript. |
| Komorebi_RH_Master_v0.14.1_README_START_HERE.md | libfile_af467603e88c819194a0547ebf2853e5 | Checkpoint scope and warning. 377 cumulative entries, 104 distinct Lean contents, no cumulative certification claim. |
| Prime_Packet_RH_Heat_Kernel_Core.tex | libfile_e0584917ec6881918be904b9c689fa82 | Exact heat normalization, prime formula and Laplace-pole criterion. Manuscript proof. |
| GROUND_MODE_FRONT_IDENTITY.md | libfile_3c51d4e1bbb481919b05fb4ccfd9eb99 | Exact Gaussian test pairing. Analytic derivation, explicitly not Lean certified. |
| STABLE_HERMITE_COMPRESSION_REPORT.md | libfile_8ba3349f3e708191b9379fb4cbb46281 | Coherent expansion, Poisson tail, shell compression. Formula audits 144 plus 27 finite cases. |
| CLAIM_BOUNDARY(20260912-220305).md | libfile_79cfd5ba194481918b5e9a759ccd00e4 | v0.13 exact absence of arithmetic cancellation, no cumulative Lean rebuild. |

Every row was read in full. Recovered text is retained byte for byte as returned text content in `recovered/`, alongside complete JSON read evidence. No original evidence was silently edited.

## New manuscript work

- Self-contained proofs of one heat time boundedness and determinant criteria.
- Explicit local energy implication using an L2-in-time valued Laplace transform, avoiding an unjustified choice of one exceptional heat time.
- Explicit digamma domination on a positive heat strip, derived from the checked series.
- Exact full absolute majorant barrier which retains squarefree support. The squarefree-coprime count is derived by the identity mu(m)^2=sum_{l^2|m}mu(l), inclusion-exclusion, and an absolutely convergent Euler product.
- Exact signed conjecture stated for all integers K>=1, so no sparse-subsequence interpolation is assumed.
- Deliberate distinction between whole zero packets and finite localized L2 prime packets.

These are manuscript proofs. No new Lean kernel certification is claimed.

## Archive retrieval failure

A current download attempt for the resolved v0.13 and v0.14 checkpoint ZIP batch failed with HTTP 403. Exact identities and status were recovered through full readable saved reports and the core TeX source. This release does not embed unmaterialized Lean trees or claim to have freshly rebuilt them.

## Figure boundary

The new figures are exact programmatic plots or explicitly labelled mathematical illustrations. The finite xi plot does not verify all zeros. The heat-front illustration uses hypothetical mode amplitude envelopes, not observed off-line zeros. The barrier plot illustrates the proven exponents, not measured Mobius cancellation. The Hermite plot illustrates a basis, not a measured spectral gap.
