# Komorebi Seeded Two-Axis Calculus v0.10.0

95-page cumulative research manuscript by Komorebi P. This package contains LaTeX, PDF, written proof fragments, five exact regression suites, audit and provenance records, source diff, and the unchanged full v0.9.0 package.

## New mathematical block

Section 18 (pages 56–63) develops complete one-step H^2 obstructions, a counterexample to sufficiency of derived-invariant exchange, quantitative averaging repair, a finite integral-lifting horizon for fixed finite groups, controlled conjugacy, and a finite-quotient/profinite distinction. Ledger entries K62–K71 identify the new results.

The finite-group stability threshold is already established in the literature. The package provides a direct proof, explicit certificates, and its integration into the calculus. It does not claim a new axiom, historical novelty, unrestricted representation lifting, or Langlands reciprocity.

## Reproduction

Use Python 3.10 or later. The environment used here was Python 3.13.5 with SymPy 1.14.0. The new action-lifting suite uses the standard library only; inherited arithmetic suites use the pinned SymPy dependency.

```bash
python -m pip install -r requirements.txt
python checks/run_all.py
python audit/integrate_v0100.py
latexmk -pdf -outdir=build -interaction=nonstopmode -halt-on-error Komorebi_Seeded_Two_Axis_Calculus_v0.10.0.tex
```

The manuscript uses a standard TeX Live setup with amsmath, amsthm, mathtools, lmodern, microtype, mathrsfs, tikz-cd, cleveref, geometry, booktabs, longtable, enumitem, and needspace. No fonts are bundled.

`checks/run_all.py` records actual commands, timings, script hashes before and after each run, report hashes, a 40-second timeout per suite, and cooperative numerical-library thread caps. A PASS is a finite regression result, not a mathematical proof certificate. The written universal proofs are in the manuscript.

`audit/check_source.py` validates the packaged source, log, inherited-block preservation, test hashes, and deterministic source regeneration. To rerun it after a new LaTeX build, copy the new build log to `audit/latex_final.log`. The packaged final log corresponds to the packaged PDF.

Optional page rendering requires PyMuPDF and Pillow, not needed for mathematical tests:

```bash
python audit/render_review.py --render-dir /tmp/komorebi-v010-renders
```

## Evidence and provenance

`STATUS.md` is the current summary. `RESEARCH_LOG.md` indexes immutable research records. `audit/AUDIT.md` states the proof/self-review boundaries and the refuted route. `audit/source_checks.md` records exact external-source translations. `audit/static_source_checks.json`, `audit/release_manifest.json`, and `checks/all_runs.json` give reproducible checks. `previous/` preserves exact v0.9.0 PDF, source, and full ZIP.

The PDF was rendered and scanned. New mathematical proofs are self-reviewed; no Lean compilation or independent referee review occurred. Earlier theorem blocks are preserved, not represented as having been independently re-audited in this release.
