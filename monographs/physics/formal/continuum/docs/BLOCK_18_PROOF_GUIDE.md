# Block 18 — 1D shell asymptotics, exact group velocity, and the correction certificate

Komorebi Physics Lean v0.18.0. Source: *Projector-Refinement Physics: Complete Unified Theory*, physical PDF pages 40–41 of 550, printed pages 27–28. The literal source targets are equations (8.11)–(8.17), but this release deliberately separates what has actually been proved from the remaining inverse-dispersion asymptotic step. The authoritative cumulative machine result is `verification/final/report.json`.

## 1. Scope and declaration counts

| Module | Theorems | Other declarations | Role |
|---|---:|---:|---|
| `Relativistic1DShellAsymptotics` | 24 | 4 | Actual sixth-order Taylor control for the exact product-cosine shell |
| `Relativistic1DGroupVelocity` | 9 | 0 | Actual momentum derivative and exact principal-branch velocity formula |
| `Relativistic1DAsymptoticAlgebra` | 18 | 2 | Continuum energy, unique second-order correction coefficient, and squared-shell algebra |
| `Relativistic1DAsymptoticExamples` | 16 | 0 | Exact nonzero and degenerate witnesses |
| `Relativistic1DSpacingParity` | 8 | 1 | Exact even/odd spacing behavior and the positive-spacing boundary |
| **Block 18** | **75** | **7** | **82 new inventoried declarations** |

The cumulative inventory has **1,637 theorem declarations, 1,926 inventoried declarations and 101 mathematical modules**. The 96 prior mathematical modules are protected by `reference/block17_preservation.json`. Counts include support results and exact examples; they are not independent physical discoveries or a completion percentage for the full manuscript.

## 2. Equation (8.15): genuine Taylor remainder for the exact shell

The exact shell remains

\[
C(\varepsilon)=\cos(m\varepsilon)\cos(k\varepsilon).
\]

The formalization proves `ContDiff` regularity and explicitly computes the derivatives through order six at zero. In particular,

\[
C''(0)=-(m^2+k^2),
\]

\[
C^{(4)}(0)=m^4+6m^2k^2+k^4,
\]

and

\[
C^{(6)}(0)=-(m^6+15m^4k^2+15m^2k^4+k^6).
\]

Using Mathlib's actual Taylor theorem, not a formal power-series convention, Lean proves

\[
C(\varepsilon)
=1-\frac{m^2+k^2}{2}\varepsilon^2
+\left(\frac{m^4+k^4}{24}+\frac{m^2k^2}{4}\right)\varepsilon^4
+O(\varepsilon^6).
\]

With

\[
E=\sqrt{m^2+k^2},
\]

the quartic coefficient is separately proved equal to

\[
\frac{E^4}{24}+\frac{m^2k^2}{6}.
\]

Thus the source form

\[
\boxed{C(\varepsilon)=1-\frac{E^2\varepsilon^2}{2}
+\left(\frac{E^4}{24}+\frac{m^2k^2}{6}\right)\varepsilon^4
+O(\varepsilon^6)}
\]

is a genuine `Asymptotics.IsBigO` theorem at zero. This closes (8.15) itself.

## 3. The nondegenerate continuum energy is explicit

Lean proves

\[
E^2=m^2+k^2,
\qquad E\ge0,
\]

and the exact degeneracy criterion

\[
\boxed{E=0\iff m=0\ \text{and}\ k=0.}
\]

Every theorem that divides by `E` carries `E ≠ 0` explicitly. At the degenerate point, the totalized algebraic correction expression evaluates to zero, but no physical division by zero is inferred from that fact.

## 4. The source correction coefficient is forced by quartic matching

Define

\[
a(m,k)=-\frac{m^2k^2}{6E}
\]

under the nondegenerate interpretation. The polynomial frequency ansatz is

\[
\omega_{[2]}(\varepsilon)=E+a\varepsilon^2.
\]

The release proves that if a coefficient `a` matches the exact fourth-order cosine-shell coefficient, then it is unique and must equal

\[
\boxed{a=-\frac{m^2k^2}{6E}.}
\]

Conversely, the displayed correction is proved to satisfy that coefficient identity. The proof derives this by algebra from the already checked shell quartic coefficient; the sign and factor are not installed as a structure field.

The corresponding exact polynomial squared-shell identity is

\[
\boxed{
\omega_{[2]}(\varepsilon)^2-k^2-m^2
=-\frac13m^2k^2\varepsilon^2+a^2\varepsilon^4.
}
\]

