# Block 16 — Finite derivation no-go and corner-algebra resolution

Komorebi Physics Lean v0.16.0. Source: *Projector-Refinement Physics: Complete Unified Theory*, physical PDF pages 36–38 (printed 23–25), Chapter 7, equations (7.1)–(7.37). The numerical residual table (7.38)–(7.44) is historical and is not used as proof evidence. The authoritative cumulative result is `verification/final/report.json`.

## 1. Scope and inventory

| New module | Theorems | Other inventoried declarations | Role |
|---|---:|---:|---|
| `PointwiseNoGo` | 14 | 3 | Primitive-idempotent proof that complex-linear derivations of finite pointwise complex algebras vanish |
| `CornerDerivation` | 19 | 1 | Actual matrix commutator derivation, Leibniz, star compatibility, trace integration by parts |
| `CornerCurvature` | 18 | 2 | Jacobi/curvature identity and commuting/noncommuting generator consequences |
| `CornerReconstruction` | 14 | 3 | Exact projector-corner reconstruction, intermediate path expansion and coarse refinement |
| `CornerExamples` | 25 | 6 | Exact 2x2 nonzero derivation/curvature/corner witnesses and the pointwise contrast |
| **Block 16** | **90** | **15** | **105 new inventoried declarations** |

The cumulative inventory is **1,461 theorem declarations, 1,731 inventoried declarations and 91 mathematical modules**. Of the theorems, 39 are recovered Paper VII declarations and 1,422 were authored across the full-edition blocks. All 86 mathematical modules from Block 15 are byte-identical. These counts include support lemmas and exact examples; they are not independent physical discoveries or a percentage of the 550-page edition.

## 2. Finite pointwise algebra: actual no-go theorem

For a finite label type `ι`, define

\[
A_ι = ι\to\mathbb C
\]

with the ordinary pointwise product. The formalization defines the primitive coordinate idempotent `atom a`, proves its coordinate multiplication laws and the finite decomposition of unity, and defines a derivation as an actual complex-linear map `D` satisfying the exact Leibniz rule.

For every primitive idempotent `e_a`, Leibniz gives

\[
D(e_a)=D(e_a^2)=D(e_a)e_a+e_aD(e_a).
\]

The theorem `atom_derivative_coordinate` evaluates this equality at an arbitrary coordinate. Off the atom coordinate the right side is zero; at the atom coordinate it is twice the same scalar. Therefore every coordinate of `D(e_a)` is zero. The proof then decomposes an arbitrary function into its coordinate atoms and concludes

\[
\boxed{D=0.}
\]

`finite_source_no_go` is the literal finite-label specialization. `zero_isDerivation` proves the zero map really satisfies the derivation interface, so the statement is not vacuous.

**Scope boundary:** the theorem is for a finite product of copies of `ℂ` with the ordinary pointwise multiplication and complex linearity. It is not generalized to every finite-dimensional commutative algebra. In particular, algebras with nilpotents are outside this statement. The proof is stronger than the source's finite `N=2,...,8` rank checks, so those numerical rank calculations are not needed as proof premises.

## 3. Full matrix algebra: exact nonzero derivation

For finite complex matrices define

\[
\delta_K(X)=i(KX-XK).
\]

The implementation is the actual matrix expression, not a structure containing desired algebraic laws. Direct ring expansion proves

\[
\boxed{\delta_K(XY)=\delta_K(X)Y+X\delta_K(Y).}
\]

Linearity, action on the identity, and the equivalence `delta K X = 0 ↔ KX = XK` are also checked.

If `K` is Hermitian, the formalization derives

\[
\boxed{(\delta_KX)^*=\delta_K(X^*)}.
\]

Hence Hermitian inputs remain Hermitian. Trace cyclicity gives `trace_delta`, and combining it with Leibniz gives the exact finite integration-by-parts identity

\[
\boxed{\operatorname{Tr}((\delta_KX)Y)=-\operatorname{Tr}(X\delta_KY).}
\]

This checks the algebraic content of (7.12)–(7.23). No floating-point residual is used.

## 4. Curvature of finite derivations

Define

\[
F_{KL}=i[K,L].
\]

The Jacobi identity is proved by direct noncommutative-ring normalization. It yields

\[
\boxed{[\delta_K,\delta_L]X=\delta_{F_{KL}}X.}
\]

Equivalently,

\[
\delta_K(\delta_LX)-\delta_L(\delta_KX)=i[F_{KL},X].
\]

