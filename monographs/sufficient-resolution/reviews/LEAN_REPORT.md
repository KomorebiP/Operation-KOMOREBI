# Sufficient Resolution: Lean guide release review

**Author:** Komorebi P.  
**Edition:** October 6, 2026  
**Status:** PASS for source mapping, publication build, and bounded editorial review. Fresh Lean compilation was not performed.

The consolidated Lean guide is delivered as `lean/Sufficient_Resolution_Lean_Guide.pdf`, `.tex`, and `.md`. The PDF has 30 pages and the Markdown preserves all 47 mathematical display blocks plus the full module census and 64-claim appendix. Its cover and source-availability notice explicitly confirm inclusion of Markdown and editable source files.

## Source inventory and claim correspondence

The regenerated registry contains 93 production modules, 998 theorem/lemma declarations, 144 definitions, nine abbreviations, and eight structures: 1,159 explicitly named declarations. These counts include helpers, examples, definitions, and classical specializations. Automatically generated structure-field names are not included in this textual count.

`Declaration_Inventory.csv` and JSON contain every named declaration, source file, line, block, declaration-start text, and source SHA-256. `Module_Inventory.csv` and JSON contain every production module, line/byte counts, declaration categories, local/external imports, and full source hashes. A comment/string-masked namespace scan agrees exactly with the inherited v0.16 index. This is textual inventory, not elaboration or proof verification.

The guide's 135 inline declaration-anchor occurrences resolve to 133 distinct actual source names. The traditional paper's 64 stable IDs SR-01 through SR-64 map to 295 representative declaration occurrences, 294 unique names. The curated Lean concordance preserves the paper's exact plain-text and printed TeX hypotheses, formulas, dependencies, status, source kinds, and hashes, adding source-line locations. Every named anchor and source hash resolves. A final live comparison confirms all 64 hypothesis/formula synopses and all declaration arrays equal the current canonical register. Its SHA-256 is `0876e7a6040ec46ce1af1ab147246c7da741e1880106dcfe2707d18e48be2a83`, recorded in `lean/CLAIM_MAPPING_AUDIT.json` and `lean/PUBLICATION_QA.json`.

All 93 production proof sources are unchanged. The current full-corpus verification driver, source audit wrapper, and release metadata were repaired separately; the guide distinguishes those orchestration changes from changes to mathematical proof sources.

## Formal coverage and boundaries

The narrative covers all sixteen development blocks: split representation; compression and actual obstruction; exact discrete memory; behavioral quotients and finite minimality; discrete and continuous approximate bounds; bounded operator exponential and Volterra memory; orthogonal and intrinsic obstruction geometry; minimum-norm reconstruction; Tikhonov construction, sensitivity, and limits; discrepancy selection; protected inexact certificates; changing operators; source-bound-free generalized discrepancy; and calibration-to-operator bounds.

The guide retains whole-map hypotheses, commutative-ring versus field domains, finite alphabet for finite certificates, finite hidden dimension, orthogonal-projectability gates, actual range versus range closure, strong versus uniform convergence, source-kernel ambiguity, positive parameters, protected residual budgets, generalized feasibility, and external calibration-truth allowances. Calibration recovery explicitly uses real Hilbert source/data spaces, fixed true operator and split frame, and fixed nonnegative discrepancy factor. It identifies the generalized selected-source constructor as a noncomputable theorem-level witness with true-operator/comparison-source/proof arguments. It does not describe that constructor as an executable available-data API.

Classical Mathlib support is credited for quotient modules, Cayley–Hamilton, projection theory, Banach open mapping, exponentials/integration, adjoints, Lax–Milgram, and the intermediate value theorem. Moore–Penrose and Tikhonov objects are identified as classical. No novelty or priority certificate is asserted.

Open boundaries remain visible: sample-wise calibration-truth bounds, stable target-only recovery from the behavioral quotient, verified or extracted Python, constrained/nonlinear/positive/integral and varying-metric settings, unbounded-generator domains, and arithmetic existence.

## Evidence status

The exact pins are Lean 4.34.0-rc2, Lean commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`, and Mathlib revision `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.

The latest archived September 14 records document two separate source-tree runs, each compiling the 31-module Block 16 dependency closure plus the block root, inspecting 52 new named transitive-axiom reports, and performing same-kernel replay on that closure. A fresh full 93-module corpus replay was not run historically. Earlier blocks have separate archived evidence.

The production axiom allowlist is `propext`, `Classical.choice`, and `Quot.sound`. Same-kernel `leanchecker` replay is not an independent verifier implementation. Pinned imported Mathlib proof artifacts were reused, not rebuilt from first principles.

Fresh final-edition finite replay passed all 16 Python suites: 40,466 native counted assertions, five additional sanity groups (six main assertions), and 1,073 reported rejected controls. All 17 current v2 manifests passed root and live-hash validation. These are bounded implementation checks with suite-specific norms, not universal proofs or formal verification of algorithms and parsers.

The full-corpus runner plan and 1,159-name audit wrapper correspondence were checked from source. No new transitive axiom commands or Lean proof compilation were executed. The proof runtime and cache are absent. Two attempts to recover the first compact-runtime chunk returned HTTP 502, preventing restoration. The guide records the failure and includes a realistic serial low-memory workflow for an independently restored matching runtime.

## Publication and self-review

Three-pass pdfLaTeX compilation succeeds. The final root command `python build_release.py --only lean` used deterministic source-date settings. Its PDF SHA-256 is `680f73f0f05bfacf96abd23816a30bb34cba22c4a791c3bd3b6a96fffe37b976`. The final log has no undefined references/commands, warnings, underfull boxes, or overfull boxes. Rotation-aware bounds checks pass for every text span on all 30 pages. Representative cover, contents, formal-contract, formula, reconstruction/certification, and claim-appendix pages were rendered and visually reviewed. The contents fit on one page, claim columns use available width, and inline constructor/option code preserves meaningful spaces.

Conservative proofreading covered the entire newly authored guide, formulas, source anchors, generated inventories, and curated claim appendix. Routine edits corrected authoring-time source-name aliases, compiler support for Pandoc listings/tables, inline-code spacing, and table alignment. No mathematical tokens or proof bodies in production Lean sources were changed. One precision improvement states that vanishing calibration errors give the retained convergence result for a fixed bounded split frame; unbounded changing reconstruction norms are not silently covered.

Authoring failures were resolved: the first Markdown-to-TeX build required handling Pandoc's inline-listings wrapper and `calc` table syntax, escaped underscores required normalization, and the first narrow claim table had underfull boxes. The final source and PDF pass. The only unresolved execution limitation is absence of the matching Lean runtime after failed transfer recovery.

`lean/PUBLICATION_QA.json` records the reviewed PDF hash; if a later root build recompiles it, refresh that hash or use the root final publication audit as authoritative. Final user-facing artifacts are saved by the root release workflow.
