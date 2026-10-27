# Building and checking edition 1.1.0

## Read without installing software

The three PDFs are in `publication/`. Their fonts are embedded. No font files or Lean runtime are distributed in this package.

## Local software for a publication build

Use Python 3.10 or newer, NumPy and Matplotlib for numeric plots, PyMuPDF (`import fitz`) for PDF inspection, Poppler (`pdffonts`), and a TeX Live installation providing `pdflatex` and the packages declared in `source/preamble.tex` and `source/komorebi-publication.sty`. The tested Python package versions are recorded in `requirements-publication.txt` and `audit/build_environment.json`.

The exact examples, rational certificate program, archive integrity checks, and static local import inventory use the Python standard library. They do not need NumPy or a GPU. Optional contact-sheet rendering uses Poppler's `pdftoppm` and Pillow.

```bash
python3 checks/verify_payload.py
bash build.sh
```

The script is offline. It does not install dependencies, contact a service, modify original evidence archives, or run Lean. It overwrites current execution reports and PDF metadata, so a rebuilt package needs a new manifest. Mathematical reproducibility does not promise byte-identical PDF metadata across environments. The visual-review record belongs to the specific PDF hashes listed there; a new rendering still needs inspection.

## Steps performed by build.sh

```bash
python3 checks/verify_sources.py
python3 checks/build_concordance.py
python3 checks/static_integration.py
python3 checks/exact_examples.py
python3 checks/revision_exact.py
python3 examples/protected_repair.py --demo > examples/three_preservation_problems.json
python3 checks/build_figures.py
python3 evidence/moving_v032/scripts/run_exact_audit.py --output-dir audit/publication_fresh_finite
python3 checks/edition_stats.py
python3 checks/build_lean_guide.py
# Compile each source/Komorebi_Space_*.tex with pdflatex three times.
python3 checks/publication_preflight.py
python3 checks/hash_manifest.py
```

The recovered focused checker resolves its output directory relative to its own historical project. Its current reports therefore appear under `evidence/moving_v032/audit/publication_fresh_finite/`, not the top-level `audit/` directory. Original frozen replay ZIPs remain unchanged.

For visual inspection after rebuilding:

```bash
python3 checks/render_review.py /tmp/komorebi-space-review --dpi 100
```

This creates page PNGs and labelled contact sheets outside the publication package. Inspect figures, labels, theorem breaks, contents, and the concordance. Mechanical preflight is not a substitute for visual inspection or mathematical proofreading.

## The finite certificate interface

`python3 examples/protected_repair.py --demo` needs only the standard library. A custom JSON file must contain `A`, `P`, and `x`. Use integers or rational strings, not floating-point numbers. Malformed input exits with code 2. A valid but obstructed problem is a successful mathematical classification. The certificate alternative is proved in the manuscript; the Python implementation has exact bounded regression evidence, not a universal Lean refinement proof.

## Lean replay is a separate operation

The frozen projects target Lean 4.34.0-rc2 and mathlib revision `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. Extract each original archive separately and follow its README with the matching external runtime and cache. The readable source views in this publication do not replace the full historical audit layout preserved in the ZIPs.

The current static audit identifies 133 distinct production module names across the two trees and the selected Hilbert source. It finds one byte-identical shared module and proposes an acyclic local import order. External mathlib imports are only enumerated, not loaded. The two old root modules remain distinct.

A new cumulative formal release must materialize a canonical source tree, choose a root, restore the pinned compiler and dependencies, compile every project module from a clean project build directory, inspect imported axioms, and rerun positive and negative controls. The selected Hilbert module and the new root must be included in that audit. None of these compiler or axiom steps is asserted to have occurred in this publication revision.
