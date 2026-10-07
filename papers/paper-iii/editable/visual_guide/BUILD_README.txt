Paper III: Visual Guide — Final Companion Edition
Author: Komorebi P.

This folder is a standalone editable source for the 26-page visual guide:
a cover, a reading-route page, and 24 worked pages containing 22 exact figures.

Build the PDF:
    python build.py

Test the build without changing the delivered PDF:
    python build.py --check-only

Use another output directory:
    python build.py --output-dir /path/to/output

The builder runs three pdflatex passes in a temporary copy. A TeX installation
with Latin Modern, TikZ/PGF, tcolorbox, amsmath, geometry, hyperref, bookmark,
fancyhdr, microtype, tabularx and the other packages named in the TeX preamble
is required. Python 3 is sufficient for PDF assembly; SymPy is not needed to
compile the already-preserved exact TikZ figures.

Replay mathematical models, separately from PDF assembly:
    python checks/verify_examples.py
    python source/generate_graphics.py

The exact-model checker and figure generator need the Python requirements
listed in requirements.txt. They write evidence or figures, so use a temporary
copy if the delivered source and historical evidence should remain unchanged.
The complete package's verification record distinguishes fresh execution from
inherited reports. Never infer a fresh mathematical check from a PDF build.

Source provenance:
    source/pages.tex                 Preserved original visual prose
    source/pages_final.tex           Final references and scope-aware prose
    source/models.py                 Preserved exact mathematical models
    source/generate_graphics.py      Preserved deterministic figure generator
    graphics/*.tex                  22 preserved editable vector figures
    checks/EXACT_CHECKS.json         Inherited named checks from original release
    SOURCE_IDENTITY.json             Byte identity with recovered visual sources
    MATHEMATICS_PRESERVATION.json    Formula and figure-call preservation
    EDITORIAL_CHANGES.json           Exact local prose changes
    VISUAL_CROSSWALK.json            Final traditional statement/page references

The editable guide can be rebuilt without the original manuscript. To recreate
its documented editorial transformations, run regenerate_editorial.py with the
final traditional map, final traditional TeX, and evidence wording JSON:
    python regenerate_editorial.py --traditional-map /path/to/canonical_label_to_final.json --traditional-tex /path/to/Paper_III_Traditional_Final.tex --expanded-map /path/to/expanded_label_to_final.json --evidence EVIDENCE_WORDING.json

All mathematical display formulas and every source model remain unchanged.
The revised orientation and closing pages distinguish the traditional paper's
broader ordinary proofs from the inherited finite v1.0.1 Lean contract.
