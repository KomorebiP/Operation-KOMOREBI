# Monograph and exact Python implementation

**Realization Boundaries: Finite Grammar, Infinite Groups, and the Limits of Reconstruction**  
Komorebi P. · Realization Calculus

The [reading edition](Realization_Boundaries_Monograph.pdf) is a 66-page book with 12 chapters, three appendices, 45 numbered mathematical contracts, eight vector figures, a glossary, and references. The [Lean companion and accepted evidence](../../README.md) live at the repository root.

## Files

- `manuscript/`: editable LaTeX chapters and style.
- `figures/`: vector figure PDFs and SVGs, PNG previews, and a figure index.
- `src/`: exact group arithmetic, test suites, printed-example replay, and Matplotlib figure generation.
- `verification/`: current Python reports and book build/visual QA records.
- The outer `provenance/` directory retains predecessor publication material and historical operational records.

## Integrity

Run this command from the **repository root** before rebuilding or editing:

```bash
python3 verify_integrity.py
```

The outer manifest covers the delivered publication files too. Rebuilding can legitimately change PDF metadata and hashes; byte-identical PDF reproduction is not claimed.

## Examples and arithmetic

Run these commands from **`publication/monograph_source`**:

```bash
python3 worked_example.py
python3 src/replay_printed_example.py
python3 src/dense_lift_groups.py
python3 src/exact_checks.py --output verification/local_core.json
python3 src/supplemental_checks.py --output verification/local_extra.json
python3 src/release_checks.py --output verification/local_release.json
```

Python 3.10 or later and the standard library suffice. The three suites passed 189,069 exact finite assertions: 114,738 core, 53,284 supplemental, and 21,047 release regressions. Counts of assertions are not counts of universally proved theorems.

Use integers or `fractions.Fraction` for rational inputs, integer prime labels and residues, and positive integer root multipliers. Floating-point and malformed inputs are rejected. A selector callable supplies Boolean or integer bits 0/1; the program assumes the oracle answers correctly. A finite-change transport requires the complete finite difference set as a precondition.

## Rebuild the PDF

From **`publication/monograph_source`**:

```bash
python3 build.py
```

To run arithmetic, regenerate the vector figures, and typeset:

```bash
python3 build.py --verify --figures
```

Figure regeneration requires Matplotlib. Typesetting requires `latexmk`, `pdflatex`, and the installed packages named in `manuscript/monograph.tex`, including mathpazo, amssymb, amsmath, amsthm, geometry, microtype, titlesec, fancyhdr, tcolorbox, TikZ, listings, hyperref, and bookmark. Font files are not bundled. The build script downloads nothing.

## Evidence

The printed proofs and separate checked Lean companion support the registered mathematical contracts. Finite Python tests exercise the implementation. Compiler receipts, exact formal scope, and same-kernel replay are recorded separately at the repository root. The separate assistance/provenance note preserves the established authorship and review disclosures.
