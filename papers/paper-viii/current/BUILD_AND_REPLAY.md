# Paper VIII: build and replay

Release closure: 10 October 2026. Run commands from the extracted package root.
Keep the delivered tree immutable. Run tests in a working copy and send build
reports outside the package when validating its original manifest.

## Requirements

Python 3, XeLaTeX and BibTeX are required to build the PDFs. Python packages used
by the build and comparison include PyMuPDF and fontTools. The numerical and
figure replays use NumPy, SciPy, pandas, matplotlib, SymPy and pytest. The actual
versions used here are in `verification/closure_2026-10-10/ENVIRONMENT.json`.
No installation is performed by the build or test commands.

The editable folders contain `FONT_DEPENDENCIES.json`, not font binaries. Install
compatible URW Base35, Latin Modern and DejaVu Sans Mono fonts locally. The resolver
searches Fontconfig, TeX's `kpsewhich`, standard platform directories, and the
optional `KOMOREBI_FONT_DIR` environment variable. That variable can contain one
or more local directories separated by the platform path separator.

The resolver compares literal hashes or semantic SFNT table fingerprints. Only
FFTM build-time metadata and the head checksum adjustment are excluded from the
semantic fingerprint. Outlines, character maps, metrics and naming tables are
not excluded. It fails explicitly when no compatible font is installed.
The builder falls back to `bibtex.original` when `bibtex` is unavailable.
The fonts are staged only in a temporary build directory.

## Read-only delivery checks

```bash
python scripts/verify_integrity.py
python scripts/check_publication_consistency.py
python scripts/build_pdfs.py --check-only --report ../paper-viii-build-replay.json
```

The check-only build compares page counts and exact per-page extracted text;
full PDF byte equality is reported separately. In the recorded final replay,
all three comparisons and all three byte identities passed. This does not
promise identical pagination under arbitrary TeX installations. A mismatch must
be investigated rather than accepted by weakening the test.

The consistency check verifies active PDF copies, metadata, companion locators,
internal links, current source pins and current bounded-run manifests. It is
read-only. It does not execute Lean or perform device benchmarking.

## Full fresh portable replay

Use a new suffix every time. This explicit mode list includes pytest and both
portable-guide checks; the historical runner's shorter default list does not.
Run this in a working copy because it writes new result directories.

```bash
python verification/monograph_checks/run_current_checks.py --modes integrity static unit original sixth fifth structured test-functions pytest sympy portable vectors --suffix YOUR_NEW_RUN
```

The recorded current run suffix is `20261010_release`. Actual pytest collection
and pass/fail/skip counts are read from its JUnit XML. The direct-function mode
executes the same 34 source tests and is not a second independent test family.

```bash
python verification/checks/validate_manifest.py verification/monograph_checks/run_pytest_20261010_release/manifest.json --root .
python verification/monograph_checks/check_traditional_models.py --data editable/traditional/monograph_data/exact_examples.json --out ../paper-viii-models.json
python verification/monograph_checks/check_corpus_arithmetic.py --corpus source/strengthened/PSC_Paper_VIII_Strengthened_Annals_Edition_Package/verification/benchmark_results_sanitized.json --out ../paper-viii-corpus.json
```

The bounded runner records actual commands, inputs, outputs, hashes, timing,
resource limits and failures. Its operating-system resource controls were
executed on Linux here. Windows-native replay of those controls has not been
verified; use a Linux environment such as WSL rather than assuming parity.

## Editing and releasing a new edition

An intentional build without `--check-only` updates the nine active PDF copies
only after all three documents compile. It does not automatically refresh all
metadata, source pins, review reports or the global manifest. Such changes need
a new editorial review and release freeze. Do not present the old closure
receipt as a check of subsequently edited files.

Lean reproduction requires the original recorded compiler and Mathlib revision,
which are documented with the source. The fresh static gate compares saved
formal evidence. It is not a new kernel run. None of these commands measures GPU
performance or authenticates incomplete historical benchmark provenance.
