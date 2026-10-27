# Block 08 — Parseval channels, universal finite dilation and current gauge

Komorebi Physics Lean v0.8.0. Literal source: *Projector-Refinement Physics: Complete Unified Theory*, physical PDF pages 28–29, printed pages 15–16. Chapter 5.4, equations (5.22)–(5.31), and Chapter 5.5, equations (5.33)–(5.34). Both source page images were inspected. The source PDF is unchanged. The authoritative cumulative result is `verification/final/report.json`, not a declaration count or this narrative.

## 1. Inventory and scope

| New module | Theorems | Definitions | Structures | Role |
|---|---:|---:|---:|---|
| ParsevalChannels | 19 | 5 | 1 | Actual given channels, effects, state/operator reconstruction, analysis and synthesis |
| ChannelDilation | 24 | 5 | 0 | Actual finite Hilbert sum, sharp coordinates, compression, range projector and operator lift |
| SquareRootDilation | 12 | 3 | 0 | Universal bounded finite-effect factorization using positive square roots |
| DilationDynamics | 12 | 1 | 0 | Actual lifted derivatives/currents and exact compression/unsharpness defects |
| CycleGauge | 10 | 2 | 0 | Divergence-free current ambiguity, coarsening and exact nonzero cycle |
| DilationExamples | 21 | 5 | 0 | Exact proper-isometry, omitted-channel and nonzero dynamic witnesses |
| **Block 08** | **98** | **21** | **1** | **120 new inventoried declarations** |

The cumulative inventory contains 670 theorem declarations, 808 named declarations and 40 mathematical modules. Of the theorems, 39 are preserved Paper VII declarations and 631 were authored in the eight full-edition blocks. All 34 Block 07 mathematical files are unchanged. These counts include support lemmas and exact examples. They are not counts of independent discoveries, empirical laws, or a completion percentage for 550 pages.

The main Hilbert spaces are complete complex inner-product spaces of arbitrary dimension. Every operator in this block is bounded and everywhere defined. The outcome set is finite. The general channel family allows a **dependent family of different output Hilbert spaces** K_i. The enlarged space is `PiLp 2 K`, with its actual Hilbert inner product, not the sup-norm product falsely assumed to satisfy Parseval.

The universal construction is finite-outcome, not finite-dimensional. No separability assumption on the state Hilbert space is imposed. Countable outcomes, unbounded maps, minimality/uniqueness of the dilation, and measurement-update instruments are not established here.

## 2. Given channels: what is assumed and what is derived

`ParsevalFamily H I K` has only channel maps V_i:H→L[ℂ]K_i and the resolution

\[
\sum_i V_i^\dagger V_i=I.
\]

The resolution is an explicit assumption for this **given-family interface**. No effect compression, probability, reconstruction or isometry result is a structure field.

`effectAtlas` constructs F_i=V_i†V_i and proves positivity, the Hermitian pairing identity, and completeness. The probability theorem derives

\[
p_i=\langle\psi,F_i\psi\rangle=\|V_i\psi\|^2.
\]

The earlier reality theorem for positive effects gives the literal complex expectation. The channel-norm identity does not replace the Born expectation by ||F_i ψ||². Individual channel norms are bounded by the state norm, and the sum of their squared norms equals the state norm squared.

The actual state and inner-product reconstructions are

\[
\sum_i V_i^\dagger V_i\psi=\psi,
\qquad
\sum_i\langle V_i x,V_i y\rangle=\langle x,y\rangle.
\]

For **every bounded operator X**, define the actual cross-channel block

\[
X_{ij}=V_iXV_j^\dagger:K_j\longrightarrow K_i.
\]

`reconstruct_operator` proves the full source identity

\[
\boxed{X=\sum_{i,j}V_i^\dagger X_{ij}V_j.}
\]

The source/target spaces and adjoint order are retained. Dropping the off-diagonal terms is not permitted. The exact example below demonstrates the error even for X=I on a one-dimensional state space.

## 3. Analysis, synthesis and actual coordinate projectors

The maps are separately constructed:

\[
V\psi=(V_i\psi)_i\in\bigoplus_iK_i,
\qquad
S(y)=\sum_iV_i^\dagger y_i.
\]

The Hilbert pairing proves S=V†. Only then does the formalization obtain

\[
SV=V^\dagger V=I,
\qquad
\|V\psi\|=\|\psi\|,
\]

