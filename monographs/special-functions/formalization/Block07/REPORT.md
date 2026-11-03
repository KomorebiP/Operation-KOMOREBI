# SF-LEAN-B07: the characteristic exponent and positive eigenvectors

This block proves the characteristic-exponent prerequisites stated before
Theorem F.2. For labeled real scales 0<q,r,a,b<1, there is a unique rho>0 with

\[
(1-q^\rho)(1-b^\rho)=(ar)^\rho.
\]

For the real matrix P(t)=[[q^t,r^t],[a^t,b^t]], the block verifies the positive
right and left eigenvectors at this exponent, max-normalizes the right
vector, computes the exact spectrum after extension to the complex numbers,
and proves that spectral radius one is equivalent to the determinant equation
for every t>0. In particular the spectral characterization also has a unique
positive exponent.

The new source contains **23 named theorem declarations**, including
supporting lemmas. The registered scope is **179 names**: 39 in the inherited
finite core and 29,21,19,16,13,19,23 in Blocks01 through 07. This is not a
proof of F.2's analytic growth bounds or of the whole monograph.

## A continuous, strictly increasing balance

Define H(t)=(1-q^t)(1-b^t)-(ar)^t using **real powers**. Positive bases make
H continuous. On t>=0 the first product is nondecreasing, since each factor
is nonnegative and nondecreasing. The subtracted term (ar)^t strictly
decreases, so H is strictly increasing on that half-line.

The exact endpoint values are H(0)=-1 and H(t)->1 as t->infinity. The latter
uses 0<q,b,ar<1. Eventually H(T)>0 for some T>0. The intermediate value
theorem gives a zero in [0,T], H(0) rules out zero, and strict monotonicity
gives uniqueness among positive exponents. No uniqueness on all real
exponents is claimed. `characteristicExponent` chooses this proved unique
positive root; its specification includes positivity and the balance equation.

## Eigenvectors and normalization

At the root, the right vector is (r^rho,1-q^rho) and the left vector is
(a^rho,1-q^rho). The source expresses the left identity by multiplying its
column vector by the transpose of P; this is equivalent to ell^T P=ell^T.
Both coordinates are strictly positive. Division by the maximum right
coordinate preserves the eigenvector equation, keeps both coordinates
positive and makes their maximum exactly one. It is not sum normalization.

The identity (ar)^rho=a^rho r^rho uses positivity of the real bases. The
other eigenvalue is lambda=q^rho+b^rho-1, and -1<lambda<1 follows from
0<q^rho,b^rho<1. The exact complex spectrum is {1,lambda}, with both real
numbers embedded into the complex field. Mathlib's actual `spectralRadius`
of this complex matrix is therefore one; it is not a renamed scalar proxy.

## Converse spectral characterization

For any positive t, the characteristic polynomial has the explicit equation
(z-q^t)(z-b^t)-r^t a^t=0. Positivity of both off-diagonal entries forces
every complex root to be real: the imaginary-part equation would otherwise
set Re(z)=(q^t+b^t)/2, contradicting the real-part equation and the strictly
positive off-diagonal product.

The complex spectrum is nonempty by finite dimensionality and algebraic
closure, and finite because it is the zero set of a nonzero characteristic
polynomial. Its norm maximum is attained. Spectral radius one thus gives a
real eigenvalue of modulus one. The value -1 cannot occur: the diagonal
entries are positive and the off-diagonal product is below one. The remaining
eigenvalue 1 gives precisely the determinant balance. This proves both
directions of the spectral characterization without a numerical eigensolver
or a general Perron-Frobenius comparison theorem.

## Interfaces and correspondence

- `characteristic_exponent_exists_unique`, `characteristicExponent_spec`:
  the unique positive real balance root and its chosen representative.
- `characteristic_right_eigenvector`, `characteristic_left_eigenvector`:
  exact matrix-vector identities in the stated row/column convention.
