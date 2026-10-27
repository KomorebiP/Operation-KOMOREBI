# Block 17 — Exact one-dimensional discrete relativistic sector

Komorebi Physics Lean v0.17.0. Source: *Projector-Refinement Physics: Complete Unified Theory*, physical PDF page 40 of 550, printed page 27. The literal target is Chapter 8.1 equations (8.1)–(8.10), before the small-spacing asymptotics in (8.11)–(8.17). The authoritative cumulative machine result is `verification/final/report.json` after the production audit completes.

## 1. Scope and inventory

| Module | Theorems | Other declarations | Role |
|---|---:|---:|---|
| `RelativisticPauli` | 25 | 5 | Actual Pauli matrices, anticommutation, Hermiticity, traces, determinants and exact diagonalizer |
| `InvolutionExponential` | 21 | 1 | Literal matrix exponentials, Pauli closed forms, unitarity and determinant one |
| `DiracWalk1D` | 20 | 3 | Ordered mass/shift update, exact entries, unitarity, determinant and trace shell |
| `Dispersion1D` | 20 | 3 | Principal branch, shell-domain proof, uniqueness and characteristic polynomial |
| `Relativistic1DExamples` | 15 | 0 | Exact nontrivial half-turn witness and branch/order tests |
| **Block 17** | **101** | **12** | **113 new inventoried declarations** |

The cumulative inventory has 1,562 theorem declarations, 1,844 inventoried declarations and 96 mathematical modules. The previous 91 mathematical source modules are protected by `reference/block16_preservation.json`. These are declaration counts, not independent physical discoveries or a completion percentage for the 550-page source.

## 2. Equation (8.1): actual Pauli algebra

The spin index type is `Fin 2`. The matrices are constructed explicitly as

\[
\alpha=\sigma_z=\begin{pmatrix}1&0\\0&-1\end{pmatrix},\qquad
\beta=\sigma_x=\begin{pmatrix}0&1\\1&0\end{pmatrix}.
\]

Lean proves entrywise that

\[
\alpha^2=I,\qquad \beta^2=I,\qquad
\alpha\beta+\beta\alpha=0,
\]

and the stronger identity `alpha_beta_eq_neg_beta_alpha`. Hermiticity, zero trace and determinant minus one are also proved. The proofs do not introduce abstract matrices carrying these laws as structure fields.

An explicit matrix

\[
P=\begin{pmatrix}1&1\\1&-1\end{pmatrix},\qquad
P^{-1}=\frac12P
\]

is constructed and proved invertible, with `β=P α P⁻¹`. This supplies the similarity used to evaluate the β exponential.

## 3. Literal matrix exponentials, not merely closed-form definitions

The source writes

\[
e^{-i\theta A}=\cos\theta\,I-i\sin\theta\,A
\]

for involutive generators. This block proves the identity for the two actual Pauli generators used by the model:

\[
\exp(-i\theta\alpha)=\cos\theta I-i\sin\theta\alpha,
\]

\[
\exp(-i\theta\beta)=\cos\theta I-i\sin\theta\beta.
\]

The left side is Mathlib's genuine matrix exponential. For α, the proof evaluates the diagonal exponential coordinatewise. For β, the proved similarity `β=PαP⁻¹` and `Matrix.exp_conj` transport the α result. Euler's complex exponential formulas are proved separately.

This is enough for Chapter 8.1. The release does **not** claim a separate generic theorem for every matrix `A` satisfying `A²=I`; only the actual Pauli involutions are required and checked here.

The scaled generators are proved skew-Hermitian. Their exponentials therefore satisfy both unitary identities, and direct determinant calculations give determinant one.

## 4. The ordered update is the literal product in (8.2)

Define

\[
M(m,\varepsilon)=\exp(-im\varepsilon\beta),\qquad
S(k,\varepsilon)=\exp(-ik\varepsilon\alpha),
\]

and

\[
U_\varepsilon(k)=M(m,\varepsilon)S(k,\varepsilon).
\]

The order is part of the definition. Each factor is reduced to its proved trigonometric form, and the full matrix is calculated exactly. The release derives

\[
U_\varepsilon(k)^\dagger U_\varepsilon(k)=I,
\qquad
U_\varepsilon(k)U_\varepsilon(k)^\dagger=I,
\]

and

\[
\det U_\varepsilon(k)=1.
\]

The normalized trace is

\[
\boxed{\frac12\operatorname{Tr}U_\varepsilon(k)
=\cos(m\varepsilon)\cos(k\varepsilon).}
\]

This checks (8.2)–(8.5) and the trace derivation in (8.9)–(8.10) without a numerical approximation.

## 5. Exact principal dispersion branch

Set

\[
C(m,k,\varepsilon)=\cos(m\varepsilon)\cos(k\varepsilon).
\]

The formalization first proves

\[
|C(m,k,\varepsilon)|\le1,
\]

so the real arccosine is being used on its actual inverse-trigonometric domain. Define

\[
\phi=\arccos C\in[0,\pi].
\]

For an explicit proof `ε ≠ 0`, define the principal frequency

\[
\omega_\varepsilon(k)=\frac{\phi}{\varepsilon}.
\]

Lean proves

\[
\boxed{\cos(\omega_\varepsilon\varepsilon)=C(m,k,\varepsilon),}
\]

which is (8.6), together with the literal formula (8.7). For positive spacing it proves

\[
0\le\omega_\varepsilon\le\frac\pi\varepsilon.
\]

The branch is not left implicit. If another real `ω` satisfies

\[
0\le \omega\varepsilon\le\pi,
\qquad
\cos(\omega\varepsilon)=C,
\]

then Lean proves `ω = principalFrequency ...`.

At `ε=0`, the phase is still proved to be zero, but no principal frequency is constructed because division by the spacing would be invalid. Lean's totalized division is not used to hide that singular case.

## 6. Characteristic polynomial

A support theorem proves for every complex 2 by 2 matrix `A`

\[
\det(zI-A)=z^2-z\operatorname{Tr}A+\det A.
\]

Applying the exact trace and determinant laws gives

\[
\boxed{\det(zI-U)=z^2-2Cz+1.}
\]

Every candidate eigenvalue satisfying the determinant-zero equation therefore obeys the corresponding quadratic shell equation. This is an exact algebraic consequence and does not require diagonalizing the update.

## 7. Exact nontrivial witness

Take

\[
m=k=1,\qquad \varepsilon=\frac\pi2.
\]

Lean proves

\[
C=0,\qquad
\phi=\frac\pi2,\qquad
\omega=1,
\]

and

\[
\boxed{U=\alpha\beta=\begin{pmatrix}0&1\\-1&0\end{pmatrix}.}
\]

Hence the update is not the identity, while

\[
\operatorname{Tr}U=0,\qquad \det U=1,
\qquad \det(zI-U)=z^2+1.
\]

The same witness proves that the mass and shift factors do not commute and that reversing their order changes the update. Thus the ordered product in (8.2) is not notation that can be freely permuted.

## 8. Explicit boundaries

This block does **not** formalize the expansions (8.11)–(8.17), differentiate the arccos dispersion, or assert continuum Lorentz invariance. It establishes the exact finite-spacing one-dimensional unitary model first. The three-dimensional Clifford sector, observer-shell defect, gauge sector, gravity, cosmology and empirical claims remain separate obligations.

The next target is the asymptotic part of Section 8.1. It should prove the source's cosine expansion and then derive the `O(ε²)` frequency correction from an explicit nonzero-energy hypothesis, rather than dividing by `E = sqrt(m²+k²)` at the degenerate point `m=k=0`.
