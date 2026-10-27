# Paper VI Build Audit

## Clean build

The final manuscript was rebuilt in an empty directory using:

```text
pdflatex -interaction=nonstopmode -halt-on-error PSC_Paper_VI_Strengthened_Annals_Edition.tex
bibtex8 PSC_Paper_VI_Strengthened_Annals_Edition
pdflatex -interaction=nonstopmode -halt-on-error PSC_Paper_VI_Strengthened_Annals_Edition.tex
pdflatex -interaction=nonstopmode -halt-on-error PSC_Paper_VI_Strengthened_Annals_Edition.tex
```

## Result

| Item | Result |
|---|---|
| Pages | 54 |
| Undefined references | 0 |
| Undefined citations | 0 |
| Duplicate labels | 0 |
| Overfull boxes | 0 |
| Underfull horizontal boxes | 0 |
| Underfull vertical boxes | 1 minor page composition warning |
| Encrypted | No |
| Searchable text | Yes |
| Fonts embedded | Yes |
| Vector figures | 15 of 15 |
| Raster images inside figure PDFs | 0 |

The only package warning comes from `cmtiup`, which is loaded through the installed `aomart` class. It does not affect the output. The one vertical spacing warning has badness 1048 and no visible defect.

All 54 pages were rendered at 170 dpi and inspected in contact sheets. Pages containing long formulas, the Bayesian sufficiency revision, the modal memory expansion, the numerical table, the disclosure, and the bibliography were also checked separately.

## Archive reconstruction

The final ZIP was extracted into a new directory. Its manifest was verified, both verification suites were rerun, and the manuscript was rebuilt from the archived source and vector figures. The rebuilt PDF again had 54 pages. A PDFium render comparison at 120 dpi found zero changed pages out of 54.
