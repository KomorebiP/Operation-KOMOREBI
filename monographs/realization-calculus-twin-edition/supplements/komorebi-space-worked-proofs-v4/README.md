# Komorebi Space: worked construction and proofs, v4

This package extends the v3 visual atlas with a 12-page mathematical companion,
fully worked coefficients and scalar calculations, and an expanded exact audit.
The original renderer and the original two figures are preserved.

## Start here

Open `Komorebi_Space_Worked_Proofs.pdf`. The first ten pages contain the construction,
proofs and verification record. The final two pages reproduce the visual plates.
The editable LaTeX source has the same basename.

The proof companion establishes:

1. The real Fourier spaces, their orthogonality and dimensions 9, 25, 81, 289.
2. Exact coefficient restriction, inclusion, nested projections and compatibility.
3. The 289-dimensional coherent space inside the 404-dimensional raw family space,
   together with a surjective 115-dimensional residual map and an explicit right inverse.
4. Split detail reconstruction, the dimensions 16, 56, 208 of the detail bands,
   and exact energy and point-value calculations for the plotted seed.
5. The residual (0, eta, -eta) caused by changing view 2. It proves the repair that
   preserves the other views and a different unconstrained least-squares repair.
6. Coordinate-swap transport and its compatibility with the square cutoffs.
7. The protected extension quotient and a branching example with nonzero obstruction.
8. A necessary and sufficient finite-energy condition for an infinite coherent
   Fourier family to have a realization in the declared Hilbert completion.

The proof distinguishes retained signal detail from compatibility defect and
from extension obstruction. It also distinguishes the adjacent-residual space
used in this chain from the all-arrow residual used in the monograph.

## Reproduce the exact finite verification

From this directory:

```sh
python verify_worked_example.py --output .
```

On Windows, `py` can replace `python`. NumPy and Matplotlib are needed only because
this command also imports and replays the original renderer's verifier.
No network connection is needed once dependencies are installed.

The successful run replayed 8,969 original checks and passed 3,695 added checks,
for 12,664 exact checks in total. `verification.json` contains the category counts
and source hashes. `worked_steps.json` contains explicit intermediate Fourier
coefficients, exact energies, values at the origin, defects, and repair costs.

All mathematical coefficient calculations use `fractions.Fraction`. The linear
identities are checked on complete bases, including all 404 raw-family basis
vectors and all 115 adjacent-residual basis vectors. The written proofs justify
linearity, Fourier orthogonality and the infinite convergence theorem.

This is not a Lean compiler run. Infinite-dimensional claims are proved in the
manuscript, not established by finite numerical testing. Floating-point values
are used to draw the trigonometric graphs, not to certify coefficient identities.

## Recreate the figures

```sh
python render_komorebi.py --output figures --dpi 300
```

Original PNG, SVG, PDF and preview files are in `figures/`. The renderer is unchanged
from v3. All main surfaces have one common vertical scale. The small detail
surfaces have twice that vertical gain, as labeled. The graphs are representations
of individual functions, not three-dimensional renderings of entire function spaces.

## Rebuild the proof PDF

A standard TeX installation with the packages named in the source is required:

```sh
pdflatex -interaction=nonstopmode -halt-on-error Komorebi_Space_Worked_Proofs.tex
pdflatex -interaction=nonstopmode -halt-on-error Komorebi_Space_Worked_Proofs.tex
```

The delivered PDF was compiled, rendered to page images, and visually reviewed.
The final compilation had no overfull-box, undefined-reference or LaTeX warnings.

## Source framework

The construction uses *Komorebi Space Monograph v1.13.0*, Sections 1, 3, 6 and 10,
and the explicit example introduced in the v3 visual atlas. This package does
not claim that the Fourier ingredients are historically new or that the example
exhausts the general Komorebi Space framework.

`PROGRESS_v4.md` records what was completed and the verification boundary.
`manifest.json` records SHA-256 hashes of all delivered files other than itself.
