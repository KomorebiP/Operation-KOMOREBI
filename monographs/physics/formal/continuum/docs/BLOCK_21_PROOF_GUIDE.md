# Block 21 — Three-dimensional continuum correction, velocity, and anisotropy

Komorebi Physics Lean v0.21.0. Source: *Projector-Refinement Physics: Complete Unified Theory*, physical PDF pages 41–42 of 550, printed pages 28–29. The literal targets are equations (8.31)–(8.41). The authoritative cumulative result is the completed PASS report at `verification/final/report.json`.

## 1. Scope and declaration counts

| Module | Theorems | Other declarations | Role |
|---|---:|---:|---|
| `Relativistic3DShellAsymptotics` | 15 | 7 | Energy, anisotropy polynomial, four-cosine Taylor expansion through sixth order |
| `Relativistic3DContinuumLimit` | 30 | 12 | Positive-spacing branch inversion and frequency correction |
| `Relativistic3DGroupVelocity` | 36 | 7 | Exact derivatives, component asymptotics, vector limit, derivative bridge |
| `Relativistic3DAnisotropy` | 15 | 4 | Fixed-radius axis-versus-diagonal comparison |
| `Relativistic3DContinuumExamples` | 14 | 0 | Nontrivial exact witnesses and specialized asymptotics |
| **Block 21** | **110** | **30** | **140 new inventoried declarations** |

The cumulative inventory contains **1,927 theorem declarations, 2,289 inventoried declarations, and 114 mathematical modules**. The 109 Block 20 mathematical modules are protected by `reference/block20_preservation.json`. These are formal declaration counts, not counts of independent physical discoveries or a percentage completion estimate for the manuscript.

## 2. Energy, anisotropy, and the shell expansion

Define

\[
E=\sqrt{m^2+k_x^2+k_y^2+k_z^2}
\]

and

\[
Q=m^2(k_x^2+k_y^2+k_z^2)
  +k_x^2k_y^2+k_x^2k_z^2+k_y^2k_z^2.
\]

The exact shell from Block 20 is

\[
C_\Delta=\cos(m\Delta)\cos(k_x\Delta)
\cos(k_y\Delta)\cos(k_z\Delta).
\]

`Relativistic3DShellAsymptotics` does not postulate a multivariable Taylor formula. It factors the shell into two already-controlled two-cosine shells, proves differentiability through the required order, computes the derivatives at zero through order six, and obtains

\[
\boxed{
C_\Delta
=1-\frac{E^2}{2}\Delta^2
 +\left(\frac{E^4}{24}+\frac{Q}{6}\right)\Delta^4
 +O(\Delta^6).
}
\]

The identity connecting the raw quartic moment to `E` and `Q` is proved algebraically. The remainder is a genuine one-sided asymptotic statement, not a finite polynomial match or numerical fit.

## 3. Branch-controlled inversion

The inverse step is delicate because `arccos` is singular at shell value one. The proof therefore follows the positive-spacing branch used in Block 19:

1. square the exact shell and normalize `1-C_Δ²` by `Δ²`;
2. prove convergence to `E²` and eventual positivity under `E ≠ 0`;
3. take the positive square root `radial3`;
4. rewrite the principal phase as an ordinary arcsine near `Δ=0+`;
5. use the checked cubic arcsine remainder and divide only on the positive-spacing filter.

The resulting coefficient is

\[
a(k)=-\frac{Q(k)}{6E(k)}.
\]

Lean proves

\[
\boxed{
\omega_\Delta(k)
=E(k)-\frac{Q(k)}{6E(k)}\Delta^2+O(\Delta^4)
}
\]

on `𝓝[>] 0`, under the explicit hypothesis `E ≠ 0`. It also proves `ω_Δ(k) → E(k)`. No two-sided positive-energy expansion is asserted, and the totalized value at `E=0` is not used to disguise a division-by-zero boundary.

## 4. Exact momentum derivatives and continuum velocity

The exact shell is differentiated separately with respect to `k_x`, `k_y`, and `k_z`. On the nonsingular principal branch,

\[
\partial_{k_x}\omega_\Delta
=
\frac{\cos(m\Delta)\sin(k_x\Delta)\cos(k_y\Delta)\cos(k_z\Delta)}
     {\sin(\omega_\Delta\Delta)},
\]

with the analogous cyclic formulas for `y` and `z`. The square-root denominator and sine denominator are proved equal on the principal branch rather than interchanged informally.

After normalizing each sine numerator by the spacing and reusing the common positive radial factor, Lean proves the stronger componentwise estimates

\[
\partial_{k_i}\omega_\Delta
=\frac{k_i}{E}+O(\Delta^2),
\qquad i=x,y,z.
\]

Consequently

\[
\boxed{
\nabla_k\omega_\Delta\longrightarrow \frac{k}{E}.
}
\]

The development also proves that the displayed components are eventually the actual derivatives of the original principal-frequency function, not merely asymptotically equivalent surrogate expressions.

## 5. Fixed-radius anisotropy

At fixed radius `κ`, define

\[
k_{\rm axis}=(\kappa,0,0),
\qquad
k_{\rm diag}=\frac{\kappa}{\sqrt 3}(1,1,1).
\]

Lean proves that both have the same exact continuum energy

\[
E=\sqrt{m^2+\kappa^2},
\]

while

\[
Q(k_{\rm axis})=m^2\kappa^2,
\qquad
Q(k_{\rm diag})=m^2\kappa^2+\frac{\kappa^4}{3}.
\]

Subtracting the two checked frequency expansions gives

\[
\boxed{
\omega_{\rm axis}-\omega_{\rm diag}
=\frac{\kappa^4}{18E}\Delta^2+O(\Delta^4).
}
\]

For `κ ≠ 0` and `E ≠ 0`, the coefficient is proved strictly positive. The massless unit-radius specialization is exactly `1/18`.

## 6. Exact witnesses and rejection tests

The witness `m=1`, `k=(1,0,0)` proves

\[
E=\sqrt2,
\quad Q=1,
\quad a=-\frac1{6\sqrt2},
\]

and specializes the frequency expansion, all three velocity components, and the eventual derivative bridge. The massless unit-radius axis/diagonal pair specializes the anisotropy coefficient to `1/18`.

Three new deliberately false controls reject the wrong correction sign, a vanished axis/diagonal coefficient, and omission of the diagonal quartic term. They supplement the 139 prior controls.

## 7. Exact boundary of the result

Block 21 checks equations (8.31)–(8.41). It does **not** yet check the observer-shell defect (8.42)–(8.48). That next step is not a mere substitution: the Lorentz-transformed momentum depends on the discrete energy, so the frequency must be controlled along a moving momentum path. The next block must prove that moving-argument transfer with an `O(Δ⁴)` remainder, not silently replace it by a fixed-momentum expansion.

No empirical validation, continuum field-theory limit, finite-spacing Lorentz invariance, or position-space locality theorem is claimed by this block.
