# Block 41 proof guide — Fourier-mode Dirac generator consistency

## Scope

Block 41 is the first dynamical continuum-consistency layer after the Euclidean
state-space reconstruction. It works on fixed integer Fourier modes of a flat
three-torus and on finite Fourier packets. It does not yet prove an operator
limit on the full continuum Hilbert space or propagator convergence.

## 1. Exact central finite-difference multiplier

For a one-dimensional mode with wave number `k`, the translation phase is

\[
e^{i k h}.
\]

The central derivative multiplier is defined by

\[
\frac{e^{ikh}-e^{-ikh}}{2h}
\]

for nonzero `h`, with the removable value `ik` inserted at zero. Lean reduces
this expression exactly to

\[
i\,\frac{\sin(kh)}{h}.
\]

The `-i` factor in the Dirac Hamiltonian therefore produces the real lattice
momentum `sin(kh)/h` exactly.

## 2. Quadratic scalar error

The prior checked theorem

\[
\frac{\sin(kh)}{h}-k=O(h^2)
\]

is transported from real scalars to complex scalars by `Complex.ofRealCLM`, and
then to a fixed four-spinor by a scalar-multiplication continuous linear map.
This yields the reusable theorem `sinQuot_residual_smul_isBigO`.

## 3. Clifford symbol

The continuum symbol is

\[
H(k)=k_x\alpha_x+k_y\alpha_y+k_z\alpha_z+m\beta.
\]

The central-difference symbol substitutes

\[
k_j\mapsto \frac{\sin(k_jh)}{h}.
\]

The mass terms cancel in the difference, leaving the sum of the three scalar
multiplier residuals. Closure of `IsBigO` under finite addition gives

\[
H_h(k)\psi-H(k)\psi=O(h^2).
\]

## 4. Exact mass shell

The explicit four-spinor Clifford representation is unfolded componentwise.
After normalization of `I^2=-1`, polynomial normalization proves

\[
H(k)^2=(m^2+k_x^2+k_y^2+k_z^2)I.
\]

Substitution of the lattice momenta gives

\[
H_h(k)^2=
\left(m^2+\sum_j\left(\frac{\sin(k_jh)}{h}\right)^2\right)I.
\]

## 5. Integer torus modes and finite packets

An integer mode `n : Fin 3 → ℤ` carries momentum `2π n`. The associated plane
wave has complex norm one. The modewise `O(h²)` theorem is specialized to these
momenta.

For a fixed finite support `S`, the packet action is a finite sum of plane-wave
multiples of the mode symbols. `IsBigO.sum` closes the modewise estimates and
proves pointwise packet consistency and convergence.

## Boundary

The packet result is pointwise in the torus coordinate and fixed finite support.
No uniform-in-support estimate, full `L²` generator theorem, self-adjointness
statement, resolvent convergence, or propagator convergence is claimed here.
