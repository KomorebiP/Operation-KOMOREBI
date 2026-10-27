# Lean 0.8.0 — refinement, recursive stability and coherent approximation

**Komorebi Large Signal Model · Komorebi P. · 10 October 2026**

This block adds the reviewed mappings P13 and P18–P21 to the frozen Foundations 1.0.0 formalization. Thirty of its 87 numbered propositions are mapped completely. Fifty-seven remain unformalized. The mathematics and production PR-LASM 2.3.0 are unchanged. The full volume remains the Lean 1.0 target.

The new sources prove the actual limits, residual identities and recurrences, rather than introducing structures whose fields assume the conclusions. Compiler acceptance and the English-to-Lean correspondence are different checks. The latter is documented proposition by proposition in `COVERAGE.md`.

## 1. P13: strong refinement at each fixed horizon

`StrongRefinement.lean` works with actual continuous linear maps. It first proves that a strongly convergent family with a uniform operator bound can act on varying convergent vectors. Induction then proves convergence of each fixed finite power.

For the compression $L_n=P_nLP_n$, the local estimate is

$$
\|L_nx-Lx\|\leq\|L\|\,\|P_nx-x\|+\|P_nLx-Lx\|.
$$

The uniform bound $\|L_n\|\leq\|L\|$ is derived from contractivity of $P_n$. Actual orthogonal subspace projections discharge that contractivity hypothesis through their projection norm theorem. The adapter works over real or complex inner-product spaces and does not require finite dimension.

`strong_fixed_horizon_refinement` concludes

$$
(P_nLP_n)^kx\longrightarrow L^kx
$$

for every fixed vector and fixed natural-number horizon. The proof does not use operator-norm convergence. `estimated_refinement_fixed_horizon` adds an independently bounded fitted family whose error vanishes strongly. Those are supplied mathematical assumptions, not conclusions of a fitting routine.

### Why the fixed horizon matters

The exact scalar example uses $r_n=n/(n+1)$ and the operator $A_nx=r_nx$. It applies the general strong-power theorem to establish convergence to the identity at each fixed horizon. For every fixed resolution $n$, a separate theorem proves

$$
\|A_n^k1-1\|\longrightarrow1\qquad(k\longrightarrow\infty).
$$

Thus the two limiting operations cannot be exchanged. These scalar maps are approximating operators, not orthogonal projections. They illustrate the fixed-power and fitted-operator boundary. The volume's adjacent infinite-dimensional operator-norm counterexample is not separately claimed as a new checked construction here.

## 2. P18: typed local defects generate a global bound

`DefectPropagation.lean` allows a different normed state space at every time. The type is literally `Z : Nat → Type`, not a single vector space with changing labels. It uses the actual true transition, representation maps, approximate update and predicted trajectory.

The residual is the difference between the next true representation and the approximate step evaluated on the current true representation. With both actual and predicted states inside the declared Lipschitz domain, Lean derives the one-step inequality. It then proves

$$
e_T\leq\left(\prod_{j<T}\lambda_j\right)e_0+
\sum_{k<T}\left(\prod_{j=k+1}^{T-1}\lambda_j\right)\delta_k.
$$

`errorEnvelope` is the actual suffix-product expression. Its successor recurrence and empty-product case are proved before the trajectory theorem. The output-decoder inequality and constant-contraction geometric formula are separate declarations.

The linear defect is also split exactly:

$$
RL-\widehat BR=(RL-BR)+(B-\widehat B)R.
$$

A bound on the second term does not eliminate the first.

The expanding scalar example has true signal zero and predicted update $\widehat z_{t+1}=2\widehat z_t+1$, initialized at zero. Its local defect has size one. The general theorem is instantiated and the envelope is proved equal to $2^T-1$. At time three the actual error is seven, not one.

A second example proves that two operators can each square to zero while their alternating product amplifies a state by $4^n$ after $n$ pairs. Individual nilpotence does not supply a common contraction certificate under switching.

