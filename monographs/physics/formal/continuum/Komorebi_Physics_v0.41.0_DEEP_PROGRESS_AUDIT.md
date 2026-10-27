# Block 41 deep progress audit

## Scientific transition

Blocks 35–40 completed the finite-state to Euclidean-`L²` reconstruction layer.
Block 41 begins the dynamics layer. It identifies the exact Fourier multiplier
of the central finite difference and proves that the resulting free Dirac
symbol approaches the continuum Dirac symbol quadratically on every fixed mode.

## Exact algebra

For `h ≠ 0`, the central translation quotient is

\[
(e^{ikh}-e^{-ikh})/(2h).
\]

Euler's identity gives `i sin(kh)/h`; the formal definition fills its removable
value `ik` at zero. Multiplication by the Hamiltonian prefactor `-i` yields the
real lattice momentum `sin(kh)/h`.

The explicit four-component Clifford representation proves the exact continuum
and lattice mass-shell squares. These are identities of spinor operators, not
numerical tests.

## Asymptotic control

The existing checked scalar estimate `sin(kh)/h - k = O(h²)` is transported
through continuous linear maps to fixed spinors and summed over three spatial
components. The resulting symbol residual is `O(h²)`. The same closure is used
for any fixed finite Fourier packet.

## Interpretation

This establishes consistency of the central-difference free Dirac generator on
finite Fourier data. It is the local algebraic ingredient expected in a
trigonometric-polynomial core proof on the flat torus.

## Unclosed analytical steps

The current packet theorem is pointwise. A complete generator theorem still
needs:

1. a torus `L²` realization of the trigonometric-polynomial core;
2. an `L²` norm estimate for the symbol residual;
3. symmetry/self-adjointness or an equivalent stability theorem;
4. strong resolvent or graph convergence;
5. strong convergence of `exp(-it H_h)` to `exp(-it H_D)`.

Gauge-covariant generator convergence is later still: Block 41 is the free
symbol layer.
