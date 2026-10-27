# Realization Boundaries
## Finite Grammar, Infinite Groups, and the Limits of Reconstruction

**Komorebi P. — Realization Calculus**

The reading edition is `Realization_Boundaries_Monograph.pdf`. It contains 12 chapters, three appendices, a glossary, references, and eight integrated vector figures. The book is self-contained: the input research notes are preserved for provenance, but are not required for reading.

## Main mathematical development

The book separates finite operator-seed generation, finite semantic description, effective group presentation, and topological generation. Its principal family consists of countable abelian groups

\[
D=\bigoplus_p C_p\subseteq G_A\subseteq P=\prod_p C_p.
\]

Every group has torsion subgroup D, quotient Q, and the same full unmarked finite-quotient system and profinite completion P. The groups are isomorphic exactly when their selectors differ finitely. An oracle X computes a copy exactly when it computes A. All universal conclusions are supported by the printed ordinary proofs, not inferred from finite tests.

The integrated development also includes the pure-preimage correspondence, a complete diagonal description of homomorphisms, endomorphism and automorphism formulas, exact root fibers, failure of reconstruction from unmarked finite quotients, and repeated diagonal escape from a fixed countable finite-description grammar.

## Reading and source files

- `Realization_Boundaries_Monograph.pdf`: complete reading edition.
- `preview/Realization_Boundaries_Preview.pdf`: selected pages from the book, with original printed pagination retained.
- `manuscript/`: editable LaTeX manuscript, chapters, and generated assertion-count macros.
- `figures/`: eight figures in PDF, SVG, and PNG, plus an index.
- `src/`: exact group arithmetic, two finite test suites, and Matplotlib figure generation.
- `verification/`: fresh test reports, theorem inventory, mathematical review, layout review, environment and provenance records.
- `provenance/`: both original input archives, retained without alteration.

## Reproduction

The arithmetic requires Python 3.10 or later and only the standard library:

```bash
python worked_example.py
python src/dense_lift_groups.py
python src/exact_checks.py --output verification/local_core.json
python src/supplemental_checks.py --output verification/local_extra.json
```

The recorded suites passed **168,022 exact finite assertions**, including seven negative controls. Counts refer to assertions, not distinct theorem proofs. The earlier direct-sum checks were replayed separately and are not added to that total.

To rebuild the PDF with the existing vector figures:

```bash
python build.py
```

To rerun the tests, regenerate the figures, and rebuild:

```bash
python build.py --verify --figures
```

Figure generation additionally needs Matplotlib. Typesetting needs `latexmk`, `pdflatex`, and the TeX packages named in `manuscript/monograph.tex`, including newpx, amsmath, amsthm, geometry, microtype, titlesec, fancyhdr, tcolorbox, TikZ, listings, hyperref, and bookmark. A standard TeX Live installation with the corresponding mathematics, fonts, and extra-LaTeX collections is suitable. No network access is used by the build script once dependencies are installed. PDF metadata may vary across rebuilds; byte-identical output is not claimed.

## Evidence boundary

No Lean compilation was performed. Appendix B is a formalization plan and statement map, not a verified Lean library. The computational tests concern exact finite arithmetic only. They do not establish noncomputability, classify all infinite groups, or establish historical priority. The book supplies ordinary proofs for those mathematical claims under their stated contracts.

The classical direct-sum prime coding is explicitly attributed to Montalban. Other references ground the standard notions of profinite completion, pure subgroups, cocycles, and degrees of isomorphism types. Historical priority for the combined common-completion family is not asserted.

The preparation record is an internal mathematical and production review, not independent external peer review. See `ASSISTANCE_AND_PROVENANCE.md` and `verification/` for exact scope.
