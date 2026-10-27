Paper II monograph build
Author: Komorebi P.

Build the authored modular edition from this directory:
    python3 build.py

To keep auxiliary files and the rebuilt PDF in a separate directory:
    python3 build.py --output-directory /path/to/build

Requirements: Python 3.9 or newer, XeLaTeX, BibTeX, and the TeX packages named
in the master and house style. Fonts, figures, atlas graphics, chapters, and
bibliography are packaged locally. Compilation requires no network access,
Lean compiler, or external Python package. The model-check scripts have their
own documented dependencies.

Paper_II_Traditional_Final.tex is the authored master. Chapters are edited in
chapters/. The embedded atlas and its exact vector sources are part of this
edition. build.py compiles these sources directly. It never replaces the
master or rebuilds chapter prose from the historical integration sources.

The former build.py --assemble option is accepted for compatibility and now
compiles the current authored edition without reassembly. Historical assembly
is available only with an explicit separate output directory:
    python3 assemble.py --historical-output source/historical_assembly/example
That command reproduces the original integration for inspection inside the
historical output directory. It does not update the current monograph.
The original source manuscripts remain in source/ and the previous edition
is preserved in the full package under source/provenance/.

The builder performs four XeLaTeX passes and runs BibTeX after the first pass
when the auxiliary file requests it. Pass transcripts and the final TeX log
are written beside the rebuilt PDF. The deterministic timestamp comes from
publication/PUBLICATION_BUILD_CONFIG.json. The --edition-date option selects
another ISO date explicitly. Exact PDF bytes still
depend on the installed TeX engine and package versions.

From the complete package root, all three companions can be rebuilt in
isolated temporary directories:
    python3 scripts/build_pdfs.py
A rebuild that compares page counts and extracted text without replacing the
shipped PDFs requires PyMuPDF:
    python3 scripts/build_pdfs.py --check-only --report verification/rebuild.json

The complete release reports and current crosswalks describe source identity,
proof preservation, printed locators, visual review, and formal scope. The
ordinary written results keep their own hypotheses. The inherited 25-row
formal contract is a separate counting and coverage unit. A PDF build does
not run Lean.
