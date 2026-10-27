# Block 22 — Moving-momentum Lorentz defect

Komorebi Physics Lean v0.22.0. This block formalizes the observer-shell calculation isolated at the end of Block 21, corresponding to equations (8.42)–(8.48) of *Projector-Refinement Physics: Complete Unified Theory*. The authoritative cumulative result is `verification/final/report.json` after its completed PASS run.

## 1. Scope and declaration counts

| Module | Theorems | Other declarations | Role |
|---|---:|---:|---|
| `Relativistic3DLorentzKinematics` | 52 | 16 | Three-vector algebra, regularized Lorentz boost, exact mass-shell and inverse identities |
| `Relativistic3DDiscreteBoost` | 12 | 5 | Boost of the exact lattice four-momentum, moving spatial displacement, continuum-energy response |
| `Relativistic3DPathInversion` | 28 | 14 | Branch-controlled generic shell-to-frequency inversion along one-sided paths |
| `Relativistic3DMovingShell` | 14 | 3 | Uniform shell expansion under an `a Δ² + O(Δ⁴)` momentum displacement |
| `Relativistic3DMovingFrequency` | 5 | 1 | Moving-argument transfer for the exact principal lattice frequency |
| `Relativistic3DObserverDefect` | 7 | 4 | Coefficient cancellation and the closed observer-defect theorem |
| `Relativistic3DObserverExamples` | 11 | 2 | Exact stationary and nonzero rational witnesses |
| **Block 22** | **129** | **45** | **174 new inventoried declarations** |

The cumulative inventory contains **2,056 theorem declarations, 2,463 inventoried declarations, and 121 mathematical modules**. The 114 Block 21 mathematical modules are protected by `reference/block21_preservation.json`. These are declaration counts, not counts of independent discoveries and not a completion percentage for the full manuscript.

## 2. Exact regularized Lorentz boost

For a real three-vector `v` with

\[
|v|^2<1,
\qquad
\gamma=(1-|v|^2)^{-1/2},
\]

the spatial boost is written using

\[
\alpha(v)=\frac{\gamma^2}{\gamma+1}.
\]

This form is defined at `v=0`, unlike the source-coordinate expression `(γ-1)/|v|²`. Lean proves their equality whenever `|v|² ≠ 0`. With

\[
E'=\gamma(E-v\cdot k),
\qquad
k'=k+\bigl(\alpha(v)(v\cdot k)-\gamma E\bigr)v,
\]

Block 22 proves exactly

\[
E'^2-|k'|^2=E^2-|k|^2
\]

and the cancellation identity

\[
\boxed{E'+v\cdot k'=\frac{E}{\gamma}.}
\]

For a nonzero positive mass-shell energy and a subluminal velocity, `E'` is proved strictly positive and equals the positive continuum energy of `k'`.

## 3. The transformed lattice momentum really moves

Let the exact lattice frequency from Block 21 be

\[
\omega_\Delta(k)
=E(k)+c(k)\Delta^2+O(\Delta^4),
\qquad
c(k)=-\frac{Q(k)}{6E(k)}.
\]

Boosting the exact discrete four-momentum

\[
p_\Delta=(\omega_\Delta(k),k)
\]

gives a transformed spatial momentum `k'_Δ`. It is not the fixed continuum momentum `k'`. Lean proves the exact identity

\[
\boxed{
k'_\Delta-k'
=-\gamma\bigl(\omega_\Delta(k)-E(k)\bigr)v.
}
\]

Consequently,

\[
k'_\Delta
=k'-\gamma c(k)v\,\Delta^2+O(\Delta^4).
\]

The corresponding continuum-energy response is proved with a quartic remainder:

