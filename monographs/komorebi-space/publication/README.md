# Komorebi Space readers

The current monograph is **Realization Calculus, Volume I: Komorebi Space**, supplied as `books/Komorebi_Space.pdf`. It uses the latest paired-volume presentation and retains the accepted mathematical chapters, proofs, figures, notation map, formal correspondence, reader workshop, hypothesis atlas, analytic appendix, and references.

The Lean guide gives the route from the written mathematics to formal declarations. The visual guide supplies sixteen worked visual investigations. Each reader contains a publication and reuse notice. Original writing and figures use CC BY 4.0; original code uses MIT. The release's third-party font and dependency notices remain applicable.

## Rebuild

From the release root, run:

```sh
python3 tools/build_readers.py --book all
```

The script uses three passes of `pdflatex` per reader. A TeX Live installation providing the packages loaded by the source is required. It writes build outputs to `build/readers/`, puts the three PDFs in `books/`, records source hashes, and reports layout or reference warnings. Use `--book monograph`, `--book lean`, or `--book visual` for one reader, or `--output PATH` for a different build directory.

Editable source is in `publication/volume_i/source/`. The monograph also imports `publication/shared/series-style.tex` and `publication/shared/series-front.tex`. Keep those relative paths intact. Figures and the visual guide's source assets are included. The builder does not run Lean or regenerate figures.

## Verification scope

The reader verification report records two successful builds, source preservation, embedded fonts, links, page-boundary checks, and visual review. PDF document identifiers vary between build directories; the two builds are otherwise byte identical. The release's formal verification report is separate.
