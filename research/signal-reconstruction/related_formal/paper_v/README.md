# Projector-Resolved Seed Calculus V, v1.1.0

Author: Komorebi P.

**The full manuscript has been proofread and expanded to 39 pages. All 20 theorem-like results have explicit proofs and reviewed Lean counterparts: 225 checked theorem targets in 23 modules.**

Read `manuscript/Paper_V_Expanded_Lean_Checked.pdf`. This is the current complete manuscript; its corrections and formalization appendix are integrated. The original 31-page PDF and earlier correction supplement are retained as historical material, not as additional instructions needed to read this edition.

The fresh checks cover the pinned Lean build and namespace axiom audit, the recovered original companion's 33 tests, 20 independent exact-model tests, 16 verifier controls, all original numerical results, and regeneration of 18 figure pairs. The full numerical JSON reproduced exactly in this environment. The combined entry point also rebuilds the paper, checks its numbering and references, compares extracted PDF text, and renders every page.

## Read alongside the paper

- `REVIEW.md`: corrections, expansion, evidence, and limits.
- `THEOREM_LEDGER.md`: all 20 results with current page numbers and exact scope.
- `MANUSCRIPT_TARGET_MAP.md`: qualified principal Lean declarations.
- `CUMULATIVE_COUNTS.md`: the Papers I–V census and duplicate-counting rules.
- `verification/paper_release_status.json`: combined release result.
- `verification/verification_status.json`: actual Lean build/audit result.
- `provenance/expanded_manuscript.patch`: exact source changes from the recovered original.

## Main repairs

Channel delay is distinguished from original-sample delay; numerical bilateral transforms carry summability hypotheses; finite Laurent/FIR filter banks have a faithful operator interpretation. Tree selection handles singleton trees and ties, and states its unit-operation cost model and joint-probability hypothesis. Mask bounds specify measurability and distinguish pointwise from essential supremum. Smith actions live on the projective line, including zero and infinity. The formal power-series identity includes exponent zero. The 1D Fourier cutoff 18 is correctly described as 37 frequency bins, and the figure axis now uses that convention.

The paper's two edge-recovery conjectures remain open. Classical physical context, numerical code, and historical priority are not additional Lean-certified results. PDF-to-Lean correspondence is a manual review; successful compilation does not automatically certify English prose.

## Reproduce

Install the pinned Lean toolchain and Python packages in `companion/requirements.txt`, plus pdfLaTeX, Poppler, and `pypdf`. In `formalization/lean`, obtain dependencies with `lake exe cache get`. Then run from this release root:

```text
python3 VERIFY_PAPER.py
```

`python3 verification/verify.py` runs the Lean/source/exact-test subset. `python3 -O verification/verify.py --static-only` performs source and exact-model checks without a Lean claim. Missing prerequisites or a failed gate cause failure.

The pinned Lean version is 4.34.0-rc2; mathlib is aeb72f1e9981b6d35b426b16dca7759be3e7ba06. The audit permits only propext, Classical.choice, and Quot.sound. The 827 audited namespace declarations include definitions and generated declarations; they are not 827 additional theorems. Build caches and toolchain binaries are excluded. The container-specific executable-path adapter is disclosed under `verification/runtime/` and is unnecessary on ordinary installations.

## Completion boundary and counts

Within its explicit finite/formal scope, the manuscript's 20-result contract is complete. Universal edge recovery, infinite-tree consistency, minimax rates, and optimal Smith sampling remain outside it.

Across Papers I–V: 168 manuscript theorem-like results; 1,456 raw mapped theorem targets; 1,443 after removing two shared qualified names and eleven known Paper-IV-to-V proof adaptations. This is a source census, not a count of independent new mathematics. Papers I–IV counts and audit status come from their release artifacts; Paper V was freshly checked here.
