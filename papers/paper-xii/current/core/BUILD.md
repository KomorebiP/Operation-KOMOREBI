# Building and checking Paper XII

These commands were exercised on Linux. WSL is the documented Windows route; native Windows parity is not claimed. Paths below are relative to this release root. Keep logs and outputs outside the sealed tree.

## Dependencies

Python 3 with PyMuPDF, NumPy, SymPy and Matplotlib; TeX Live with pdfLaTeX, XeLaTeX, BibTeX, TikZ, amsart, fontspec, unicode-math and the packages named by the wrappers. The visual generator uses TikZ; the four repaired main diagrams use Matplotlib. No image-generation service or empirical simulation is involved.

The exact checked versions and executable paths are in `evidence/block01/ENVIRONMENT.json`. Installed font dependencies are P052, Nimbus Sans, DejaVu Sans Mono and Latin Modern Math. No standalone font files are supplied. Use the local system's font installation. The reader wrapper source is fully included.

The builder tries `bibtex`, then `bibtex.original`, then `bibtex8`, and accepts only a runnable executable. The first launcher was broken in the checked runtime; `/usr/bin/bibtex.original` worked. This is not a dependency on that absolute path on another machine.

## Verify the supplied bytes

```text
python tools/verify_package.py
```

The root manifest hashes every file except itself and rejects extra files. A check output placed inside the tree would count as an extra file. Nine standalone font files were excluded from the recovered predecessor. Therefore its unmodified historical top-level distribution manifest is not a manifest of this sanitized release. Use the root manifest; original scientific archive hashes are separately authenticated by the replay.

## Seven bounded gates

```text
python tools/replay.py --output ../paper_xii_replay
```

The runner records gate name, executable script hash, exit status, timeout, duration and log hashes. Outputs include the detailed result JSON for each gate. A timeout is failure, including for negative controls. Only the named finite suites, source checks and historical-log authentication run. No Lean or Lake process is launched.

A selected replay uses, for example:

```text
python tools/replay.py --gates publication-regressions visual-exact --output ../selected_replay
```

## Rebuild all three readers and their links

```text
python tools/build_readers.py --output ../paper_xii_build
```

The builder stages copies, resolves installed fonts, regenerates the visual figures, makes three TeX passes, and runs bibliography generation for the monograph. Shell escape is disabled. It builds the entire trio so that every companion annotation points to the actual destination in the current target PDF.

To divide execution into bounded stages:

```text
python tools/build_readers.py --stage compile --output ../paper_xii_build
python tools/build_readers.py --stage links --output ../paper_xii_build
```

The output directory contains the three release-named PDFs, `COMPILE.json`, `LOCATORS.json` and `BUILD.json`. Deterministic dates are fixed in source and the build environment. PDF reproducibility is a separate property from proof verification. Identical output is verified in the recorded environment, not guaranteed across different TeX/font/PyMuPDF versions.

The legacy per-reader `build.py` files in the current source folders are thin adapters to this coordinated builder. Legacy files inside `predecessor/` describe their historical environments and are not the preferred current entry points.

## Rendering

Render the three final PDFs with a PDF renderer and compare changed pages after any edit. The preserved final contact sheets, detailed pages, document hashes and inspection record are under `verification/block01/`. A bounds check cannot detect every visual overlap and does not replace inspection.

## Future formal replay

The guide records Lean 4.34.0-rc2, exact compiler and Mathlib pins, all historical source/object hashes, and the explicit theorem-argument audit. Obtain the exact compiler and dependency cache separately. Work from a disposable copy of the formal archive. The historical verifier mutates its build and log directories; do not run it inside this sealed reading release. No fresh kernel acceptance is asserted by the commands above.
