# The ambient splitting obstruction

**Author:** Komorebi P.

## Result

Let (H) be a finite-dimensional real vector space with positive-definite
metric (G). Let (N\subseteq H) be a fixed observation kernel, and suppose
every recurrent operator (M_a) satisfies

\[
M_a^{\mathsf T}GM_a=G,
\qquad
M_aN\subseteq N.
\]

Then the (G)-orthogonal complement (N^{\perp_G}) is invariant under every
(M_a). Consequently, in the decomposition

\[
H=N^{\perp_G}\oplus N,
\]

each operator is block diagonal. A one-way semantic-to-fiber memory term is
impossible under these assumptions.

## Proof

Each (G)-isometry is invertible. Because (M_aN\subseteq N) and dimensions
are preserved, (M_aN=N). Take (x\in N^{\perp_G}) and (n\in N). There is
an (m\in N) with (n=M_am). Isometry gives

\[
\langle M_ax,n\rangle_G
=\langle M_ax,M_am\rangle_G
=\langle x,m\rangle_G
=0.
\]

Thus (M_ax\in N^{\perp_G}). Both summands are invariant, so no off-diagonal
write or return block survives. The argument is generatorwise and does not
require group relations.

## Finite-group strengthening

For a real representation \(\rho\) of a finite group \(\Gamma\), every invariant
subspace has an invariant complement even when no metric is initially given.
Choose any projection (p:H\to N) and average it:

\[
P=\frac1{|\Gamma|}\sum_{g\in\Gamma}
\rho(g)p\rho(g)^{-1}.
\]

Then (P) is equivariant, (P|_N=I), and \(\ker P\) is an invariant
complement. This is the relevant form of Maschke's theorem. Equivalently, one
may average an arbitrary positive-definite metric over the group.

Therefore, an exact real (D_4) representation cannot contain an intrinsic
non-split linear memory extension. A triangular cocycle can be removed by a
change of splitting; an affine finite-group cocycle likewise has an averaged
fixed point and can be translated away.

## Interpretation of v0.6

The v0.6 hard construction can have a curved ambient (K) while its semantic
quotient is exact because the full (K)-action is not required to factor
through (D_4). Equivalent semantic paths may differ on (K). This is valid
ambient path holonomy, but the fixed block isolation makes it dormant rather
than useful memory.

The posthoc exact-depth diagnostic confirms the distinction empirically. Both
the exact quotient control and the same quotient with deliberately curved
ambient dynamics retained 1.0000 robust accuracy through depth 16,384. Curved
fiber dynamics do not destabilize semantics when the quotient connection is
exact.

## What must change for useful ambient memory

Keep the exact semantic quotient, but relax at least one no-go assumption:

1. **Typed path monoid or category:** add irreversible `WRITE`, `HOLD`, and
   `QUERY` arrows rather than requiring the full dynamics to be a (D_4)
   representation.
2. **Contractive skew product:**
   \[
   s_{t+1}=\rho(a_t)s_t,
   \qquad
   k_{t+1}=\lambda R_{a_t}k_t+c(a_t,s_t),
   \quad 0\leq\lambda<1.
   \]
3. **Typed release:** keep (k) invisible to the ordinary semantic head, but
   expose it through a registered query head or query transition.
4. **Phase-dependent kernel:** allow the kernel during `HOLD` to differ from
   the kernel during `QUERY`; orthogonal write/read dynamics can then remain
   norm bounded without pretending that one fixed future-null space exists.
5. **Nonlinear bounded fiber:** use gated or saturating updates when persistent
   storage, selective overwrite, and provenance cannot be represented by a
   stable linear extension.

The decisive benchmark should give two histories the same (D_4) quotient
state but different payloads. Their ordinary outputs must agree throughout
`HOLD`, then diverge in the exactly predicted way at `QUERY`. Causal fiber
ablation and transplantation must change only the queried payload, while long
hold sequences remain bounded.

This establishes a clean division of labor:

\[
\boxed{\text{exact flat quotient for stable semantics}}
\qquad+
\qquad
\boxed{\text{typed non-group fiber dynamics for memory}}.
\]

