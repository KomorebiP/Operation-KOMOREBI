# Paper XII — Visual Appendix

An 18-page worked visual companion to **Patching Support, Hecke Packets, and
Conditional Automorphic Completion**, Komorebi P., formal release v0.17.0.
This is an editorial/expository edition, not a new Lean proof release.

## Read

- `Paper_XII_Visual_Appendix.pdf`: the 18-page appendix, with page labels V–1 through V–18.
- `Paper_XII_With_Visual_Appendix.pdf`: the original 36-page manuscript followed by the appendix (54 pages).

The original main-body figures remain in the 36-page manuscript. The new appendix
is additional reader-oriented material; it does not silently replace or rewrite the
original paper. Both parts have navigable PDF bookmarks, and appendix cross-references
are clickable. All 36 original pages have matching text and matching rendered output
in the combined edition.

## Contents

1. Seeing the objects: existence, support, realization, and three teaching models.
2. Object atlas and contravariance of points.
3. Completed local quotient: the exact monomials that survive `(x^2,y)`.
4. Point factorization: 625 candidate third-order points, five accepted points, and obstructed nonzero tangent directions.
5. Completion: compatible 5-adic digit prefixes at every precision.
6. Fitting geometry: the presentation `diag(x,y)` and fiber dimensions 0, 1, 2.
7. Same support, different nilpotent structure: `diag(x,y)` versus `diag(x^2,y)`.
8. Base change, coordinate transport, and an explicit presentation stabilization.
9. The exact three-point spectrum of the complete local node; branches are not projector packets.
10. Auxiliary freeness, missing component support, and a nonreduced special fiber.
11. Derived support in the two-term complex `[k[t] --t--> k[t]]`.
12. A five-dimensional nonsemisimple algebra, explicit CRT projectors, and Jordan chains.
13. Empty packet modules and the distinction between generalized packets and scalar fibers.
14. The coefficient-prime-two obstruction to sign projectors; augmentation recovery.
15. Stable cores: equal nonzero level dimensions can yield different inverse limits.
16. Fixed finite-carrier stabilization versus infinite tail escape.
17. The precise supplied-input/checked-consequence boundary of the final conditional theorem.
18. A theorem crosswalk, reading checks, and provenance.

## Rebuild

With Python 3.10+ and the listed Python packages installed, and a TeX distribution
providing `pdflatex`, run from this directory:

```text
python build.py
```

The script runs the exact checks, regenerates the mathematical TikZ graphics,
compiles the appendix twice, combines it with the preserved original PDF, and checks
page counts, page preservation, safe text bounds, internal link targets, and raster
image absence in the appendix. It does not contact the network or run Lean.

The TeX packages used are standard: geometry, fontenc, lmodern, microtype, amsmath,
amssymb, mathtools, graphicx, array, booktabs, tabularx, multicol, xcolor, TikZ,
tcolorbox, fancyhdr, hyperref, and bookmark. No font files are distributed.

## Edit

- `appendix.tex`: typography, page style, and mathematical macros.
- `source/pages.tex`: all explanatory text, formulas, references, and inline diagrams.
- `source/generate_graphics.py`: deterministic vector-figure generation.
- `graphics/*.tex`: generated, fully editable TikZ graphics.
- `checks/verify_examples.py`: independent exact symbolic and finite arithmetic checks.
- `original/source/`: original manuscript LaTeX, bibliography, and original vector figures, preserved from the formal release.
- `original/Paper_XII_v0.17.0.pdf`: the unmodified baseline used by the integration script.

Changing the original PDF changes the preservation baseline. The supplied bundle
uses the exact original 36-page PDF from this conversation. Rebuilding with different
software versions may change PDF metadata and typography; the mathematical data and
figure-generation rules are deterministic.

## Mathematical and verification boundaries

The appendix adds no Lean declarations and does not change the inherited 49-claim
revised contract. No Lean suite was rerun for this editorial task. Original versus
revised statement boundaries and external arithmetic inputs remain unchanged.

`checks/EXACT_CHECKS.json` records **31 passing exact checks**, including exhaustive
finite-ring enumeration and exact symbolic/matrix calculations. The finite checks
have explicit domains and limits. Uniform infinite claims have arguments in the
appendix; they are not inferred by extrapolating a plotted window.

The coordinate sketches are explicitly labeled real closed-point shadows. They are
not presented as complete drawings of an affine or formal scheme. The complete local
node's three-point specialization diagram is instead an exact description of that
particular prime spectrum.

The finite commutative algebra used to teach packets is a toy model, not a claim that
an arithmetic automorphic carrier has been constructed.

## Audit

- `checks/BUILD_AUDIT.json`: page counts, vector-image checks, source hashes, page-preservation comparisons, and link checks.
- `checks/EXACT_CHECKS.json`: arithmetic and symbolic verification results.
- `checks/VISUAL_REVIEW.md`: renderer and editorial review record.
- `checks/DEVELOPMENT_NOTES.md`: corrected development issues and remaining scope limits.
- `MANIFEST_SHA256.json`: hashes of the delivered source and output files.

Primary references are the theorem numbers in the supplied manuscript. This appendix
introduces no unverified external literature claims.
