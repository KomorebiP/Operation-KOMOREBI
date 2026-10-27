# Worked visual appendix to Paper VI

The standalone appendix has 28 pages and 26 vector TikZ plates. It is compiled with the supplied `appendix.tex`; content is in `source/pages.tex`. Each page presents a small mathematical model, an exact formula or finite calculation, a visual representation, and an interpretation boundary.

## Build in isolation

From the complete bundle root:

```text
python Run-PaperVI.py build --output-dir rebuilt/reading
```

The implementation is `visual_appendix/build.py`. It copies inputs to a temporary directory, reruns exact checks, regenerates the TikZ files, and runs `pdflatex` twice. It rejects overfull/underfull boxes, unresolved references, page spillover, unexpected bitmap images, invalid internal links, and changes to the original reading pages. The completed PDF and audit are written only to the requested output directory.

The combined PDF's source lines link to the corresponding original manuscript pages. Standalone appendix navigation remains internal. Ordinary original figures and manuscript references are preserved.

## Mathematical evidence

`checks/EXACT_CHECKS.json` lists 204 successful exact/symbolic assertions and 11 deliberately false controls rejected for their stated reasons. Matrices and rational quantities are computed with SymPy. Full enumeration is only asserted for the specified finite families. Symbolic integrations retain their stated domains. New calculations are not kernel-checked Lean declarations.

The generator evaluates analytic functions numerically only to place drawing coordinates. Numeric curve geometry is not used to establish any exact identity, improper integral, or infinite-series claim. Labels distinguish probabilities, rates, likelihood weights, error magnitudes, and algebraic expressions.

Original source and proof boundaries remain in the preserved release. Consult `START_HERE.md` and `verification/DEVELOPMENT_NOTES.md` for the exact scope and corrected draft issues.
