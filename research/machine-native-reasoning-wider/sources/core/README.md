# Machine-Native Reasoning
## Evidence, Methods, and Accountable Revision
### Reviewed mathematical core, edition 0.2 · Komorebi P. · 9 October 2026

This is the next result-level selection in the theory-first monograph. It is not the 1,919-page source reader with a stronger label. The continuous book now has 40 pages, nine chapters, 27 complete statement/proof pairs, twelve counterexamples, and six analytical figures.

The six new results integrate selected arguments from Large Signal Model Foundations 0.4.0, PRIQ 0.1.4, and AVOC's traditional publication based on formal v0.41.0. None of those whole documents or whole implementations is admitted by this selection. The earlier twenty-one statement/proof pairs are unchanged. The preceding four source-wide test replays remain historical v0.1 evidence, not new executions.

## Read in this order

1. `Komorebi_Machine_Theory_Reviewed_Core_v0.2.pdf` is the canonical reader. `src/core.tex` is its editable source.
2. `RESULT_INDEX.json` locates each result in the source and printed pages. `RESULT_LEDGER.json` binds assumptions, source excerpts, review notes, and finite checks.
3. `review/PROOF_REVIEW.md` describes what was reviewed for each result. `review/READING_ARCHITECTURE.md` explains the dependency-first order.
4. `REVIEW_NOTES.md` states the complete current checking scope and actual failures. `SOURCE_DISPOSITION.json` accounts for all 24 documents in the former collection.

## The new connection

Chapter 2 distinguishes algebraic packets from probability components. Chapter 3 extends static correction to exact joint state/report instruments and controlled histories, with a separate approximation bound. Chapter 5 uses the same retained belief to plan one finite experiment sequence, then handles uniform model error before optimizing the policy.

The sensor example is unchanged except for explicitly supplied noisy calibration. Under a correct-report probability of 3/4, report charge 1/20, and wrong-choice loss one, the optimal expected costs for report horizons 0, 1, 2, 3 are 1/2, 3/10, 3/10, 11/40. The three-report policy takes two reports, stops when they match, and requests the third only on disagreement. This is a finite analytical result, not agent training or a behavioral experiment.

## Reproduce

First verify the frozen snapshot **before** regenerating any timed outputs:

```text
python code/verify_release.py
```

Build and check with Python 3.10+ plus a LaTeX installation containing the packages used in `src/core.tex`, PyMuPDF, and Poppler's `pdffonts`:

```text
python code/build.py
python code/check_fresh.py
```

The Bash convenience entry point is `bash build.sh`. The exact mathematical checks themselves use Python's standard library. The build runs both `check_core.py` and `check_admissions.py`, then three LaTeX passes, source/proof-preservation auditing and PDF preflight. The fresh checker builds a temporary source copy and compares both mathematical reports and the worked-example data, excluding only explicit timing fields. It also compares all page texts, geometry, navigation, and rendered pixels at a stated scale.

Regenerate figures with Matplotlib (not needed for a PDF rebuild from the shipped vector assets):

```text
python code/make_figures.py
python code/make_admission_figures.py
```

Render all pages and contact sheets for visual review with Pillow and PyMuPDF:

```text
python code/render_review.py --out /path/to/review-images
```

This rewrites `evidence/render_record.json`. A later integrity check will correctly notice regenerated files whose bytes changed. Keep original receipt snapshots separately when running a new reproduction.

## Checking scope

Current runs: 27 exact finite groups and 205,477 assertions, including the unchanged 21-group predecessor suite and six new admission groups. The comparisons use exact integers, sets, and fractions. There is no new neural training, full LSM/PRIQ/AVOC test-suite run, Lean replay, hardware benchmark, or external-service execution.

The compilation and review records are project-local evidence. Internal prose review, finite checks, source preservation, and document rebuilding are distinct. Neither assertion counts nor a passing manifest constitute independent peer review or a universal proof. The new results do not establish learned physical semantics or an integrated general agent.

## Package boundaries

The package includes selected source excerpts rather than all original source PDFs. Their filenames and hashes bind them to the previously preserved collection. The older core source and review notes are retained under `review/predecessor/`. The original delivered v0.1 PDF and ZIP are unchanged.

No standalone font files, neural checkpoints, third-party full papers, or private conversation transcript are included. No source is relicensed. Windows execution, tagged accessibility, PDF/A, and cross-platform PDF byte identity were not certified.
