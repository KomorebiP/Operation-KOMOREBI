Paper IV: Visual Guide, Monograph Edition
Author: Komorebi P.

This folder is a standalone editable source for the 28-page visual guide:
a cover, a reading route, and 26 worked pages containing 24 editable vector figures.

Build the PDF:
    python build.py

Test the build without changing the delivered PDF:
    python build.py --check-only

Use another output directory:
    python build.py --output-dir /path/to/output

The builder runs four XeLaTeX passes in an isolated complete source copy.
Python 3.9 or later, XeLaTeX, and the packages named in the current preamble are
required. Local styles, bundled fonts, current prose inputs, and editable TikZ
figures are retained. BibTeX is invoked only when bibliography data is present.
The build does not regenerate prose, mathematical models, or figure assets.
SymPy is not needed to compile the preserved exact figures.
SOURCE_DATE_EPOCH defaults to the edition date and FORCE_SOURCE_DATE is enabled.
The alias --output-directory is also accepted.

Replay mathematical models separately from PDF assembly:
    python checks/verify_examples.py
    python source/generate_graphics.py

The mathematical tools require the Python requirements in requirements.txt.
They write evidence or figures. Run them in a temporary copy if the delivered
source and inherited evidence should remain unchanged.

The monograph revision freshly passed all 147 exact or certified checks,
rejected all five deliberately false controls, and reproduced the four local
cubic zero brackets. All 24 current figures were freshly regenerated in an
isolated copy. These executions do not constitute a fresh Lean compilation.
The companion Lean guide records the inherited formal contract and its scope.

Source and evidence:
    source/pages.tex                       Preserved original visual prose
    source/pages_final.tex                 Authored monograph prose and locators
    source/models.py                       Preserved exact mathematical models
    source/generate_graphics.py            Deterministic figure generator
    graphics/*.tex                         24 editable vector figures
    checks/verify_examples.py              Unchanged mathematical checker
    checks/EXACT_CHECKS.json               Preserved inherited named results
    checks/EXACT_CHECKS_MONOGRAPH.json     Fresh isolated checker results
    checks/FIGURE_REGENERATION_MONOGRAPH.json  Fresh current figure comparisons
    SOURCE_IDENTITY.json                   Current and original source hashes
    MATHEMATICS_PRESERVATION.json          Formula and figure-call preservation
    EDITORIAL_CHANGES.json                 Editorial changes and layout adjustment
    VISUAL_CROSSWALK.json                  Traditional statement and page locators
    qa/PDF_QA.json                         Fresh PDF geometry and rendering checks

All 52 displayed formulas, 275 inline formulas, and 24 figure calls in the
worked prose retain their original mathematical tokens. Twenty-three figures
retain their original bytes. The V13 branch diagram moves one label clear of
the loop arrow and domain boundary. Its mathematical objects and labels are
unchanged. The matching coordinate in the generator is updated.

To refresh current page-header locators after a new traditional build:
    python refresh_monograph_locators.py --traditional-map /path/to/canonical_label_to_final.json --traditional-tex /path/to/Paper_IV_Traditional_Final.tex

This changes only the 26 headers and crosswalk metadata. It preserves all
worked prose, mathematical tokens, figure calls, and evidence wording.

The current pages_final.tex is the authored source of truth. The inherited
regenerate_editorial.py is retained as a historical reconstruction tool. It
recreates the October 5 editorial assembly and must not be used to overwrite
the current monograph. Build from the current source using build.py.

The package preserves the original release and its historical evidence in
source/complete/visual_appendix. PDF assembly, finite mathematical replay,
and formal compilation are separate operations with separate evidence.