and attach a `LinearIsometry` to the actual analysis map. Injectivity is a conclusion, not an input.

`ChannelDilation.inclusion` and `coordinate` are genuine bounded maps. The latter inserts only the selected coordinate and zeros all others. Their idempotence, pairwise orthogonality, Hermitian identities and identity sum are proved to construct a sharp `coordinateAtlas` on the enlarged Hilbert space. The resulting compression theorem is

\[
\boxed{F_i=V^\dagger\Pi_iV.}
\]

The sharp probability ||Π_i Vψ||² is proved equal to the original effect probability. None of these equations is postulated as the definition of an unspecified dilation.

### The two identity equations are not interchangeable

Define

\[
Q=VV^\dagger.
\]

The proofs establish Q†=Q and Q²=Q, and characterize Qy=y exactly by existence of ψ with Vψ=y. Thus Q is the projection onto the actual analysis image. The residual y−Qy has zero synthesis and is orthogonal to every analyzed state.

It is **not** generally true that Q=I on the larger space. A proper isometry example below rejects that claim exactly.

For the supported operator lift L(X)=VXV†, the proofs establish

\[
V^\dagger L(X)V=X,\quad
L(XY)=L(X)L(Y),\quad
L(X^\dagger)=L(X)^\dagger,\quad
\boxed{L(I)=Q.}
\]

The lift is injective and is multiplicative into the supported operator corner. It is not claimed unital into the entire ambient operator algebra. Its actual coordinate blocks are exactly the original V_iXV_j†.

## 4. Universal factorization: a previous gap is now closed

The given-Parseval-family theorem alone would leave an existence gap for arbitrary effects. `SquareRootDilation` closes that finite bounded gap.

Start with **only an existing `EffectAtlas`**: each F_i is bounded, positive and Hermitian, and sum_i F_i=I. Its quadratic-form positivity is proved equivalent to the nonnegative operator-order condition required by Mathlib's continuous functional calculus. Then define

\[
V_i=\sqrt{F_i}
\]

using `CFC.sqrt`, not an assumed factor or an existential oracle for the desired dilation. The library proves the square-root factorization within the imported Mathlib development; the new local module applies it to the actual effects and proves

\[
V_i^\dagger=V_i,\quad V_i^2=F_i,\quad
\sum_iV_i^\dagger V_i=I.
\]

This constructs `sqrtFamily`. The general direct-sum construction now provides an explicit map into finitely many Hilbert copies of H:

\[
V\psi=(\sqrt{F_i}\psi)_i,
\qquad
\boxed{V^\dagger V=I,\quad F_i=V^\dagger\Pi_iV.}
\]

`exists_finite_dilation` has no Parseval family or compression identity among its input assumptions. `dilation_compression` proves the statement for the specifically defined map, not just an unspecified existential witness. Every proof-bearing construction is included in the axiom audit.

This is a new formalization in this project, **not a claim that positive square roots or the dilation principle were first discovered here**. Mathlib's functional-calculus proofs and imported cache are reused, not reauthored or rebuilt wholesale.

## 5. Why positive effects are not necessarily sharp

For arbitrary bounded ambient operators, let C(X)=V†XV. Then

\[
\boxed{C(XY)-C(X)C(Y)=V^\dagger X(I-Q)YV.}
\]

The identity is proved by actual operator multiplication. It prevents silently treating compression as a multiplicative map on all ambient operators.

Substituting the sharp coordinate projector Π_i gives

\[
F_i-F_i^2=V^\dagger\Pi_i(I-Q)\Pi_iV.
\]

Taking the actual quadratic expectation and proving the residual orthogonality yields the stronger norm identity

\[
\boxed{
\langle\psi,(F_i-F_i^2)\psi\rangle
=\|(I-Q)\Pi_iV\psi\|^2\ge0.
}
\]

The real expectation is used in Lean with reality inherited from self-adjointness. The right side measures the part of a projected dilation vector outside the analysis image. This explains, with an exact checked identity, how sharp coordinate projectors yield non-idempotent compressed effects.

## 6. Actual dynamics and currents survive the dilation

For a supplied bounded skew generator A, define the enlarged generator A_tilde=VAV†. It is proved skew. Given the original derivative

```lean
HasDerivAt psi (A (psi t)) t
```

`lifted_flow` derives the actual derivative of Vψ and identifies it with A_tilde(Vψ). No enlarged trajectory equation is assumed.

The current theorem identifies the full sharp current on the enlarged space with the original positive-effect current:

