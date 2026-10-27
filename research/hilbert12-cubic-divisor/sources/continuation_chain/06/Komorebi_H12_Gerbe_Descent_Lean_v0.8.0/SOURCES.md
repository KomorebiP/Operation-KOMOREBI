# External theorem check and notation dictionary

Checked during this v0.8.0 continuation. This is a theorem-application check,
not a novelty survey. Primary mathematical sources only are used below.
Source PDFs are not redistributed in this package.

## Holomorphic gerbe condition and topologically trivial group

Oren Ben-Bassat, *Gerbes and the Holomorphic Brauer Group of Complex Tori*,
arXiv:0811.2746v3, revised 5 February 2013.
https://arxiv.org/html/0811.2746v3

Section 6, exponential sequence and Definition 2: the topological image is
H^3(X,Z) intersect (H^{1,2} + H^{2,1}). The kernel of the DD class is the
quotient of H^2(X,O) by the image of H^2(X,Z). Applied to our specific product
CM torus, this gives the analytic interpretation of our exact Hodge matrices.
The paper does not compute our matrix's fixed classes or choose a gamma descent.

## Gamma gerbe and primitive topological class

Giovanni Felder, *Elliptic gamma functions, triptic curves and SL3(Z)*,
arXiv:math/0604588v1, 27 April 2006, reporting joint work with Andre Henriques,
Carlo A. Rossi and Chenchang Zhu.
https://arxiv.org/pdf/math/0604588v1

Theorems 4 and 5, page 3: for a rank-three oriented triptic curve the DD group
is Z and the gamma gerbe has generator DD class. Theorem 1, page 2, specifies
its meromorphic-section interpretation. The full source is Felder, Henriques,
Rossi and Zhu, *A gerbe for the elliptic gamma function*, math/0601337v1.
The short account is an author-written primary statement, not a search snippet.
Its title page and theorem page were checked.

Our smoothing application uses the lattice map diag(1,1,5) for z -> 5z between
bases (tau,s,1) and (5tau,5s,1). Pullback multiplies the oriented H^3 class by
five. Therefore the tensor quotient G^5 / pullback(G_coarse) has DD class zero.
This is not an asserted compact descent or value theorem.

## Smoothing convention

Bergeron, Charollois, Garcia, *Elliptic units for complex cubic fields
(On Eisenstein's Jugendtraum)*, arXiv:2311.04110v2, equation (2.13) and the
pure-cubic example.
https://arxiv.org/html/2311.04110v2

The numerator fifth power and denominator with simultaneously scaled argument
and periods are matched to the project's fixed convention. Existing modulus
results are not upgraded to phase comparisons.

## Elliptic pairing orientation

Steven D. Galbraith, *The Weil pairing on elliptic curves over C*, author note,
15 February 2011 revision, section 3, page 2.
https://www.math.auckland.ac.nz/~sgal018/pair-over-C.pdf

For P=(a+b tau)/ell and Q=(c+d tau)/ell with integer coordinates, the stated
pairing is exp(2 pi i(ad-bc)/ell). With tau=omega, ell=7, our two coordinate
vectors are (-1,-3) and (2,3), determinant three. Changing pairing convention
or reversing arguments inverts the phase; the convention is not left implicit.

## Stein-cover triviality

Joachim Wehler, *Stein Manifolds*, LMU Winter Semester 2021/22 lecture notes,
Draft Release 4.3, 4 September 2022, Theorem 6.22, printed page 206 (PDF page 210).
https://www.mathematik.uni-muenchen.de/~wehler/20190530_Stein_Manifolds_script.pdf

Cartan theorem B: every coherent O-module on a Stein manifold is acyclic.
X=(C^*)^3 is Stein, for example by its closed embedding z_i w_i=1 in C^6.
Hence the exponential sequence identifies H^2(X,O^*) with H^3(X,Z).
This proves existence of a holomorphic trivialization for the topologically
trivial smoothed pullback, not a canonical trivialization or scalar value.

## Boundary

The geometric conclusions in PROOF.md are ordinary deductions from these
sources and the explicit matrix calculations. The Lean source checks the
finite/integer coefficient statements; it does not implement analytic sheaf
cohomology, gerbes, Cartan's theorem, or the missing gamma comparison.
