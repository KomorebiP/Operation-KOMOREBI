# Proof Path Theory — monograph edition 1.5.0

**Komorebi P. · Operation Komorebi**

Certificates, compression, discovery fields, and mathematical memory.

## Read the book

The current **60-page monograph** is `docs/Proof_Path_Theory.pdf`. Its editable
source is `docs/Proof_Path_Theory.tex`. The book has five illustrated part
openers, **22 vector figures**, four worked visual studies, and a revised
reference section. `docs/Proof_Path_Theory_Visual_Sampler.pdf` is an eight-page
selection from the same final PDF, not another version of the mathematics.

The visual studies show actual restriction maps, a whole-support gluing
counterexample, a normalized binary obstruction witness, and observation ranks.
The part openers include a genuine 3D binary realization cube, a compression
collision, and explicitly parameterized review-error curves.

## Editions and evidence

Publication edition **1.5.0**, Python distribution **1.3.0**, and inherited formal
evidence **1.2.0** identify different artifacts. The technical package has not
been silently version-bumped. Its source, tests, formal files, and inherited
compiler evidence remain unchanged.

- `VISUAL_UPGRADE_REPORT.md` records the redesign and corrections to the diagrams.
- `VERIFICATION_SUMMARY.md` records the checks actually run for this edition.
- `data/visual_verification_1.5.0.json` audits source identity and diagram data.
- `evidence/visual_1.5.0/` contains new test, build, preflight, and reproduction logs.
- `editorial/visual_baseline_1.4.0.json` pins the unchanged mathematical source.
- `data/claim_ledger.csv` retains all 33 stable result groups.
- `PROGRESS_LEDGER_v1.5.0.md` records the restart point and verification boundaries.

**No new Lean build is claimed.** The selected formal interfaces retain their
prior evidence. The whole monograph and the new diagram generator are not
universally Lean-verified. The social models are not empirical findings.

Earlier reports keep their dates and versions. In particular, the 1.3.0
proofreading record is historical evidence, not the 1.5.0 publication audit.
The older 1.4.0 root reports and generators are preserved under
`historical/publication_1.4.0/`.

## Reproduce the checks

Install the package and its test dependencies before working offline:

```bash
python -m pip install -e . --no-build-isolation
python -m pytest -o addopts='' -q
python scripts/deep_validation.py
python scripts/verify_bridge.py
python scripts/verify_visual_edition.py
python scripts/check_manifest.py
```

The visual checker additionally uses PyMuPDF. Figure generation requires
Matplotlib, NumPy, and the installed **Lato** font. The figure generator fails
rather than silently changing fonts. No font files are distributed. The
manuscript uses pdfLaTeX, NewTX, Source Sans Pro, TikZ, and the packages in its
preamble. No model API is required.

```bash
python scripts/design_figures.py
cd docs
pdflatex -interaction=nonstopmode -halt-on-error Proof_Path_Theory.tex
pdflatex -interaction=nonstopmode -halt-on-error Proof_Path_Theory.tex
pdflatex -interaction=nonstopmode -halt-on-error Proof_Path_Theory.tex
```

Run the manifest checker **before** rebuilding: a new PDF build may have a new
timestamp and therefore a different hash even with identical page content.
Figure PDF metadata are fixed; identical PDF and PNG figure hashes were checked
on a second generation in the release environment.

## Separate formal replay

The formal runtime is not bundled. With the pinned runtime already available:

```bash
python scripts/verify_lean.py --runtime /path/to/portable-kit
```

A full technical replay is available through `scripts/verify_release.py` with
that same runtime argument. It is not the default publication check. Copy the
package before running it because it writes new evidence records and may rebuild
distributions. A new Lean replay changes log hashes and is distinct from the
inherited evidence expected by the visual identity checker.

## Rights and scope

The license notice remains unchanged. This editorial edition does not choose a
redistribution license on the author's behalf. Claims about formal correctness,
software tests, and finite visual examples remain separated from historical
priority, independent peer review, and empirical claims about communities.
