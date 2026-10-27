Paper II visual atlas build
Author: Komorebi P.

Compile the authored guide from this directory:
    python3 build.py

To place the PDF and auxiliary files elsewhere:
    python3 build.py --output-directory /path/to/build

Requirements: Python 3.9 or newer, XeLaTeX, and the TeX packages named in the
master and house style. Fonts and TikZ vector sources are packaged locally.
Compilation needs no network access, raster image generator, Lean compiler,
or external Python package. The exact model checks have separate dependencies.

Paper_II_Visual_Guide_Final.tex is the current editable master.
source/pages_final.tex contains the authored plate text and companion locators.
The 24 stable labels V1 through V24 identify the worked plates independently
of PDF pagination. The exact mathematical model sources are in source/ and
the 22 vector figure sources are in graphics/.

Normal compilation preserves the master, plate prose, figures, and models.
To regenerate only exact graphics after an intentional model edit:
    python3 source/generate_graphics.py
The generator requires SymPy. The checks/verify_examples.py script records
explicit finite test ranges and also requires SymPy.

The complete package supplies a safe helper that compiles the authored guide:
    python3 scripts/regenerate_visual_guide.py
Run that command from the complete package root. To regenerate mathematical
graphics before compilation, add --graphics. To regenerate graphics without
compilation, add --graphics-only. This helper never restores pages_final.tex
or the master from the historical visual appendix. Historical source copies
remain in the full package under source/visual_guide_original/ and provenance.

The builder performs four XeLaTeX passes. It writes pass transcripts and the
final TeX log beside the PDF. The deterministic timestamp comes from
publication/PUBLICATION_BUILD_CONFIG.json. The --edition-date option selects
another ISO date explicitly. Exact PDF bytes may differ across
TeX installations.

The models explain the statements and expose their mechanisms. Finite exact
checks validate the displayed instances. Universal proofs and formal coverage
retain the scope recorded in the traditional paper and Lean guide.