- `normalizedCharacteristicVector_positive`,
  `normalizedCharacteristicVector_max`, `normalized_characteristic_eigenvector`:
  positivity, max normalization and the eigenvector identity.
- `characteristic_spectrum`, `characteristic_second_eigenvalue_bound`,
  `characteristic_spectralRadius`: exact spectrum and radius at the root.
- `characteristic_spectrum_real`, `characteristic_spectrum_norm_attained`,
  `characteristic_spectralRadius_iff`,
  `characteristic_spectral_exponent_exists_unique`: the converse and uniqueness
  of the spectral characterization.

The exact source locator is the characteristic-exponent and positive-vector
section of `monograph/sections_v11/coupled_growth_full.tex`, before Theorem
F.2. See [CLAIM_MAP.json](CLAIM_MAP.json) and [declarations.json](declarations.json).

## Verification and file I/O

The source-bound [receipt](evidence/receipt.json) has **36 steps**: version
identification, nine dependency revision checks, warning-as-error compilation
and exact axiom audits for seven coupled modules, same-kernel replay of those
modules, four rejection fixtures and one positive interface fixture. The
freshly audited coupled scope is 140 declarations; the finite core's 39-name
evidence is inherited. Only propext, Classical.choice and Quot.sound are
allowed logical axioms. Cached Mathlib imports are reused rather than freshly
rebuilt or replayed from an empty environment.

The controls reject a zero exponent, using the left eigenvector as a right
eigenvector without transposition, confusing max normalization with sum
normalization, and placeholder proofs. The positive fixture checks the
preserved rational tuple: exponent one, normalized right vector (1/2,1),
the transposed left identity, spectral radius one, and second eigenvalue
-1/10. The symmetric all-half tuple has normalized vector (1,1) and radius
one at exponent one. An exact boundary check shows the all-one tuple has no
balance root. No sampled root or floating-point eigenvalue is load-bearing.

The native environment remains Lean 4.34.0-rc2 and Mathlib
`aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. Preparation fetched 128 and 55
missing cache entries for the matrix/spectral APIs and complex algebraic
closure, using the pinned checkout. No package revision changed. The public
verifier performs no installation or network access.

```text
python tools/verify_coupled_characteristic.py --toolchain /path/to/toolchain --mathlib /path/to/mathlib --work /path/to/new/sf-block07
```

Use a new work directory outside the release; --git and --packages support
portable local layouts. [IO_MANIFEST.json](IO_MANIFEST.json) inventories actual
input hashes, output log/receipt hashes and generated object hashes, with the
objects explicitly marked as unbundled replay outputs.
[SOURCE_MANIFEST.json](SOURCE_MANIFEST.json) seals the immutable records,
dated guide and every replay input. Review is [self-review](SELF_REVIEW.md),
not independent review.

## Phase closeout and continuation

Base: `ac74a88377d7c5a4daa8bc463d3f45629277e192`. Cutoff and assessment are
the same SF-LEAN-B07 source-bound checkpoint. Earlier proof blocks, their
records and dated guides, manuscript sources and reading PDFs are preserved.
Current sources, I/O, catalogue and continuation files are updated. No new
complete archive release is claimed.

The explicit balance/2x2-spectrum route resolves this block's target. General
positive-matrix comparison and logarithmic reparametrization remain deferred
alternatives: use them if later larger-matrix results or root enclosures need
them. They were not refuted. The [Block06 closeout](../Block06/REPORT.md)
retains the component-rescaling result and earlier deferred methods.

Next: formalize the positive-real evaluation and comparison inequalities used
in F.2, starting with U(R),V(R)>=R and the eventual lower recurrence along
contracted radii. Then establish the explicit lower and upper type bounds,
the radial exponent limit, and the type-vector proportions. The characteristic
exponent and matrix identities are prerequisites, not those growth estimates.
Operator decoupling and broader monograph coverage remain separate obligations.
