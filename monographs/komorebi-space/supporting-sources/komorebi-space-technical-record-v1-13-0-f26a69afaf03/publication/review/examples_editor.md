# Computational example editorial review

Scope: `examples/README.md` and `examples/INEXACT_CERTIFICATES.md`, followed by explicitly authorized public string edits in `budgeted_repair.py` and its supplied demonstration JSON. The other three programs and other four JSON files retain their original bytes.

## Changes

- Replaced an incomplete historical README with an accurate guide to all four Python CLIs.
- Removed internal theorem IDs, obsolete section numbering, and obsolete claims about the absence of formal counterparts.
- Added an actual regularized-solver command, correct input fields, dimension restrictions, and the interpretation of the returned budget.
- Added a complete inexact-certificate input and create/verify workflow, with exact expected values checked against execution.
- Preserved the distinction between measured fit, actual residual, a Hilbert normal certificate, and the raw coordinate-covector norm.
- Kept computational evidence finite and scoped. No universal Python-to-Lean implementation claim is made.
- Updated four Python text literals/docstrings only: the description of the default demonstrations, the dual-witness docstring, and the two public scope strings. Updated the corresponding five JSON `scope` fields. No function/API names, algorithms, formulas, numerical values, schemas, or numerical JSON content changed.

## Validation

`build/examples_editor/verification.json` records ten exact commands with their working directory, exit code, output paths, output hashes, Python version, and source hashes. Nine positive commands succeeded. A certificate with an altered normal-residual norm was rejected as intended with exit code 2. All four fresh default outputs match the supplied demonstration JSON files. The custom certificate's displayed numerical values all match execution. The documented approximation command produces the requested depth and trajectory length.

The Python abstract syntax trees are identical after masking text literals. An explicit recursive JSON comparison found exactly five changed strings, all under `scope`, and no other difference. `build/examples_editor/string_changes.diff` records the complete executable/data edit. The before-source snapshots and hashes are retained in the same evidence directory.

## Proofread-math self-review

Routine edits: prose, mathematical explanations, file references, command examples, and Markdown structure.

Mathematical-token changes: none to existing algorithmic formulas or numerical inputs/outputs. The guide now states the existing normal-covector and Gram-metric identities explicitly.

A documentation-writing command initially interpreted two LaTeX `\alpha` escapes as control characters. The subsequent text scan caught both occurrences; they were corrected before final validation. No program or JSON mathematics was affected. Final Markdown has no unexpected control characters, and all code fences and display-math delimiters are paired.

No broader regression suite was rerun. This work validates the documented finite examples and preserves the computational algorithms. General results remain supported by their printed proofs and the separately stated formal scope.

Status: frozen for publication packaging.
