# Paper III, Section 17: packet jets and multilinear reconstruction

**Continuation version:** 0.3.0, 19 October 2026 (America/Chicago)  
**Mathematical status:** The results in this note have complete ordinary mathematical arguments.  
**Formal status:** Two Lean source modules are **candidates only, not compiled or kernel replayed** in this environment. They are stored in `formal/drafts/` and are not imported by the accepted production root. This note is not a certification of Section 17 in Lean.

## 1. Exact algebraic result with weakened assumptions

Let `R` be a semiring and `X, Y` be modules over `R`. Let `I, J` and `A` be finite index sets, with `A` indexing multilinear input slots. Take two finite families of linear maps

\[
P_i\in\operatorname{End}_R(X),\qquad Q_\gamma\in\operatorname{End}_R(Y),
\quad \sum_i P_i=1_X,\quad\sum_\gamma Q_\gamma=1_Y.
\]

Neither idempotence nor pairwise annihilation is needed for the following identity. For any multilinear map `B : X^A -> Y`, and any tuple `h=(h_a)`, the **finite resolution-of-identity expansion** is

\[
B(h_a:a\in A)=\sum_{\gamma\in J}\sum_{\alpha\in I^A}
 Q_\gamma B(P_{\alpha(a)}h_a:a\in A).\tag{17.R}
\]

**Proof.** In each input slot use the literal identity
`h_a = sum_{i in I} P_i h_a`. By additivity of `B` in that slot, expand its finite sum. Because every index set is finite, the resulting iterated sums can be regrouped as a single sum indexed by all functions `alpha : A -> I`; no limit interchange occurs. Next apply `sum_gamma Q_gamma = id` to the value of `B` and distribute each linear `Q_gamma` over the finite inner sum. This proves (17.R). The argument does not assume symmetry or alternating behavior of `B`; it also handles the empty slot set.

**Strength and limitation.** Completeness alone gives (17.R). It does **not** say that analysis `x |-> (P_i x)` is invertible, or that `(P_i x)_i` are independent coordinates. For those stronger properties one needs precisely the idempotence and pairwise annihilation conditions already checked in Section 16. The distinction prevents a false promotion of a mere decomposition identity to a coordinate equivalence.

## 2. True packet jets on actual range modules

For the complete, idempotent, pairwise annihilating systems used in the manuscript, let `X_i=range(P_i)` and `Y_gamma=range(Q_gamma)`. Define

\[
J_{\gamma\mid\alpha} B : \prod_{a\in A}X_{\alpha(a)}\longrightarrow Y_\gamma,
\qquad (z_a)\longmapsto Q_\gamma B(z_a).
\]

The formula really has codomain `Y_gamma`: `Q_gamma B(z)` is by construction in the range of `Q_gamma`. Multilinearity is inherited by composition with the range inclusions and `Q_gamma`. The projected inputs `P_{alpha(a)}h_a` are genuine members of `X_{alpha(a)}`. Hence (17.R) is exactly the manuscript's **derivative reconstruction** after choosing `B=D^rF(x)` and forgetting continuity for the algebraic calculation. The Lean candidate `MultilinearPacketJets.lean` constructs this range-to-range multilinear map explicitly by `MultilinearMap.compLinearMap`, `LinearMap.compMultilinearMap`, and `MultilinearMap.codRestrict`.

If `F:X->Y` is `C^m` on an appropriate open set of Banach spaces, its actual `r`th Fréchet derivative at `x` is a continuous symmetric `r`-multilinear map. Inserting it for `B` yields Theorem 17.2, with no new differentiability assumption beyond that needed to construct the derivative. The expansion in fact applies to any continuous multilinear map, symmetric or not.

## 3. Norm estimate and topology bridge

The earlier Section 16 module systems use `LinearMap`s, not necessarily bounded maps. For Section 17's analytic claims, explicitly demand that every `P_i` and `Q_gamma` be bounded linear operators on normed spaces. This is essential and cannot be inferred from the algebraic Section 16 hypotheses in infinite dimension.

Let `B:X^r -> Y` be continuous multilinear. Its *ambient extended jet* is

\[
\widetilde J_{\gamma\mid\alpha}B
=Q_\gamma\circ B\circ(P_{\alpha(1)},\ldots,P_{\alpha(r)}).
\]

Standard operator norm estimates for composition in every slot imply

\[
\|\widetilde J_{\gamma\mid\alpha}B\|
\le \|Q_\gamma\|\,\|B\|\prod_{a=1}^{r}\|P_{\alpha(a)}\|.\tag{17.N}
\]

**Proof.** By the definition of the continuous multilinear operator norm, for `v_a` one has
`||B(P_alpha(a) v_a)|| <= ||B|| product_a ||P_alpha(a) v_a||`.
Use `||P_alpha(a) v_a|| <= ||P_alpha(a)|| ||v_a||`, and then apply the output bound `||Q_gamma y|| <= ||Q_gamma|| ||y||`. The resulting pointwise estimate is (17.N) on taking the operator norm. This argument does not use Hilbert orthogonality.

