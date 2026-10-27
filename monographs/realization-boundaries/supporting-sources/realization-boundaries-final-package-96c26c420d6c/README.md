# Realization Boundaries
## Finite Grammar, Infinite Groups, and the Limits of Reconstruction

**Komorebi P. · Realization Calculus**

The final reading edition is `Realization_Boundaries_Monograph.pdf`: 64 pages, 12 chapters, three appendices, 45 numbered theorem/proposition/lemma/corollary statements, eight vector figures, a glossary, and references. The original research archives are retained for provenance, but are not needed to read the book.

## Mathematical scope

The book separates finite operator-seed generation, finite semantic description, effective group presentation, and topological generation. Its principal family consists of countable abelian groups

\[
D=\bigoplus_p C_p\subseteq G_A\subseteq P=\prod_p C_p.
\]

Each group has torsion subgroup D, quotient Q, and the same full unmarked finite-quotient system and profinite completion P. The groups are isomorphic exactly when their selectors differ finitely. An oracle X computes a copy exactly when it computes A. The proofs retain the distinction between uniform marked decoding and nonuniform unmarked decoding.

The development also includes pure intermediate groups, a complete diagonal homomorphism description, endomorphism and automorphism formulas, exact root fibers, nonreconstruction from unmarked finite quotients, and repeated diagonal escape from a fixed countable finite-description grammar. The completion P has a computable inverse-system presentation. This is not a computable enumeration of the elements of its uncountable underlying set.

The final proofreading corrects a categorical overstatement: failure to reflect isomorphisms uses the larger source category containing D and the groups G_A. Between the paired-prime groups alone, completion does reflect isomorphisms. Propositions 9.3 and 9.4 state and prove the distinction.

## Files

- `Realization_Boundaries_Monograph.pdf`: final reading edition.
- `preview/`: a selected-page preview, retaining the printed page labels.
- `manuscript/`: editable LaTeX and chapter sources.
- `figures/`: eight vector figures, PNG previews, and a figure index.
- `src/`: exact group arithmetic, three test suites, the printed-example replay, and figure generation.
- `verification/`: current test reports, theorem/source inventory, proofreading report, reference checks, layout checks, build evidence, and source changes.
- `provenance/`: two original research archives and a separately labeled archive of the earlier monograph's operational records.

## Verify the downloaded snapshot

Before rebuilding or editing, run:

```bash
python verify_integrity.py
```

The manifest covers the delivered files. Rebuilding may legitimately change hashes, including PDF metadata; byte-identical reproduction is not claimed.

## Reproduce the arithmetic

Python 3.10 or later and the standard library suffice for these commands:

```bash
python worked_example.py
python src/replay_printed_example.py
python src/dense_lift_groups.py
python src/exact_checks.py --output verification/local_core.json
python src/supplemental_checks.py --output verification/local_extra.json
python src/release_checks.py --output verification/local_release.json
```

The three suites passed **189,069 exact finite assertions**: 114,738 core, 53,284 supplemental, and 21,047 release regressions. These include seven named mathematical negative controls and 39 malformed-input rejection cases. The four assertions extracted directly from the book's Python example also passed and are not added to that total. Assertion counts are not counts of universally proved theorems.

Rational inputs must be integers or `fractions.Fraction` values. Prime labels, residues, and multipliers must be integers. Floating-point and other malformed inputs are rejected rather than silently truncated. Root multipliers must be positive. Selectors return a Boolean or integer bit 0/1. A finite-change transport requires the complete finite difference set as a precondition.

## Rebuild the PDF

With dependencies installed:

```bash
python build.py
```

To replay the three suites, regenerate the figures, and rebuild:

```bash
python build.py --verify --figures
```

Figure regeneration needs Matplotlib. Typesetting needs `latexmk`, `pdflatex`, and the packages named in `manuscript/monograph.tex`, including newpx, amsmath, amsthm, geometry, microtype, titlesec, fancyhdr, tcolorbox, TikZ, listings, hyperref, and bookmark. Use a TeX installation with the corresponding mathematics, fonts, and extra-LaTeX collections. The build script does not download dependencies or use the network. Font files are not distributed in this package.

## Evidence boundary

The universal mathematical conclusions are supported by the written proofs. **No Lean compilation or independent external peer review was performed.** Appendix B is a formalization plan, not a verified Lean library. Finite tests do not establish infinite classification, noncomputability, or grammar escape.

The classical direct-sum prime coding is explicitly attributed to Montalbán. Reference checks were targeted, not an exhaustive historical-priority audit. The finalization report records both substantive corrections and recovered production failures. The reading text contains no development-version references; the versioned operational ledger is kept separately.