Thus the coefficient underlying (8.12) is checked exactly.

**Boundary:** this is a coefficient/candidate theorem. This block has **not yet proved** that the exact inverse-arccos frequency itself satisfies

\[
\omega_\varepsilon=E+a\varepsilon^2+O(\varepsilon^4).
\]

That remaining analytic inversion is not relabeled as complete equation (8.11).

## 5. Equation (8.13): actual momentum derivative of the exact branch

The shell derivative is first proved from the original product-cosine function:

\[
\frac{\partial C}{\partial k}
=-\varepsilon\cos(m\varepsilon)\sin(k\varepsilon).
\]

At points satisfying

\[
\varepsilon\ne0,\qquad |C|<1,
\]

the principal arccos branch is differentiable. Lean differentiates the actual `principalFrequency` from Block 17 and obtains

\[
\frac{\partial\omega_\varepsilon}{\partial k}
=
\frac{\cos(m\varepsilon)\sin(k\varepsilon)}
{\sqrt{1-C^2}}.
\]

It then proves on the principal branch

\[
\sqrt{1-C^2}=\sin(\omega_\varepsilon\varepsilon)>0,
\]

and hence

\[
\boxed{
\frac{\partial\omega_\varepsilon}{\partial k}
=
\frac{\cos(m\varepsilon)\sin(k\varepsilon)}
{\sin(\omega_\varepsilon\varepsilon)}.
}
\]

This is the actual derivative statement in (8.13). The denominator nonzero condition is proved from the strict shell-interior hypothesis; it is not ignored through totalized division.

The exact velocity is proved even in mass and odd in momentum. The continuum estimate `k/E + O(ε²)` in (8.14) is **not** yet claimed.

## 6. Spacing parity reveals the correct asymptotic side

The exact shell and principal phase are even in the spacing:

\[
C(-\varepsilon)=C(\varepsilon),\qquad
\phi(-\varepsilon)=\phi(\varepsilon).
\]

Because the principal frequency divides the nonnegative phase by the signed spacing, Lean proves for `ε ≠ 0`

\[
\boxed{\omega_{-\varepsilon}=-\omega_\varepsilon.}
\]

A total extension taking value zero at `ε=0` is also proved exactly odd. For negative spacing, the principal frequency is nonpositive.

This matters for the remaining asymptotic theorem: an expansion with leading term `+E` must be stated on the **physical positive-spacing filter**, not as an unqualified two-sided expansion around zero. The source uses lattice spacing as a positive physical scale; the formalization now makes that domain issue explicit.

## 7. Exact witnesses

At `m=k=1`, Lean proves

\[
E=\sqrt2,
\qquad
C(\varepsilon)=1-\varepsilon^2+\frac13\varepsilon^4+O(\varepsilon^6),
\]

and

\[
a=-\frac{1}{6\sqrt2}<0.
\]

The fourth and sixth shell derivatives are exactly

\[
C^{(4)}(0)=8,
\qquad
C^{(6)}(0)=-32,
\]

so the Taylor calculation is nonvacuous. The squared-shell coefficient becomes exactly `-1/3`.

At `m=k=0`, the energy and totalized correction are both exactly zero, providing the explicit degeneracy witness.

Five new negative controls reject a wrong fourth derivative, wrong sixth derivative, nonzero degenerate energy, the wrong correction sign, and the wrong squared-shell coefficient.

## 8. Verification and remaining boundary

The completed production report is authoritative. The verifier recompiles every mathematical module and the aggregate with warnings as errors, checks the exact declaration inventory, audits every named declaration for axiom dependencies, verifies all preservation layers through Block 17, and requires every negative control to fail with its designated diagnostic. Active proof sources contain no `sorry`, `admit`, custom axioms, native evaluation or disabled-kernel mechanisms.

This release **does not claim equations (8.11), (8.12), and (8.14) in their full exact-frequency asymptotic form**. It proves the source shell expansion, exact velocity identity, the unique correction coefficient forced by fourth-order matching, and the exact polynomial squared-shell consequence. The remaining analytic step is a one-sided inversion theorem for the principal arccos branch that upgrades these coefficient facts to

\[
\omega_\varepsilon
=E-\frac{m^2k^2}{6E}\varepsilon^2+O(\varepsilon^4)
\quad(\varepsilon\to0^+).
\]

That theorem should be the first target of Block 19. Only after it and the velocity `O(ε²)` consequence are closed should the formalization move into the three-dimensional Clifford walk.
