# Traditional final edition

**Komorebi Quadratic-Form Engine and K-COS**, Komorebi P., October 7, 2026.

- `Quadratic_Form_KCOS_Traditional.pdf`: complete traditional edition.
- `Quadratic_Form_KCOS_Traditional.tex`: editable canonical LaTeX source.
- `Quadratic_Form_KCOS_Traditional.md`: complete editable text, including mathematics, proofs, experiments, and companion contracts. Statement and reference numbers follow the PDF.
- `final_edition_validation.tex`: fresh 58-test record and independently contained extreme-tail/matrix controls.
- `lean_coverage.tex`: precise claim-to-declaration map and formalization boundary.
- `claim_inventory.json` and `source_anchors.json`: the 55 theorem/lemma/proposition/corollary statements, five remarks, one algorithm, and canonical PDF anchors.

The final text retains the full v1.9 matrix-to-tail manuscript and integrates the complete centered-packet theory from the separate K-COS paper. Historical September measurements are labeled separately from fresh October 7 validation. Numerical enclosures are distinguished from analytic approximation ledgers.

Original matrix illustrations remain unchanged in `../engine/figures_final/`. This edition uses 24 layout derivatives in `figures_final/`, alongside four unchanged matrix originals and three unchanged packet figures in `figures_packets/`. Notes and legends have reserved space; coincident curves and dual metrics are distinguished. The derivative files beginning `figure_05`, `figure_06`, and `figure_07` use archived rank/discrepancy summaries or the original rounded packet labels because their raw plotted vectors were not archived. No hidden samples or new empirical data are introduced.

`relayout_figures.py` and `relayout_late.py` regenerate the derivatives from archived sources. `FIGURE_RELAYOUT_EARLY.json` and `FIGURE_RELAYOUT_LATE.json` record source hashes, full plotted arrays, recipes, and preservation checks. Read the matching visual and Lean guides for explanation and formal coverage.

`FIGURE_INDEPENDENT_REVIEW.json` pins all 31 images inspected at native resolution; `FIGURE_DATA_PRESERVATION.json` retains the independent coordinate checks. The build uses `check_figure_reviews.py` to associate that review only with matching image bytes. A different output hash is marked as requiring a new review.

Run `python build_traditional.py` to regenerate figures, rebuild the PDF with three LaTeX passes, and regenerate Markdown. This requires Python with Matplotlib and NumPy, `pdflatex`, and `pandoc`. Use `--skip-markdown` to rebuild only figures and PDF, or `--skip-figures` to retain the already generated images. The build logs and statement inventory are retained for verification.
