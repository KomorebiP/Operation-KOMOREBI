# Source and claim map

## Authoritative input

Library handoff `PRSC_Paper_VIII_Latest_v0.6.0_Finite_Register_Complete.zip`, containing `PRSC_VIII_v0.6.0_Checked_Sixth_Block`. The current record is the 392-declaration, 40-module, 56-item branch. File IDs and hashes are recorded in `PRESERVATION.json`.

The original manuscript is **Packet Operator Algorithms, Exact Compilation, and GPU Realization**, 45 pages. Its eight-page sixth-block supplement carries the final small-core proof and exact scope. The combined reader edition keeps both unchanged before the 28 appendix pages. Earlier supplements and the original numerical package remain available in the source trees.

## Appendix map

| Visual page(s) | Original material | New worked content |
|---|---|---|
| 1–2 | Sections 2–3, 8–11; sixth supplement | Operator, factors, compilation, input/output and evidence distinctions. |
| 3–4 | Theorems 2.3, 3.1, 3.4; count/capacity results | A fully populated 6 by 6 operator with an exact BDLR description; modeled work/storage and active block counts. |
| 5–8 | Theorem 4.3, Corollary 4.4, Theorems 4.5 and 4.7 | Exact complex Fourier multipliers, Toeplitz padding, transpose-sensitive vectorization, and all Walsh butterfly stages. |
| 9–10 | Theorems 5.1 and 5.3 | Actual thin product factors with the quadratic cross term and a Woodbury inverse with its indispensable small denominator. |
| 11–12 | Theorem 5.6 and sixth supplement pp. 2–6 | Rank-deficient stored factors reduced to their true ranges; exact core tails; compression of an outside competitor; explanation of both lower-bound mechanisms. |
| 13 | Theorems 5.7–5.8 | Factor perturbation versus post-product recompression; exact amplification of local errors. |
| 14–16 | Sections 2.1 and 6 | Coefficient cancellation behind permitted paths, exact topological triangular solve, Schur fill and cancellation. |
| 17–18 | Propositions/Theorems 7.2–7.6 | Strict global/local Krylov inclusion; exact normalized coupling and a sharp Jacobi condition bound. |
| 19–20 | Theorem 8.1, Theorems 8.4–8.5, Proposition 9.2 | Coherent block error, distinct matrix norms, input sensitivity, and a clipped precision allocation. |
| 21 | Theorem 8.7 and Remark 8.8 | All 27 precision assignments checked against the exact-weight recurrence; conservative rounding. |
| 22–23 | Section 9.2–9.4 | All five candidate-tree prunings; unsupported budget optimum; exact local recompilation and strict decision margins. |
| 24–26 | Sections 3.2, 10–11 | Shape classes, one-pass byte counts, synthetic reuse threshold, and output-aligned benchmark comparisons. |
| 27 | Theorems 2.3, 3.4, 5.1 | Product factors applied to the original running input and checked against a separately formed dense reference. |
| 28 | Sixth supplement and current ledger | Separation of saved formal evidence, new examples, numerical software tests, and historical device observations. |

## New evidence and limits

`visual_appendix/checks/EXACT_CHECKS.json` records the exact/symbolic positive assertions and deliberately false alternatives. These are particular checks, not new universal proofs or expanded Lean coverage. The vector plates are generated deterministically from arrays and formulas. Sampled coordinates used to draw curves are not precision certificates.

The inherited Python package tests, verifier-software tests, and numerical small-core mirrors were replayed in working copies. Floating-point mirrors retain their tolerances; replotting a saved timing corpus is not hardware replication. The original manuscript's figure generator and TeX source were rebuilt and compared with the shipped pages. Current editorial commands and results are distinct from saved Lean compiler records.

No source theorem, formal hypothesis, original figure, or saved benchmark row was modified. The full source release does not certify an unrestricted optimizer, a GPU kernel implementation, numerical QR/SVD, general SVD existence, or a generic dense-matrix exponent. Those claims are not added by the visual appendix.