The genuine range-restricted jet uses `z_a \in range(P_alpha(a))` with the subspace norm. Because `P_alpha(a) z_a=z_a`, the range jet agrees on those inputs with the ambient extension. Norms on these subspaces are inherited from `X`, so the operator norm of the restriction is at most that of the ambient extension. Its values lie in `range(Q_gamma)` with the inherited norm. Thus the identical right-hand bound holds for the range jet.

The Lean candidate `BoundedPacketJetNorm.lean` covers **only the ambient inequality** using mathlib's two norm-composition lemmas. The construction of continuous range maps and proof of the literal range norm bridge remain uncompiled/unformalized in this checkpoint. When all packet projectors are *orthogonal Hilbert projections*, the norm of each nonzero projection is one. If a zero projector occurs, the corresponding positive-order packet jet is zero.

## 4. Second-order composition and finite packet labels

For twice continuously differentiable `G:X->Y` and `F:Y->Z`, at `x` the usual second chain rule is

\[
D^2(F\circ G)(x)[h,k]
=D^2F(Gx)[DG(x)h,DG(x)k]
 +DF(Gx)[D^2G(x)[h,k]].\tag{17.C2}
\]

Fix input labels `alpha, beta`, output label `delta`, and projectors `P`, `Q`, `S` on the three spaces. Put `h_alpha=P_alpha h` and `k_beta=P_beta k`. In the first term of (17.C2), insert `sum_gamma Q_gamma=id_Y` **twice**, once for each argument of `D²F`. In the second, insert it **once** for the output of `D²G`. Project the final result with `S_delta`. The fully decorated two-term formula is

\[
\begin{aligned}
S_\delta D^2(F\circ G)(x)[h_\alpha,k_\beta]
={}&\sum_{\gamma,\eta}
  S_\delta D^2F(Gx)[Q_\gamma DG(x)h_\alpha,
                          Q_\eta DG(x)k_\beta]\\
 &+\sum_\gamma S_\delta DF(Gx)
        [Q_\gamma D^2G(x)[h_\alpha,k_\beta]].
\end{aligned}
\]

These two groups correspond to the two set partitions of `{1,2}`. Discarding the mixed or intermediate labels generally gives the wrong derivative, even if all packet families are exact.

For general order `n`, the classical higher chain rule is a sum over set partitions. A partition with `k` blocks has `M^k` intermediate labelings when `Y` has `M` packets. Consequently the number of decorated terms before pruning is exactly

\[
N_{n,M}=\sum_{k=1}^n S(n,k)M^k.
\]

This is a combinatorial counting fact, not evidence that the full higher chain rule has been formalized. Zero jet blocks imply zero individual decorated summands. Cancellations can make the actual support *smaller* than this predicted support, so support inclusion, not equality, is the correct general assertion.

## 5. Exact finite checks and negative controls

The independent Python script evaluates finite rational tensors and explicitly conjugated non-coordinate projectors. It also checks real `ell-infinity` operator norms by exhaustive sign corners (a multilinear function reaches its coordinate extrema on the corners of a finite cube), so the comparisons are exact rational inequalities rather than floating approximations. Further checks compare an independently symbolically differentiated composite polynomial against the two decorated second-order chain-rule groups.

The deliberately false controls ensure that these invalid shortcuts are rejected:

* Keeping only diagonal input packet label tuples.
* Dropping completeness of the input projectors.
* Inferring invertible packet coordinates from complete idempotents **without pairwise annihilation**. Three copies of the identity over `F_2` give a minimal counterexample.
* Dropping intermediate packet label sums from the second-order chain rule.

See `evidence/section17/exact_tests.json` for case counts and exact counterexamples. All those tests are **finite checks, not universal formal proofs**.

## 6. Remaining proof obligations

1. Recover the pinned Lean 4.34.0-rc2 compiler, matching mathlib objects, and the nine recorded dependency revisions.
2. Compile both draft modules in an isolated object tree against the inherited checked source without modifying it.
3. Correct any elaboration issues, then audit all new declarations and their transitive axiom dependencies. Repeat kernel replay from upstream imports only.
4. Construct genuinely continuous range inclusion/analysis/synthesis maps and obtain the normed/direct-sum bridge.
5. Connect the exact statement type to `iteratedFDeriv`, including appropriate `C^r` hypotheses and the actual manifold of base points. After that, formalize the projected Taylor remainder with the Bochner integral.
6. Formalize the unrestricted finite-partition Faà di Bruno theorem and pruning support inclusion, not merely the `n=2` equality and term count.
7. Reconcile all claims with the current manuscript and create a matching current Lean reader. The separate October 16 `98+2 / 2693` completion claim remains unsupported by retrieved proof artifacts.

**Accepted prior work remains unchanged.** None of the new draft proof declarations should be counted as compiled or kernel verified until those steps pass.