\[
J^{\Pi}_{ij}(\widetilde A,V\psi)=J^F_{ij}(A,\psi).
\]

The formalization also proves actual derivatives of channel-norm and enlarged sharp probabilities. This is for a **fixed** Parseval family; differentiating a time-dependent analysis map would require its extra derivative term. These theorems transport a supplied trajectory, not construct a solution of an ODE.

## 7. Current ambiguity: literal Chapter 5.5

For a real finite current array K, `IsCycle K` explicitly requires antisymmetry and zero row sums. The proof establishes

\[
(J+K)\mathbf1=J\mathbf1
\]

and preserves antisymmetry when J is antisymmetric. Conversely, for two antisymmetric arrays, equal row sums are equivalent to their difference being a cycle. Every finite subsystem has zero net boundary flux from such a cycle. Cycles remain cycles under genuine address-map coarsening. The original actual probability derivative is also compatible with adding one.

The exact nonzero example is

\[
K=\begin{pmatrix}0&1&-1\\-1&0&1\\1&-1&0\end{pmatrix}.
\]

Lean proves both K≠0 and zero divergence. Continuity therefore does not uniquely determine every pairwise current. This does **not** assert that every gauge-modified array is produced by the same fixed microscopic generator. The original bilinear formula remains a selected generator-induced representative.

## 8. Exact tests

On H=ℂ with two scalar output channels, set V_0=(3/5)I and V_1=(4/5)I. The actual maps and their adjoints are constructed, and their Parseval resolution is proved. On ψ=1, the probabilities are 9/25 and 16/25.

The enlarged nonzero vector y=(4/5,−3/5) satisfies V†y=0 and Qy=0. Lean proves Q≠I and that analysis is not surjective. Thus L(I) is not the ambient identity.

The full reconstruction of I is exactly I, while keeping only diagonal channel blocks gives

\[
\left(\sum_i V_i^\dagger(V_iIV_i^\dagger)V_i\right)1
=\frac{337}{625}\ne1.
\]

The compressed first coordinate effect is not idempotent. The multiplicativity of arbitrary compression is separately refuted. The norm-square unsharpness identity has the exact nonzero value

\[
\langle1,(F_0-F_0^2)1\rangle
=\|(I-Q)\Pi_0V1\|^2
=\frac{144}{625}.
\]

The actual universal square-root dilation of Block 07's positive two-dimensional soft atlas also has probability 43/100, current −12/25 and an actual local probability derivative −12/25 at t=0. The reused affine vector curve is a **local derivative witness**, not a global normalized solution.

Nine new deliberately invalid controls reject ambient identity, forced sharpness, multiplicative compression, omitted cross channels, missing Parseval normalization, amplitude confused with probability, current uniqueness, the wrong nonzero current sign, and automatic surjectivity. Each requires its own intended diagnostic. Exact checked opposite facts appear in the active modules.

## 9. Audit and boundaries

The starting 572-theorem Block 07 package was freshly audited before extension. The final verifier removes local compiled outputs and recompiles 40 mathematical modules plus aggregate, inventories all 808 named declarations including constructors, requires all 59 controls to fail for their intended diagnostics, and checks all 34 old mathematical files against `reference/block07_preservation.json`. All older preservation checks remain active. The final report must be completed PASS before release packaging; an external fresh-extraction report independently records the second full run.

Lean 4.34.0-rc2; Mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06; nine clean pinned dependency repositories; one worker; warnings as errors. The imported Lean/Mathlib cache is reused, not independently rebuilt wholesale. Allowed audited axioms are only propext, Classical.choice and Quot.sound. There are no admitted active proofs, custom axioms, native evaluation or disabled kernel checks.

Chapter 5.6's historical floating residuals (5.35)–(5.43) are not rerun or relabeled as exact new theorems. Countable outcomes, unbounded generators, minimal/unique dilations, instruments, time-dependent channel differentiation, dynamical existence/positivity semigroups, entropy-boundary extensions, continuum gravity/cosmology and empirical adequacy remain separate.

**Next literal target:** Chapter 6.1 and 6.4, graph-compatible countable atlases and packet continuity. The domain of the unbounded generator, preservation of that domain by projectors, and convergence of both state sums and generator images must be represented explicitly. Strong Hilbert convergence alone cannot replace graph convergence. Section 6.3 additionally distinguishes strong convergence from operator-norm convergence; do not equate them.