\[
E(k'_\Delta)
=E'
-\gamma c(k)\frac{v\cdot k'}{E'}\Delta^2
+O(\Delta^4).
\]

This is the term that a frozen-momentum substitution would miss.

## 4. Generic path inversion

A reusable theorem was needed because `arccos` is singular at shell value one. The generic path layer assumes a one-sided shell expansion

\[
S(\Delta)
=1-\frac{E^2}{2}\Delta^2+B\Delta^4+O(\Delta^6),
\qquad E>0,
\]

then proves, through normalized sine-square, positive square-root, and `arcsin` branch control,

\[
\frac{\arccos S(\Delta)}{\Delta}
=E+\left(\frac{E^3}{24}-\frac{B}{E}\right)\Delta^2
+O(\Delta^4).
\]

No Taylor expansion of `arccos` at one is assumed.

## 5. Moving-shell theorem

Let

\[
t_\Delta=a\Delta^2+O(\Delta^4),
\qquad
q_\Delta=q+t_\Delta v.
\]

The exact four-cosine shell at `q_Δ` is expanded through sixth order. Lean proves that the moving spatial factor changes the quartic shell coefficient by exactly

\[
-a\,v\cdot q.
\]

The complete moving shell therefore satisfies the hypotheses of the generic path inversion theorem, with a genuine `O(Δ⁶)` remainder. The associated exact principal frequency obeys

\[
\boxed{
\omega_\Delta(q_\Delta)
=E(q_\Delta)+c(q)\Delta^2+O(\Delta^4).
}
\]

The lattice correction is evaluated at the limiting momentum `q`, while the continuum energy is evaluated at the actual moving momentum. This is the precise transfer statement required by the observer calculation.

## 6. Closed observer-shell defect

Define

\[
\mathfrak L_\Delta(k,v)
=
\gamma\bigl(\omega_\Delta(k)-v\cdot k\bigr)
-
\omega_\Delta(k'_\Delta).
\]

Combining the boosted-energy expansion, moving continuum-energy response, and moving-frequency theorem first gives the operational coefficient

\[
\gamma c(k)
-
\left[
-\gamma c(k)\frac{v\cdot k'}{E'}+c(k')
\right].
\]

Using

\[
E'+v\cdot k'=E/\gamma,
\qquad
c(k)=-\frac{Q(k)}{6E},
\qquad
c(k')=-\frac{Q(k')}{6E'},
\]

Lean proves the exact cancellation

\[
\gamma c(k)
-
\left[
-\gamma c(k)\frac{v\cdot k'}{E'}+c(k')
\right]
=
\frac{Q(k')-Q(k)}{6E'}.
\]

Hence the main theorem is

\[
\boxed{
\mathfrak L_\Delta(k,v)
=
\frac{Q(k')-Q(k)}{6E'}\Delta^2
+O(\Delta^4).
}
\]

The assumptions remain explicit: `|v|² < 1`, nonzero source continuum energy, and the positive-spacing filter `Δ → 0+`.

## 7. Exact witnesses

At zero observer velocity, Lean proves the stronger exact identity

\[
\mathfrak L_\Delta(k,0)=0
\]

for every spacing, not merely vanishing of the leading coefficient.

For the rational witness

\[
m=3,
\qquad
k=(4,0,0),
\qquad
v=(3/5,0,0),
\]

Lean proves

\[
E=5,
\quad
\gamma=\frac54,
\quad
E'=\frac{13}{4},
\quad
k'=\left(\frac54,0,0\right),
\]

\[
Q(k)=144,
\qquad
Q(k')=\frac{225}{16},
\]

and therefore

\[
\boxed{
\mathfrak L_\Delta
=-\frac{693}{104}\Delta^2+O(\Delta^4).
}
\]

This gives a formal nonzero finite-spacing Lorentz-defect witness.

## 8. Exact boundary

Block 22 proves a quantified leading violation of continuum Lorentz covariance for this specific exact lattice shell. It does **not** prove exact finite-spacing Lorentz invariance. It also does not yet provide a position-space locality theorem, a gauge-link or plaquette-holonomy construction, an interacting gauge-field continuum limit, or empirical adequacy of the model.

The next physical frontier should be selected only after reconciling the source immediately following equation (8.48). The natural candidates are the exact position-space realization of the walk and the gauge-link/holonomy layer.