## 3. P19: predictions run on their own memory

The finite-memory transition is an actual function of an integer-indexed history:

$$
\mathcal F_t(z)=\widehat A z_t+\sum_{k=0}^{H-1}\widehat K_kz_{t-1-k}.
$$

Integer indices retain the initialization window $-H,\ldots,0$. Natural-number truncated subtraction would silently reuse the initial sample when the intended prehistory is zero; this construction avoids that ambiguity.

`finiteMemory_error_bound` is derived from operator norms on the current error window. With

$$
a=\|\widehat A\|+\sum_{k<H}\|\widehat K_k\|<1,
$$

the invariant radius is

$$
E=\max\left(E_0,\frac{\Delta}{1-a}\right).
$$

Lean proves that $aE+\Delta\leq E$ and performs the induction on the recursively generated prediction. The conclusion includes the actual supremum over nonnegative time, not just a pointwise statement for a selected test horizon.

### The full defect budget is connected to P10

`MemoryApproximation.lean` proves the exact split into coefficient differences, omitted initialized memory and forcing discrepancy. The zero-prehistory identity covers both $H=0$ and $t<H$.

For $K_k=BD^kC$, $\|D\|\leq\rho<1$ and a true-history bound $Z$, the derived budget is

$$
\Delta=Z\left(\|A-\widehat A\|+\sum_{k<H}\|K_k-\widehat K_k\|\right)
+\|B\|\|C\|Z\frac{\rho^H}{1-\rho}+F_0.
$$

Here $F_0$ bounds the difference of the true and retained initialization forcing. Dropping $BD^tq_0$ permits $F_0=\|B\|\|q_0\|$; retaining it exactly permits $F_0=0$. `certified_memory_truncation` inserts this derived budget into the recursive supremum theorem.

The stability test is sufficient, not necessary. A failed norm-sum certificate is not a proof that a recurrence is unstable. Bounded true histories, the contraction hypothesis and initialization bounds remain explicit.

### An actual recursive example

The new example compares the zero reference signal with

$$
\widehat z_{t+1}=\tfrac12\widehat z_t+\tfrac14\widehat z_{t-1}+\tfrac18,
\qquad\widehat z_{-1}=\widehat z_0=0.
$$

It constructs the trajectory recursively as current/previous pairs, embeds it into an integer history and proves the recurrence. The first three values are $1/8,3/16,1/4$. Applying the general theorem gives a uniform error bound $1/2$ because $a=3/4$ and $\Delta=1/8$.

This is a separately declared reference calculation, not a recovery of an older dataset or the manuscript's original hidden generator. It tests the distinction between a true-history residual and a predictor driven by its own history. A gain-one drift example has bounded local residual and unbounded accumulated error.

## 4. P20: retain every ordered interaction that is claimed

The packet model uses actual continuous multilinear maps. `HasPacketBound` quantifies over vectors in the actual specified packet ranges, and bounds the map by their product norms. The exact full expansion follows from multilinearity and complete synthesis.

`omitted_interaction_identity` proves that the full polynomial minus the retained polynomial is precisely the sum over omitted ordered tuples. Repeated indices and cross terms are not silently removed. It yields

$$
\|F(x)-F_{\mathcal I}(x)\|\leq
\sum_m\sum_{\boldsymbol i\notin\mathcal I_m}
\beta_{m,\boldsymbol i}\prod_j\|P_{i_j}x\|.
$$

The Lipschitz estimate telescopes one multilinear argument at a time. On a ball of radius $R$ it gives the stated degree factor $m\beta R^{m-1}$. Actual orthogonal subspace projections supply contractivity in the Hilbert adapter. The underlying algebraic theorem is valid in the more general declared normed-space setting.

An independent nonpolynomial remainder is added through a separate triangle inequality. The theorem does not infer that an unexpanded physical law equals its polynomial model, nor that predicted trajectories stay inside the declared ball.

