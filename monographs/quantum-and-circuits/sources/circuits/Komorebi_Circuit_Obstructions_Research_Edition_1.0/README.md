# Circuit Obstructions: research edition 1.0

Komorebi P. · 7 October 2026

This set provides a main paper, a visual guide, and a Lean guide for the fixed
Circuit Obstructions claims C01–C08. The source baseline is local release
v1.2.0, Lean Block 02. Original releases, checkpoint archives, source documents,
and verification evidence remain preserved.

The central archived formal endpoint for a legal restored classical
NOT/CNOT/Toffoli implementation of `(x,0^a,b) -> (x,0^a,b xor f(x))` is
`DegreeLE (T+1) f` and `2 * betaStar f <= T+3`. The shared-register invariant
allows dirty intermediate workspace, temporary input disturbance, and output
feedback. Restoration for every input and both initial target values is a
theorem hypothesis.

## Reading order

1. Main paper: full definitions, written proofs, calibration results, exact
   projection examples, witness algebra and trace arguments.
2. Visual guide: exact finite fixtures and reproducible Python figures.
3. Lean guide: actual formal types and dependencies, all 115 theorem
   declarations, archived verification, and commands for a compatible toolchain.

The broader claim group C02 includes an evaluation-span dual and affine-input
arguments outside the Lean block. C03–C08 have written arguments and declared
finite evidence. They are not promoted to formal proofs by this edition.

## What was run in this edition

The complete exact Python/C++ verification (`scripts/verify.py --all` in the
source repository) passed, including fresh small-domain profiles, current
scientific checks, Block 02 degree controls, and the preserved historical runner.
The original source seal passed. Additional bounded review scripts and exact
visual fixtures are supplied with their own scopes.

A fresh Lean replay was attempted and failed before proof checking because the
`lean` executable is unavailable. The 21 September successful build, axiom
audit, eight module replays and eight rejected negative controls are preserved
as archived source-bound evidence. There is no new kernel-pass claim.

PDF builds and rendering have separate records. A PDF build, a finite test, a
source-hash check and a proof-kernel check establish different things. Counts
across overlapping suites are not added together.

## Reproduce

The source repository needs Python 3.10+ and a C++17 compiler for `--all`.
It needs no external Python packages or network access for its scientific
checks. Run from `source/komorebi-circuit-obstructions-v1.2.0`:

```sh
python scripts/check_integrity.py
python scripts/verify.py --all
```

For Lean, separately install or supply the pinned Lean 4.34.0-rc2 toolchain.
Only bundled Std is used, with no Mathlib dependency:

```sh
python scripts/verify_lean.py --toolchain /path/to/toolchain
```

For publication figures install matplotlib and NumPy in a Python environment.
For documents use TeX Live with the supplied package dependencies, including
Latin Modern and Palatino support. Poppler, PyMuPDF and Pillow support review.
Run from the publication-set root:

```sh
python scripts/make_figures.py
python scripts/build_main.py
python scripts/build_lean_register.py
python scripts/build_lean_guide.py
python scripts/build_documents.py
python scripts/verify_publication.py
```

The original historical theorem source is included because `build_main.py`
constructs the consolidated traditional manuscript from it and documents the
edition changes. The complete original source ZIP and Git bundle are also
included unchanged. Source and PDF hashes are listed in the publication manifest.
To verify an extracted set without rebuilding it, run
`python scripts/verify_package_manifest.py` from its root. For the delivered
ZIP, pass `--zip /path/to/the/zip`. The manifest checks every included file's
size and SHA-256; it is a content check rather than an authorship certificate.

## Scope and attribution

The work was developed with AI assistance. Model-assisted reviews are supplied
but do not constitute independent human review. General-circuit lower bounds,
P versus NP, an efficient weighted-trace evaluator, and exhaustive novelty
claims are outside this edition's scope. The original rights record is
preserved. No new distribution licence, DOI or public hosting status is assigned.
