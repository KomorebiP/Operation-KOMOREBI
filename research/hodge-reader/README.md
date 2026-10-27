# Operation Komorebi: Hodge

Conjecture Series 06. Komorebi P. Reader edition 1.0, 9 October 2026.

Begin with the monograph in `pdf/`. The landscape visual guide is a companion with worked examples and explicit diagrams. This edition does not prove the general rational Hodge conjecture. It separates exact identities, manuscript arguments, imported geometric theorems, finite computation, and unresolved algebraic correspondence constructions.

## Build the PDFs

From this folder:

```sh
python3 build.py --figures
python3 validate_fonts.py
python3 quality_check.py
```

The build requires Python 3, NumPy, SymPy, Matplotlib, Pillow, PyMuPDF, TeX Live with the listed LaTeX packages, and Poppler. Exact versions used for this edition are recorded in `evidence/AUTHORING_ENVIRONMENT.json`. Compilation runs until cross-references stabilize. The resulting content is reproducible from the sources. A different TeX environment or timestamp can change PDF bytes.

## Read the evidence

- `evidence/PROOF_AUDIT.md` and its claim cards record the current audit verdicts, hypotheses, and gaps.
- `evidence/computation/` contains fresh bounded runs, exact check scripts, inputs, raw logs, and computation manifests. Historical counts are distinguished from new replays.
- `evidence/literature/` records checked primary sources, notation translations, attribution corrections, and source-access limits.
- `evidence/formal/FORMAL_STATUS.md` explains the existing Lean file's actual assumptions and the failed current compiler probe. The edition claims no current Lean pass.
- `evidence/originals/` preserves the recovered historical artifacts unchanged. `evidence/recovered/` contains their extracted contents. Historical theorem labels and success flags are not automatically endorsed by this edition.
- `evidence/RECOVERY_INPUTS.json` pins the recovered source bytes. The release manifest pins all packaged files.

The general Hodge infrastructure needs actual algebraic cycle classes and typed correspondences. A positive compressed Gram form, matching CM types, or a finite packet census alone supplies neither. The current degree-70 carrier and degree-210 transfer are special-case manuscript arguments with separately checked arithmetic. The five-phase cycles reproduce Aoki's known construction. The K23 program still requires an explicit algebraic correspondence at the stated construction boundary.

Original source archives contain discovery scripts and older reports. Use the current audit and reproducibility instructions to distinguish authoritative verification from exploratory records. Failed proposals and invalid discovery inputs are retained as evidence and are excluded from positive conclusions.
