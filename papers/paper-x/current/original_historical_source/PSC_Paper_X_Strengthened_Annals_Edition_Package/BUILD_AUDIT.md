# Build audit

## Build sequence

The final manuscript was compiled with

```text
pdflatex
bibtex
pdflatex
pdflatex
```

The installed system used `/usr/bin/bibtex.original` because its ordinary BibTeX link was broken.

## Final PDF

1. Pages: 41
2. Page size: US letter
3. Searchable text: yes
4. Encrypted: no
5. Fonts embedded: yes
6. Type 3 fonts: none
7. Raster objects in the manuscript PDF: none
8. Raster objects in the fourteen figure PDFs: none
9. Ghostscript structural validation: passed

## Compiler review

The final build has no unresolved references, unresolved citations, duplicate labels, overfull boxes, or underfull horizontal boxes.

The remaining messages are one harmless warning from the installed `cmtiup` dependency, two journal class messages about repeated authors in the bibliography, and one minor vertical page composition warning with no visible defect.

## Clean rebuild comparison

A clean build was made in a separate directory from the final TeX, BibTeX, and vector figure files.

```text
working pages: 41
clean pages: 41
changed rendered pages: 0
```

The comparison was performed at 160 dots per inch with the render comparison utility supplied in the PDF skill package.

## Visual review

All 41 final pages were rendered at 180 dots per inch. Four contact sheets were inspected. The title page, theorem dense pages, the characteristic zero trace correction, the completion theorem, the logical boundary table, and the bibliography were also inspected individually.

No clipped text, overlap, missing glyph, malformed equation, misplaced float, or broken reference was found.
