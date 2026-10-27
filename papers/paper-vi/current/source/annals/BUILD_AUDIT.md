# Paper VI Build Audit

## Final build

- Journal class: `aomart`
- LaTeX engine: `pdflatex`
- Bibliography engine: BibTeX
- Final pages: 41
- PDF file size: 686205 bytes
- Abstract length: 180 words
- Vector figures: 12
- PDF encrypted: no
- Searchable text: yes
- Fonts embedded: yes
- Type 3 fonts: 0

## Reference and source integrity

- Unique labels: 103
- Duplicate labels: 0
- Missing internal references: 0
- Bibliography entries: 21
- Missing citation keys: 0
- Uncited bibliography entries: 0
- Proved result records: 63
- Complete proof environments: 63

## Compiler messages

There are no overfull boxes, undefined references, undefined citations, or duplicate labels. Six minor underfull line warnings and one underfull page box warning remain because automatic word hyphenation is suppressed and figures are allowed to float naturally. Visual inspection found no spacing defect. The installed journal class also emits its internal `cmtiup` package warning.

## PDF preflight

The PDF opens in PyMuPDF, is not encrypted, is not a scanned image document, and contains no XFA form data. The complete preflight output is stored in `PDF_PREFLIGHT.txt`.

## Visual audit

All 41 pages were rendered at 150 dots per inch and inspected through four contact sheets. Pages containing the fractional defect theorem, Green formulas, rational memory realization, disclosure, and references were also inspected at full page scale.

No clipping, overlap, broken glyph, malformed equation, missing figure, or truncated reference was found.

## Figure audit

All twelve figures are vector PDF files. The figure generator sets the PDF font type to embedded TrueType. The final manuscript contains no Type 3 figure fonts.

## Clean build comparison

The final source, bibliography, and vector figures were copied to a clean directory and rebuilt. A page image comparison at 120 dots per inch reported:

```text
pages in working build: 41
pages in clean build: 41
changed pages: 0
```

## Verification

The final verification run reports:

```text
Paper VI revised verification: 475471/475471 checks passed in 16 groups
```

The largest reported residuals come from finite Trotter slicing and truncated numerical integration. Exact algebraic identities were resolved to floating point precision.

## Boundary

The build and verification records establish reproducibility of this release. They do not replace independent mathematical review or a historical priority analysis.
