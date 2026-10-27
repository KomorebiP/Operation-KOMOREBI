# Operation Komorebi conjecture pieces

Reader edition 1.0, 8 October 2026. Author pseudonym: Komorebi P.

The two manuscripts are self-contained accounts of the Collatz and Riemann programs. Each separates mathematical identities, source-reported historical proof checks, fresh bounded computation, conditional implications, and the open conjecture.

## Contents

- `collatz/`: manuscript source, bibliography, source register and selected recovered research evidence.
- `riemann/`: manuscript source, bibliography, source register and selected recovered research evidence.
- `shared/figures.py` and `shared/figures/`: reproducible charts, exact integer inputs, numerical inputs and environment requirements.
- `shared/review_checks.py`: independent exact arithmetic controls for the Collatz formulas.
- `shared/REVIEW.md`: mathematical review and its coverage boundary.
- `shared/LITERATURE_CHECK.md`: verified classical statements, notation translations, primary references and source-access limitations.
- `shared/preamble.tex`: the common modern monograph design.
- `AUTHORING_REPORT.md` and `shared/LAYOUT_VALIDATION.json`: resolved failures and final reader layout checks.
- `pdf/`: final reader PDFs.

The evidence folders contain selected complete texts and clearly identified read windows. The retained JSON records identify their original filenames, versions and read ranges. This bundle is not the entire historical Lean project or its build environment. Historical Lean results are labelled as historical. No fresh Lean run is claimed by this authoring task.

## Rebuild

Use Python 3 with the pinned packages in `shared/figures/requirements.txt`, and a TeX installation providing `pdflatex`, `mathpazo`, `amsmath`, `mathtools`, `microtype`, `titlesec`, `fancyhdr`, `graphicx` and `hyperref`.

```bash
python shared/figures.py
python shared/review_checks.py
python build.py
```

`python build.py --only collatz` or `--only riemann` rebuilds one manuscript. `python build.py --figures` also reruns the figure script. The output is placed in `pdf/`.

For optional PDF layout checks, install PyMuPDF and Pillow and provide Poppler's `pdftoppm`, then run `python quality_check.py`. That script generates page renders and machine checks. Its manual review field starts as pending because a new build still needs visual inspection. `python package.py` creates the final source ZIP and verifies its manifest and archive integrity.

Fresh computation reproduces finite checks and illustrations. It does not prove universal Collatz descent or the missing arithmetic cancellation estimate for RH. The printed proofs and classical cited theorems carry the universal claims actually stated.

## Corrections and preserved history

The Riemann manuscript repairs two defects in the archived sign-free prime-cube argument: an interval mass was incorrectly used as an upper bound for the full signed sum, and the interval count omitted the squarefree weight. The new proof uses the full triangle majorant and an explicit squarefree count. The original recovered report remains unchanged, with the correction recorded in the review and author notes.

Some historical archive and original-paper downloads could not be obtained. Each source register records the exact access limit. Readable research records and verified primary alternatives supply the stated dependencies.
