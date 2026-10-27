# Hilbert12 Cubic Divisor Transport and Reconstruction — visual companion

Read `H12_Cubic_Divisor_Visual_Guide.pdf` or its full Markdown companion. The guide has nineteen pedagogical pages and eighteen exact Python illustrations, each supplied as a vector PDF and PNG. All charts use declared source formulas or explicitly illustrative analytic profiles. No AI imagery, external dataset, gamma evaluation, or infinite-product numerical certificate is used.

`author_content.py` is the page-content source. It writes `guide_content.json`, which `build_guide.py` renders to TeX and Markdown; `validation/source_anchors.json` lists the raw-source anchors. Figure data are declared in `generate_figures.py`.

Rebuild from this directory:

```bash
python generate_figures.py
python author_content.py
python build_guide.py
pdflatex -halt-on-error H12_Cubic_Divisor_Visual_Guide.tex
pdflatex -halt-on-error H12_Cubic_Divisor_Visual_Guide.tex
```

The figure generator requires NumPy and Matplotlib; its other dependencies are from Python's standard library. The local TeX installation must provide the standard packages named in the source. Rebuilding updates artifact hashes and PDF metadata dates; exact declared scientific values remain reproducible.

`finite_control.json` pins all36 figure payloads and records exact integer/Fraction checks, eighty-digit Decimal coordinate illustrations, finite bounds, software versions, and generator hash. It includes all seven rational lifts on2,197 triples and explicit growth families for n=1,…,16. Finite controls do not replace the ordinary proofs or universal Lean statements. `validation/computation_contract.json` documents the scope and links the independently bounded replay evidence.

The final guide distinguishes the nonzero divisor support from the full nondiscrete lattice, point counts from multiplicity, the ungrouped absolute genus-three construction from possible grouped alternatives, and plane divisor regularity from periodic descent. The correction's branch-free cube representation is an analytic formula; the original arithmetic identification remains open.

`validation/PUBLICATION_QA.json` records every original-resolution figure and individual150dpi-page review, the two initial box-layout defects and their repairs, the final large-map embeds, and all current guide/source hashes. Scientific controls are exactly unchanged by the layout repairs. `validation/final_render_verification.json` authenticates the final unchanged-page comparisons and the four affected pages.
