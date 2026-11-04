# Lean verification of polynomial transport

**Recorded 4 November 2026 · Komorebi P.**

The [polynomial transport companion](../formal/polynomial-transport/README.md) constructs the concrete coordinate map, residue operators, Fourier average, and transported product used in the [roots-of-unity and falling-factorial example](demonstrations/ROOTS_UNITY_FALLING_FACTORIAL.md). The earlier reader companion supplied generic additive transport. This extension supplies the actual finite polynomial objects and proves their compatibility.

## What is now formalized

The project contains **66 named theorem declarations and 10 definitions** across six modules. These counts include supporting lemmas, explicit witnesses, and one restatement of the classical Stirling identity already present in the earlier reader companion. The retained generic transport module and the positive controls are audited separately.

| Module | Theorem declarations | Definitions | Formal scope |
|---|---:|---:|---|
| [PolynomialPackets](../formal/polynomial-transport/KomorebiPolynomial/PolynomialPackets.lean) | 15 | 2 | Finite polynomial coefficient masks over a semiring, linearity, projector laws, reconstruction, refinement and coefficient extension. |
| [FallingFactorial](../formal/polynomial-transport/KomorebiPolynomial/FallingFactorial.lean) | 12 | 3 | The actual rational falling-factorial basis equivalence, its inverse on powers, constants, degree preservation and nonmultiplicativity. |
| [FallingPackets](../formal/polynomial-transport/KomorebiPolynomial/FallingPackets.lean) | 15 | 2 | The concrete conjugated projectors, their finite formulas and laws, and complete input/output block reconstruction. |
| [RootsOfUnity](../formal/polynomial-transport/KomorebiPolynomial/RootsOfUnity.lean) | 7 | 1 | The actual complex polynomial substitution average, its coefficient formula, the canonical exponential root and rational coefficient compatibility. |
| [FourierBridge](../formal/polynomial-transport/KomorebiPolynomial/FourierBridge.lean) | 2 | 0 | The equality connecting the rational falling-coordinate projector to complex Fourier averaging. |
| [FallingProduct](../formal/polynomial-transport/KomorebiPolynomial/FallingProduct.lean) | 15 | 2 | Transported multiplication, its algebraic laws, basis-degree addition and exact cyclic packet convolution. |

The [claim map](../formal/polynomial-transport/CLAIM_MAP.json) gives every declaration's exact signature, coefficient domain, reading-page correspondence and pinned source dependencies. Counts describe declarations, rather than independent mathematical discoveries or complete coverage of every section on the page.

## The coordinate map has the required direction

The constructed linear equivalence is

\[
\Phi:\mathbb Q[z]\simeq_{\mathbb Q}\mathbb Q[x],
\qquad \Phi(z^k)=x^{\underline{k}}.
\]

Lean represents both carriers as \(\mathbb Q[X]\). Their two roles are fixed by the actual equivalence and its inverse. The construction uses bases with finitely supported coordinates. It preserves degree, including the zero polynomial's degree convention, and fixes every rational constant.

The inverse-power formula is proved for every natural \(n\):

\[
\Phi^{-1}(x^n)=\sum_{k=0}^{n}S(n,k)z^k.
\]

In particular, \(\Phi(z^2)=x^2-x\), while \(\Phi^{-1}(x^2)=z^2+z\). The map is linear and has an actual inverse. It does not preserve ordinary polynomial multiplication.

## Fourier averaging and falling packets agree

For a positive modulus \(N\), a canonical residue \(0\le r<N\), and a primitive complex \(N\)-th root \(\zeta\), the companion proves the polynomial identity

\[
P_r^{(N)}p(z)
=\frac1N\sum_{\ell=0}^{N-1}\zeta^{-r\ell}p(\zeta^\ell z).
\]

The right side uses actual polynomial substitution. The proof uses the negative integer exponent directly and compares every coefficient. It applies to arbitrary finite polynomials, with no degree cutoff. Positive composite moduli and \(N=1\) are included. A separate theorem supplies the canonical root \(e^{2\pi i/N}\).

