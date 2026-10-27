# Build and PDF Audit

## Build source

The release PDF was compiled from a clean directory containing only:

- `PSC_Paper_V_Annals_Human_Edition.tex`
- `PSC_Paper_V_Annals_Human_Edition.bib`
- the 14 vector PDF figures

## Build commands

```text
pdflatex -interaction=nonstopmode -halt-on-error PSC_Paper_V_Annals_Human_Edition.tex
bibtex8 PSC_Paper_V_Annals_Human_Edition
pdflatex -interaction=nonstopmode -halt-on-error PSC_Paper_V_Annals_Human_Edition.tex
pdflatex -interaction=nonstopmode -halt-on-error PSC_Paper_V_Annals_Human_Edition.tex
```

## PDF state

| Check | Result |
|---|---:|
| Pages | 43 |
| Page size | US letter, 612 by 792 points |
| Encrypted | No |
| Searchable text | Yes |
| Likely scanned | No |
| Fonts embedded | Yes |
| Outline items | 32 |
| Form fields | 0 |
| Attachments | 0 |
| Missing references | 0 |
| Missing citations | 0 |
| Overfull boxes | 0 |

The build reports five minor underfull box warnings and one harmless `cmtiup` warning generated through the installed `aomart` dependency. No visual defect was found at those locations.

## Render review

All 43 pages were rendered at 150 DPI and inspected through five contact sheets. Higher risk pages containing the numerical tables and the final bibliography were also inspected individually. No clipping, text overlap, broken glyph, black square, malformed equation, or unreadable table was found.

## Clean build comparison

The working PDF and the clean directory PDF were rendered independently at 100 DPI and compared pixel by pixel.

```text
pages in first PDF: 43
pages in clean PDF: 43
changed pages: 0
```

The comparison record is included as `CLEAN_BUILD_COMPARISON.json`.

## Verification suites

```text
Paper V revised verification: 11052/11052 checks passed in 13 groups
Original Paper V source suite: 27 passed
```

The scripts and logs are included in the package.