The exact two-packet example keeps all degree-one terms and only same-packet degree-two terms:

$$
F(u,v)=u+v+(u+v)^2,\qquad
F_{\mathcal I}(u,v)=u+v+u^2+v^2.
$$

Both the general truncation and Lipschitz theorems are instantiated using proved packet-range bounds. The omitted difference is exactly $2uv$ and its magnitude is $2|u||v|$. At $(2,3)$ it is twelve. This example uses the explicit product maximum norm; the general orthogonal Hilbert adapter is separate.

## 5. P21: reconcile in one object space

A linear atlas has analysis $A_a$, synthesis $S_a$ and $S_aA_a=I$. Its realizable coefficient space is the actual range subtype of $A_a$. The formalization constructs encode/decode maps and proves that they are inverses on that subtype.

Fitted chart operators are pulled back as $L_a=S_aG_aA_a$. The weighted mean $\overline L=\sum_aw_aL_a$ is then re-encoded as $A_a\overline LS_a$. Consistency and every atlas intertwining identity follow from the actual reconstruction laws.

The weighted variance identity is proved in a real inner-product space and for the explicit finite Frobenius sum. A chosen orthonormal basis is constructed for the finite-dimensional real operator adapter. The resulting coordinate equivalence links the Frobenius objective to actual linear operators. Unique minimization follows from the nonnegative squared distance to the mean; the mean is the minimizer, not an assumed optimization output.

For actual continuous-operator norms and nonnegative weights summing to one,

$$
\|\overline L-L_*\|\leq\sum_aw_a\|L_a-L_*\|.
$$

The weighted fits $2,4$ with weights $1/4,3/4$ have mean $7/2$ and minimum squared cost $3/4$. Lean applies the general variance/minimum theorem to prove uniqueness. A unanimous fit of four is also exactly four even when the intended target is zero. Agreement is not correctness.

### The coefficient norm is transported, not confused with an ambient norm

`coeffNormed` and `coeffNormedSpace` construct genuine normed structures through the injective decoder:

$$
\|c\|_a=\|S_ac\|.
$$

The general transport theorem is an isometry in these explicitly induced structures. The represented transition has exactly the same set of valid Lipschitz constants as the object-space map, in both directions. These are not assertions about whatever ambient subtype metric may also exist on redundant coefficient arrays.

The concrete atlas $A(x)=(x,2x)$ rejects $(1,0)$ as nonrealizable. Repair maps any ambient output back into the range. A second atlas scales the signal by three. Its ordinary ambient metric is not preserved, whereas the decoded pullback distance is preserved exactly. The general theorems specify the induced metric explicitly; client code should not silently substitute an ambient subtype instance.

## 6. Evidence and scope

The ten new modules are `DefectPropagation`, `StrongRefinement`, `MemoryStability`, `MemoryApproximation`, `PacketApproximation`, `WeightedReconciliation`, `AtlasReconciliation`, `ReconciliationHilbert`, `Block8Examples` and `Block8ApproximationExamples`.

They add 115 named theorems, including 47 in the two example modules. Cumulatively the source has 67 proof modules, 1,178 explicitly named declarations and 904 named theorems. There are 613 foundation/supporting theorems and 291 example-module theorems. These are source-declaration counts, not novelty counts or general performance measures.

Ten new intentionally false proof files test dropped horizon, recursive-stability, prehistory, domain, packet-interaction, weighting, correctness and metric requirements. They are outside the active import graph. A rejection only counts when Lean returns a proof diagnostic, not when an import, identifier or runtime is missing.

Use the current verification reports for actual build outcomes. Kernel replay is additional checking within Lean's own implementation. It is not a second proof assistant or a fresh exhaustive rebuild of imported Mathlib. There is no production-code validation, sensor experiment, statistical coverage experiment or new model checkpoint in this block.