When the generators commute, the induced derivations commute. When `K` and `L` are Hermitian, `F_{KL}` is Hermitian. The formalization also records a useful distinction: a nonzero curvature matrix that is central acts trivially by the inner derivation. Thus “matrix curvature nonzero” and “curvature action nonzero” are not collapsed into the same assertion.

## 5. Projector-corner reconstruction and two-step paths

For a finite complete orthogonal packet family `P`, define

\[
X_{ab}=P_aXP_b.
\]

The existing packet-family completeness is used to prove the actual reconstruction

\[
\boxed{X=\sum_{a,b}P_aXP_b.}
\]

Applying this to `δ_K X` gives (7.32). Inserting the resolution of the identity between `K` and `X` in the two commutator terms proves

\[
\boxed{
P_a(\delta_KX)P_b
=i\sum_c\bigl(P_aKP_cXP_b-P_aXP_cKP_b\bigr).
}
\]

The proof also rewrites each summand as products of actual matrix corners. It does not introduce an abstract “path amplitude” with the desired result as an axiom.

For an address map into a coarse label type, the actual coarse projectors are finite sums of the fine projectors. Their completeness and multiplication laws are proved, and

\[
\boxed{
Q_A(\delta_KX)Q_B
=\sum_{a:f(a)=A}\sum_{b:f(b)=B}P_a(\delta_KX)P_b.
}
\]

This checks (7.31)–(7.37) and ties the Chapter 7 corner algebra back to the earlier exact refinement machinery.

## 6. Exact nonzero witness

On two coordinates use

\[
K=\begin{pmatrix}0&0\\0&1\end{pmatrix},\qquad
L=\begin{pmatrix}0&1\\1&0\end{pmatrix},\qquad
Z=\begin{pmatrix}1&0\\0&-1\end{pmatrix}.
\]

All three are proved Hermitian. The exact derivation value is

\[
\boxed{
\delta_KL=\begin{pmatrix}0&-i\\i&0\end{pmatrix}\ne0.
}
\]

Thus the matrix algebra supports a genuine nonzero derivation, while the two-coordinate pointwise algebra satisfies the proved no-go theorem.

For the same pair,

\[
F_{KL}=\begin{pmatrix}0&-i\\i&0\end{pmatrix}\ne0
\]

and its action on `Z` is

\[
\boxed{
\delta_{F_{KL}}Z=\begin{pmatrix}0&-2\\-2&0\end{pmatrix}\ne0.
}
\]

The actual coordinate packet family has the exact off-diagonal differentiated corners `-i E_01` and `i E_10`, zero diagonal corners, and reconstructs the full nonzero derivative. A separate nonzero trace calculation proves the sign in integration by parts is observable rather than vacuous:

\[
\operatorname{Tr}((\delta_KL)^2)=2,
\qquad
\operatorname{Tr}(L\,\delta_K(\delta_KL))=-2.
\]

## 7. Verification and boundaries

The production verifier recompiles all 91 mathematical modules and the aggregate with one worker and warnings as errors. It audits all 1,731 inventoried declarations and requires every deliberately invalid control to produce its designated proof diagnostic in its mapped source range. The 86 Block 15 mathematical modules are checked against `reference/block15_preservation.json`. Only `propext`, `Classical.choice` and `Quot.sound` are permitted axiom dependencies. There are no admitted active proofs or custom axioms.

Seven new controls reject a nonzero pointwise derivation, the false extension of the no-go to the matrix witness, vanishing curvature, the wrong curvature-action sign, disappearance of a nonzero off-diagonal corner, the wrong corner phase, and the wrong trace integration-by-parts sign.

This block proves finite algebraic identities. It does not turn the matrix inner derivation into a continuum spatial derivative, prove a continuum limit, identify a specific physical Hamiltonian, or establish empirical adequacy. Chapter 6's still-open half-power/differential-oscillator and broader interacting-domain obligations remain separate. The historical numerical residuals (7.38)–(7.44) were not rerun because the exact identities they approximate are now kernel-checked in the stated finite setting.

**Next literal source:** Chapter 8, discrete relativistic sectors. The first target is (8.1)–(8.10): Pauli involutions/anticommutation, the exact local update, unitarity, determinant one and the trace/dispersion identity. The asymptotic frequency and group-velocity expansions (8.11) onward should be formalized only after the exact finite-spacing identities are stable.
