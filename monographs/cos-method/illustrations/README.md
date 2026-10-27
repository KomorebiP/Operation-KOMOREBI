# Quadratic-Form Engine / K-COS visual companion

The 18-page guide follows factors, storage blocks, phase propagation, residual completion, tilted transforms, spectral packets, and the final enclosure decision. Its illustrations use small declared models. They add no production timing or performance claims.

Read `Quadratic_Form_KCOS_Visual_Guide.pdf` or the complete Markdown companion. `build_guide.py` is the single content source for both formats. `guide_content.json` and `validation/source_anchors.json` expose the page structure and traditional-paper anchors.

Rebuild from this directory:

```bash
python generate_figures.py
python build_guide.py
pdflatex -halt-on-error Quadratic_Form_KCOS_Visual_Guide.tex
pdflatex -halt-on-error Quadratic_Form_KCOS_Visual_Guide.tex
```

Figures require NumPy, SciPy, and Matplotlib. The ninety-digit Erlang control uses Python's standard-library `Decimal`. No image-generation service or external dataset is used. Each figure has a vector PDF and a PNG rendering.

`finite_control.json` records the declared toy inputs, exact integer identities, floating diagnostics, decimal log-law evaluations, software versions, and figure hashes. The audited bounded run and its validated manifest are preserved under `validation/figure_run_visual_repair/`. These finite checks do not replace the source theorems or a directed-rounding probability enclosure.

The traditional paper and Lean guide retain the authoritative proof and formalization scopes. In particular, the exact-spectrum interval path and the analytic packet path have different arithmetic guarantees.

The repaired figures reserve space for operators, labels, legends, and notes. All seventeen figure PNGs and all eighteen PDF pages were inspected individually at full resolution. `validation/VISUAL_REPAIR_REPORT.json` records the corrections and confirms exact equality of the finite-control payload before and after the layout changes. The original generator and control record are preserved in `validation/before_visual_repair/`; `validation/figure_run_final/` is historical evidence for that earlier revision.

Both independent full-resolution reviews passed, including the final page 13 spacing refinement. `validation/INDEPENDENT_VISUAL_PUBLICATION_REVIEW.json` pins the final guide and all figure PNGs; `validation/final_render_verification.json` confirms that all final PDF renders match the individually inspected pages.
