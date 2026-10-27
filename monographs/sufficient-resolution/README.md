# Sufficient Resolution

Komorebi P. - Final paper set, October 6, 2026

This set develops the existing Sufficient Resolution v0.16.0 contracts in three complementary forms. The traditional paper gives the mathematical argument. The visual guide develops worked examples and geometric explanations. The Lean guide relates formulas and hypotheses to the formal source and verification records.

The traditional manuscript consolidates 64 principal result groups across all sixteen blocks, with proofs and a declaration concordance. These are editorial groupings of the existing source, not a claim of 64 independent new discoveries. Both companion guides map back to these same groups.

## Reading set

- `traditional/Sufficient_Resolution_Traditional.pdf`
- `visual/Sufficient_Resolution_Visual_Guide.pdf`
- `lean/Sufficient_Resolution_Lean_Guide.pdf`

Each document has an editable `.tex` source and a `.md` counterpart. The complete source ZIP includes these Markdown files, figure-generation code and figures, the formal source, example data, replay tools, and verification records. The source-availability notes in the documents refer to this complete bundle.

## Mathematical scope

The algebraic theory includes split and redundant representation, compatible coordinate operators, hidden-return composition defects, discrete memory, behavioral sufficient quotients, finite-horizon certificates, and approximate error transport. Analytic extensions treat bounded continuous-time flows and Hilbert-space obstruction, reconstruction, regularization, discrepancy, operator uncertainty, and calibration frames under their explicitly stated hypotheses.

The task and permitted continuations are part of the behavioral model. Reconstruction theorems retain their noise, conditioning, closed-range, source ambiguity, and parameter assumptions. Strong and uniform convergence are distinct. Calibration fitting requires a separately justified calibration-truth error allowance. A theorem asserting existence or using a noncomputable choice does not itself supply an executable search algorithm.

Sample-wise calibration uncertainty, a direct bridge to stable target-only prediction, formal verification of the Python implementations, and the broader constrained/nonlinear/geometric realization directions remain identified research problems. Publication of the completed contracts does not assert completion of those directions.

## Formal source and evidence

The cumulative v0.16.0 source has 93 production modules and 998 theorem/lemma declarations, within 1,159 enumerated named declarations. Supporting definitions, helpers, examples, and specializations are included in these inventories. The declaration count is not a count of independent discoveries or a whole-program completion percentage.

The original checkpoint is retained unchanged at `provenance/Komorebi_Sufficient_Resolution_Lean_v0.16.0.zip`. Its SHA-256 is `ebb2d71a211ea9938c1b223f9858d5636d0973b5aa519244667200646b832ff4`. The `formal/` directory contains the release-use source and tooling. The production Lean files are preserved byte-for-byte; release tooling and current documentation are identified separately from the inherited records.

Archived v0.16.0 verification compiled the latest block's 31-module dependency closure plus its block root in two final runs, audited 52 new named declarations, and performed same-kernel replay. A fresh full 93-module replay was not part of that historical verification. The final release verification report records the exact checks completed for this paper set and any runtime-recovery limitation. Python checks supply bounded implementation evidence; they are not formally verified code or substitutes for general mathematical proofs.

For this edition, all sixteen finite Python suites passed, reporting 40,466 native counted assertions, plus five fixed sanity groups with six main assertions. The visual examples separately passed 280 exact rational assertions. Eighteen current computation manifests (seventeen base records and one visual-example record) pass schema and live artifact-hash checks. These overlapping checks are not aggregated into a count of distinct mathematical facts.

A fresh Lean compilation, axiom audit and proof-kernel replay were **not run**. Both attempts to recover the essential first runtime chunk failed with HTTP 502. The archived source evidence is retained, and the matching runtime is required for a future full replay. See `verification/RUNTIME_RECOVERY.json` for the actual attempts and `verification/CURRENT_RELEASE_VERIFICATION.json` for the completed checks.

## Rebuilding and replaying

With a suitable TeX distribution installed, run `python3 build_release.py`. It makes three pdfLaTeX passes for each document. Consult the individual guide directories for regenerating figures and editable Markdown.

The formal toolchain pins are Lean 4.34.0-rc2, commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`, and Mathlib revision `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. Follow the Lean guide and release-use runner instructions for a serial build. A matching Lean/Mathlib runtime and dependency cache are prerequisites; the runtime is not bundled in this paper set.

Use the verification records to distinguish freshly executed computation from archived proof-check reports. Historical records retain their original commands and paths as provenance; copying a record into this bundle does not constitute a new run.

`package_release.py` regenerates the complete ZIP, `BUNDLE_INDEX.json`, and `SHA256SUMS.txt`, and independently verifies every indexed payload after ZIP creation. Document authoring caches and rendered review pages are excluded from the distribution ZIP.

## Release review

The `reviews/` directory records the mathematical scope review, traditional-paper review, visual review, Lean-guide review, computational review, and cross-document consistency review. These reports state their actual coverage and dependency boundaries.

This is a private publication handoff. It does not select a new distribution license or publish an external repository.
