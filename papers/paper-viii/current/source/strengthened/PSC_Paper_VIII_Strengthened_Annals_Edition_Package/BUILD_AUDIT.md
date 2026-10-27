# Paper VIII build audit

## Final artifact

- PDF: `PSC_Paper_VIII_Strengthened_Annals_Edition.pdf`
- Pages: 45
- Page size: US letter
- PDF version: 1.7
- Encrypted: no
- Searchable text: yes
- Embedded fonts: yes
- Type 3 fonts: none
- Raster images in the main PDF: none

## Source build

The final source builds with the Annals `aomart` class through:

```text
pdflatex
bibtex
pdflatex
pdflatex
```

The environment used `/usr/bin/bibtex.original` because the default `bibtex` link was broken.

## Compiler result

The final log contains:

- no errors
- no undefined references
- no undefined citations
- no multiply defined labels
- no overfull boxes
- six minor underfull horizontal line warnings
- one underfull vertical page composition warning
- one harmless `cmtiup` package warning inherited from the installed journal class

The underfull warnings produce no visible spacing defect in the rendered pages.

## Clean build comparison

A new directory was created containing only:

- the final LaTeX source
- the BibTeX database
- the twenty two vector figures

The manuscript was rebuilt from that directory. The working and clean PDFs were rendered at 150 dots per inch and compared page by page.

```text
pages in working build: 45
pages in clean build: 45
changed pages: 0
```

## Visual inspection

All 45 pages were rendered and inspected through five contact sheets. Higher risk pages containing the compiler frontier, measured tables, multi panel benchmark figures, the disclosure, and the bibliography were also checked individually.

No page shows:

- clipped text
- overlapping equations
- broken glyphs
- black boxes
- truncated figure labels
- missing captions
- misplaced tables

## Figures

The article contains 22 figure environments and 22 source figure PDFs. Every source figure is vector only. `pdfimages` reports no raster object in any figure file.

## PDF validation

The final file:

- opens through PyMuPDF
- renders through Poppler
- passes a Ghostscript null page parse
- contains no forms or JavaScript
- is not encrypted
- is not a scanned document

## Archive

The final package is built without LaTeX auxiliary files or rendered page intermediates. A SHA 256 manifest covers every packaged file except the manifest itself. The ZIP archive is checked after creation.
