# Build audit

## Final build

The final source was compiled in a clean directory with the following sequence.

```text
pdflatex
bibtex
pdflatex
pdflatex
```

The resulting PDF contains 49 pages.

## Compiler state

1. No compilation errors occurred.
2. No unresolved references occurred.
3. No unresolved citations occurred.
4. No duplicate labels occurred.
5. No overfull boxes occurred.
6. The journal class emitted its known `cmtiup` package warning.
7. Several minor underfull line warnings remain. They do not produce a visible defect.

## PDF preflight

1. The PDF opens successfully.
2. It is not encrypted.
3. It is searchable.
4. All fonts are embedded.
5. No Type 3 fonts are present.
6. The main PDF and every figure PDF contain no raster image objects.

## Visual review

All 49 pages were rendered at 170 dots per inch. Seven contact sheets were inspected. Higher risk pages containing exact recovery, positive memory, constraint obstruction, the continuum boundary table, and the bibliography were also inspected individually.

## Clean rebuild comparison

The working PDF and the final renamed clean build were rendered at 150 dots per inch and compared pixel by pixel.

```text
pages compared: 49
changed pages: 0
```
