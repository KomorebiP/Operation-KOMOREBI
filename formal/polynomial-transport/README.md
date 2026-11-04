# Polynomial packets and falling-factorial transport

**Komorebi P. · 4 November 2026**

This companion constructs the polynomial coordinate change used in the
[roots-of-unity and falling-factorial example](../../docs/demonstrations/ROOTS_UNITY_FALLING_FACTORIAL.md)
and connects it to the actual finite complex averaging formula.

The production inventory contains 66 named theorem declarations and 10
definitions. It includes supporting lemmas, explicit witnesses and one
restated classical Stirling helper. The 18 positive control theorems and the
retained generic transport declarations are counted separately.

The forward linear equivalence is

\[
\Phi:\mathbb Q[X]\simeq_{\mathbb Q}\mathbb Q[X],
\qquad \Phi(X^k)=X^{\underline{k}}.
\]

It is built from the ordinary monomial basis and the monic descending
Pochhammer basis. Its inverse, degree preservation, finite coefficient formula,
and inverse-power Stirling formula are proved. In particular,
\(\Phi(X^2)=X^2-X\), whereas \(\Phi^{-1}(X^2)=X^2+X\).

## Polynomial and Fourier projectors

`Packets.packet N r` retains the coefficients at degrees `k` whose remainder
`k % N` equals `r`. For positive `N`, residue labels satisfy `r < N`;
labels outside that range give the zero polynomial. Its input and output are
actual polynomials, so finite support is
part of the carrier. The coefficient ring may be any semiring. Reconstruction
requires `N > 0`; refinement requires a positive finer modulus divisible by
the coarse modulus.

For `N > 0`, `r < N`, and a primitive complex `N`-th root `ζ`, the theorem
`RootsOfUnity.average_eq_packet` proves the polynomial identity

\[
\frac1N\sum_{\ell=0}^{N-1}\zeta^{-r\ell}p(\zeta^\ell X)
=P_r^{(N)}p.
\]

The formula uses the negative integer exponent directly. It applies to every
finite complex polynomial, without a degree cutoff. The canonical exponential
root and the extension of rational coefficients to complex coefficients have
separate corollaries.

## Concrete falling-factorial packets

The operator on rational polynomials is constructed as

\[
Q_r^{(N)}=\Phi P_r^{(N)}\Phi^{-1}.
\]

The companion proves its finite falling-coordinate formula, idempotence,
orthogonality, reconstruction, divisible-modulus refinement, and complete
input/output block reconstruction for a transported linear operator.

Let \(\iota:\mathbb Q[X]\to\mathbb C[X]\) extend coefficients. The exact
comparison between the two descriptions is

\[
\iota\!\left(\Phi^{-1}(Q_r^{(N)}f)\right)
=\frac1N\sum_{\ell=0}^{N-1}\zeta^{-r\ell}
  (\iota\Phi^{-1}f)(\zeta^\ell X).
\]

This equation compares objects in \(\mathbb C[X]\). The inverse coordinate
map \(\Phi^{-1}\) acts on \(\mathbb Q[X]\), exactly as declared.

## Transported multiplication

The companion also constructs the product from Section 9:

\[
f\star g=\Phi(\Phi^{-1}f\cdot\Phi^{-1}g).
\]

It proves associativity, commutativity, the unit, rational bilinearity, and
\(X^{\underline a}\star X^{\underline b}=X^{\underline{a+b}}\). For \(N>0\),
its residue packets satisfy the exact cyclic convolution law

\[
Q_r^{(N)}(f\star g)=
\sum_{a,b=0}^{N-1}
\mathbf1_{(a+b)\bmod N=r}\,
  (Q_a^{(N)}f)\star(Q_b^{(N)}g).
\]

The same coefficient-packet convolution is proved over an arbitrary semiring
before applying the rational falling-factorial equivalence. The distinction
from ordinary target multiplication is proved already at
\(X\star X=X(X-1)\ne X^2\).

## Evidence and reproduction

The [claim map](CLAIM_MAP.json) records every named declaration, the exact
signature and module context, its reading-page correspondence, and source
dependencies. The [statement review](REVIEW.md) records its own scope and
source hashes. The [native replay](verification/2026-11-04/run.json) binds the
checked inputs, verification program, compiler diagnostics, and axiom lists.

From the repository root, with the pinned portable runtime already extracted:

```text
python -B tools/verify_lean_companion.py --project formal/polynomial-transport --runtime /absolute/path/Komorebi_Portable_Lean_4.34.0-rc2 --output /tmp/polynomial-transport-replay
```

Use a new or empty output directory. A standard Lean installation can prepare
the dependencies at the committed pins and omit `--runtime`.

The toolchain is Lean 4.34.0-rc2 at compiler commit
`6a10ac8c22beadecabdbb0919c2b50214762f91d`, with Mathlib revision
`aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. The verifier builds the project in a
fresh directory, audits the exact declaration inventory, replays project
modules, checks positive controls, and requires deliberate false assertions
to fail for the intended reason. It accepts only `propext`, `Classical.choice`,
and `Quot.sound` as axiom dependencies. Replay uses the same Lean kernel and
pinned imports, rather than an independently implemented verifier.

The retained generic additive-transport module is copied byte for byte from
the earlier reader companion and audited separately. The classical
second-Stirling polynomial identity is restated as a helper for the inverse
formula; its earlier coverage is identified in the claim map.

## Formal boundary

The falling-factorial equivalence here is over the rational numbers. Its
extension to arbitrary coefficient rings, the explicit signed-first-Stirling
coefficient formula, constructive Newton interpolation, concrete difference
and translation operators, spectral-projector formulas, and infinite-series
or analytic claims have separate proof obligations.

[Public verification guide](../../docs/LEAN_POLYNOMIAL_TRANSPORT.md) ·
[Earlier reader companions](../reader-examples/README.md)
