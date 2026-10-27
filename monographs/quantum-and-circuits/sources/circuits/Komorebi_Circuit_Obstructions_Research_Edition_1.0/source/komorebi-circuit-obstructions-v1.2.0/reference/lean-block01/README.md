# Lean-verified core, Block 01

This 15-page reference covers all 40 theorem declarations in the C01 formalization. It is a supplement, not a replacement for the 28-page written-theorem companion of v1.0.0. Only original Theorem 2.1 has acquired formal status.

Build with an installed LaTeX distribution containing newtx and tcolorbox:

    python build.py

Proof statements have mathematical renderings and exact source identifiers/line locations. `declaration-map.json` is checked against the source inventory. The `.lean` files contain the full machine proofs; their elaborated types and axiom reports are in `evidence/lean-block01/verified/logs/axioms_and_statements.log`.

The PDF was built twice with pdfLaTeX, rendered in MuPDF, and visually inspected. All 15 pages passed text-bound checks; no overfull boxes or unresolved references remained. The maps cover exactly the same 40 declarations as the formal runner. No font files are included in this package.