On rational polynomials, the actual falling-factorial projector is

\[
Q_r^{(N)}=\Phi P_r^{(N)}\Phi^{-1}.
\]

Its coefficients are selected in the falling basis. This gives

\[
Q_0^{(2)}(x^2)=x^2-x,
\qquad Q_1^{(2)}(x^2)=x.
\]

Both packets reconstruct \(x^2\). The displayed fifth-degree example is also checked exactly: the three packets of \(x^5\) at \(x=4\) are \(600,244,180\).

Let \(\iota\) extend rational coefficients to complex coefficients. The named connecting theorem proves

\[
\iota\!\left(\Phi^{-1}(Q_r^{(N)}f)\right)
=\frac1N\sum_{\ell=0}^{N-1}\zeta^{-r\ell}
  (\iota\Phi^{-1}f)(\zeta^\ell z).
\]

Thus the two formulas agree on their correctly typed coordinate descriptions. The comparison occurs in \(\mathbb C[z]\) after the rational coordinate map has been applied.

Idempotence, orthogonality, reconstruction, and divisible-modulus refinement are proved for the actual \(Q_r^{(N)}\). Refinement uses the filtered-address form: sum the fine packets whose addresses have the requested coarse residue.

## Multiplication follows the same coordinate change

The product from Section 9 is constructed as

\[
f\star g=\Phi(\Phi^{-1}f\cdot\Phi^{-1}g).
\]

The companion proves associativity, commutativity, the unit and rational bilinearity, together with

\[
x^{\underline a}\star x^{\underline b}=x^{\underline{a+b}},
\qquad x\star x=x(x-1)\ne x^2.
\]

For every positive modulus, the complete packet product is the exact cyclic convolution

\[
Q_r^{(N)}(f\star g)=
\sum_{\substack{0\le a,b<N\\(a+b)\bmod N=r}}
(Q_a^{(N)}f)\star(Q_b^{(N)}g).
\]

The supporting coefficient-packet convolution is proved over every semiring before transport to the rational falling-factorial coordinates.

## Evidence and remaining scope

The [recorded replay](../formal/polynomial-transport/verification/2026-11-04/run.json) binds the sources, verification program and compiler logs by SHA-256. It includes a fresh build, exact declaration and axiom audits, project kernel replay, **18 named positive-control theorems**, and **eight deliberate rejection controls**. The controls cover the direction of \(\Phi\), the displayed packet values, Fourier normalization and sign, invalid primitivity, zero-modulus reconstruction, ordinary-projector reuse, ordinary-product reuse and an unfinished proof.

The [internal statement review](../formal/polynomial-transport/REVIEW.md) records its source hashes and checks the correspondence between the Lean statements and the reading claims. The [Mathlib dependency record](../formal/polynomial-transport/SOURCE_DEPENDENCIES.md) identifies the exact upstream results and hypotheses. The [replay instructions](../formal/polynomial-transport/README.md#evidence-and-reproduction) use the pinned Lean 4.34.0-rc2 toolchain. The [Reader Lean companions workflow](https://github.com/KomorebiP/Operation-KOMOREBI/actions/workflows/reader-lean-companions.yml) reruns the project on relevant changes.

The formalized falling-factorial equivalence is over \(\mathbb Q\). The complex averaging theorem supplies a realization of the cyclotomic expression in \(\mathbb C[X]\). The explicit signed-first-Stirling matrix entries, cyclic permutation trace formula, arithmetic-progression reindexing of refinement, constructive Newton interpolation, concrete difference and translation operators, rational spectral-projector formula, characteristic-three arguments, and infinite-series identities remain outside this companion. The transported-product theorem does not yet establish the page's \(\Delta\)-derivation rule.

[Earlier Lean companions](LEAN_READER_COMPANIONS.md) · [Worked example](demonstrations/ROOTS_UNITY_FALLING_FACTORIAL.md) · [Run and verify](VERIFICATION.md)
