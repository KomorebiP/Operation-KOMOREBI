# Build audit

## Build result

The final source compiles with `pdflatex`, `bibtex8`, and two further `pdflatex` passes.

## PDF result

| Check | Result |
|---|---|
| Pages | 40 |
| Page size | Letter |
| Searchable text | Yes |
| Encrypted | No |
| Fonts embedded | Yes |
| Broken glyphs observed | No |
| Clipped text observed | No |
| Overlapping text observed | No |
| Undefined references | None |
| Undefined citations | None |
| Overfull boxes | None |
| Underfull boxes | None |

All 40 pages were rendered to images. The revised filtered lifting pages, graph transport pages, smooth transport pages, final scope section, disclosure, and bibliography were inspected directly.

## Compiler message

The installed journal class requests the package `cmtiup` through its dependency chain and produces one harmless package warning. The source itself has no unresolved build warning.

## Preflight

The PDF opens successfully with PyMuPDF, is not scanned, contains no forms, contains no XFA data, and is not encrypted.
