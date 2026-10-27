# Building and checking the publication

## Required local software

Use Python 3.10 or newer, PyMuPDF (`import fitz`), Poppler (`pdffonts`), and a TeX Live installation providing `pdflatex`, standard mathematical packages, TikZ, tcolorbox, mathpazo, hyperref, cleveref, xurl, and the packages listed in the shared preamble. The original compiled PDFs are included for reading without installing any of these tools.

Run:

```bash
bash build.sh
```

The exact finite checks and archive/concordance checks use only the Python standard library. PyMuPDF and Poppler are used by PDF preflight. The script is offline and does not install a compiler, contact a service, or modify the original evidence archives. It regenerates current audit timestamps and PDF metadata, so rebuilt PDFs are not promised to be byte-identical across environments.

## Manual sequence

```bash
python3 checks/verify_sources.py
python3 checks/build_concordance.py
python3 checks/exact_examples.py
python3 evidence/moving_v032/scripts/run_exact_audit.py --output-dir audit/publication_fresh_finite
python3 checks/build_lean_guide.py
# Compile each source/Komorebi_Space_*.tex file with pdflatex three times.
python3 checks/publication_preflight.py
python3 checks/hash_manifest.py
```

## Lean replay is a different operation

The frozen projects target Lean 4.34.0-rc2 and mathlib revision `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. Extract each original archive separately and follow its README with a matching external runtime and dependency cache. Do not execute a foundation extension-replay script and describe that as a clean build of every production module.

The publication source views expose all production modules and selected supporting files, not every historical audit payload. Use the original ZIPs for the original full verification layout. A combined formal tree needs a separately reviewed integration of shared modules before a new compiler result can be reported.
