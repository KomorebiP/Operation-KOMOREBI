# Independent publication review

Review date: 2026-10-07. Mode: conservative mathematical proofreading and publication QA. This review does not replace the separate proof audit, numerical validation, or Lean build.

**Final publication verdict: passed for the reviewed scope.** All three final PDFs were inspected, with no unresolved objective proofreading or layout finding. The separate reports state the mathematical, numerical and formal verification guarantees.

## Coverage completed

- Traditional manuscript: all changed material relative to the supplied v1.9 manuscript, the integrated packet section, scope classifications, historical-evidence wording, bibliography and cross-references.
- Final 84-page traditional PDF: every page inspected in seven contact sheets after all corrections and completed fresh-validation/Lean appendices. Structural preflight reported no page-bound overflow or replacement glyphs; no clipping or overlap was visible. An initial 81-page draft was also checked before completion.
- Final traditional source has 161 distinct labels, no duplicate labels or missing references, and matching environment counts. The two companion sources also have matching environment counts. No final source contains the stale v1.7 candidate title. Exact source-check hashes are in `PUBLICATION_SOURCE_CHECK.json`.
- Lean companion source: finite-algebra and enclosure-composition model, all 26 declaration names against both mathematical modules, hypotheses, normalization, reproduction instructions and remaining formal obligations.
- Final 8-page Lean guide: every page inspected after pagination improvements. Structural preflight reported no page-bound overflow or replacement glyphs. The completed summary agrees with the recorded successful build and axiom audit: 26 theorems, 8 definitions, 34 audited declarations, no `sorryAx` or custom axiom. The verification controls are correctly described as accepted-valid and rejected-invalid proof checks.
- Visual plotting source: declared integer Gram/cone/residual identities and illustrative floating packet and mode-decay controls. The final Erlang-law curve uses Python Decimal at precision 90; it is a point-arithmetic illustration, not an interval certificate.
- Final 18-page visual guide: full source, every rendered page in two contact sheets, all figure captions, formula domains, and guarantee classifications. Structural preflight reported no page-bound overflow or replacement glyphs; no clipping or overlap was visible.
- Fresh validation text: 58 selected test methods, split into 48 production methods and 10 directed regressions; final nonfinite-only guard amendment and earlier finite-run source hashes are explicitly distinguished. Displayed deep-tail and matrix-tail ratio upper bounds round outward and match the fresh report.
- Source preservation: all 39 Markdown files in the v1.9 provenance archive have byte-identical extracted copies in the final release tree. The packet v0.1 provenance archive contains no Markdown files.

## Findings resolved by the manuscript owner

1. Added explicit nonempty-packet and nonnegative-integer expansion-order hypotheses.
2. Added common COS domain conditions and an explicit positive integer mode count for the combined theorem.
3. Marked archived numerical claims in prose, including the abstract and conclusion; the initial date qualification had covered tables and plots only.
4. Visual packet formulas now state the nonempty packet, integer order, transform half-plane and logarithm branch conditions.
5. Visual acceptance text now specifies a directed ratio upper endpoint versus an exact-tolerance lower endpoint, with preserved literal outer endpoints.
6. Visual central reduction now explicitly assumes PSD covariance and symmetric quadratic matrix; the primed cosine sum is conventionally typeset.
7. Lean contents now occupies one page; all declaration rows remain together after a local table-font adjustment.

No mathematical-token change was made by this reviewer. The author owns the hypothesis and evidence-wording corrections above.

## Unresolved findings

None within this review's coverage. Render inspection covered all 110 final PDF pages (84 traditional, 18 visual, 8 Lean). Full underlying historical experiment regeneration and additional probability formalization were outside this publication-review task.

One minor reviewer finding was withdrawn: an earlier generator revision used mpmath, but the final Decimal implementation correctly supports the visual caption's description of decimal arithmetic. No unresolved visual finding remains.

## Guarantee boundary

The traditional text distinguishes exact structural inequalities, real-arithmetic analytic probability ledgers and directed numerical enclosures. The focused Lean companion covers finite Gram identities, refinement/action invariance, positivity, pointwise coefficient order and consequences of already supplied enclosures. It does not imply a full Lean certificate for Gaussian reduction, spectral inclusion, probability coupling, COS inversion/remainders or interval-library correctness.
