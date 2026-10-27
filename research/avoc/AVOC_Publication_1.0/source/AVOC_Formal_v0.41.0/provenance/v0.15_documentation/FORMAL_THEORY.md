# AVOC v0.15.0 — from Bayesian/model errors to guarded policy guarantees

Author: Komorebi P.

## 1. The audit gap this release addresses

The v0.14 audit separated posterior L1 error from L1 error between laws on next controller states. Distinct nearby beliefs can induce disjoint Dirac laws on belief-state space. Therefore a small posterior error cannot simply be substituted into the older total-variation/L1 stochastic abstraction theorem.

This release instead compares expected continuation values over the finite observation alphabet. It proves a division-free mean posterior bound, combines it with explicit continuation-table regularity and exact metadata transport, and propagates model backup residuals into reference Bellman-Q error. That derived error is then used in the existing whole-policy regret and certificate/budget-safety theorems.

All reference-model language is mathematical: the 'raw' system is a declared reference model, not an assertion that its probabilities are the physical truth about a real LLM.

## 2. Finite joint observation laws

Let b,c be normalized rational beliefs on a finite world space Omega. Let E,F be normalized nonnegative channels to the same finite observation alphabet O. Define

    p(o) = sum_w b(w) E(o | w)
    q(o) = sum_w c(w) F(o | w)
    J = sum_o sum_w |b(w) E(o | w) - c(w) F(o | w)|.

The convention throughout is full L1, not half-scaled total variation.

If

    ||b-c||_1 <= alpha
    for each w: sum_o |E(o|w)-F(o|w)| <= beta,

then Lean proves

    J <= alpha + beta
    ||p-q||_1 <= J.

The inputs concern prior and observation-model errors. No optimal-value error is an input.

## 3. Average posterior stability without an evidence floor

Let b_o,c_o be the total Bayes updates. On an impossible observation the established updater returns a normalized fallback belief. Its probability coefficient is zero.

The scaled identity is valid in every case:

    p(o) b_o(w) = b(w) E(o|w).

For any two normalized beliefs x,y and nonnegative mass p, a division-free estimate is

    p ||x-y||_1 <= sum_w |p x(w)-q y(w)| + |p-q|.

Applying it observation by observation yields

    sum_o p(o) ||b_o-c_o||_1 <= 2 J <= 2(alpha+beta).

This result permits zero predictive probabilities and different predictive supports. It is an average under the reference predictive distribution. It does not assert a uniform bound on each posterior branch.

### Why the denominator disappears

A pointwise posterior inequality can divide by a very small evidence mass. Here the same mass weights that branch's contribution to the expectation. The scaled Bayes identity permits the proof to use joint masses directly, without division. This does not repair arbitrary discontinuous continuation functions or make rare-event posterior inference uniformly stable.

## 4. Expected continuation comparison

For observation-specific functions f_o of the next belief, assume

    |f_o(x)-f_o(y)| <= L ||x-y||_1
    |f_o(x)| <= R
    L >= 0, R >= 0.

Then

    |sum_o p(o) f_o(b_o) - sum_o q(o) f_o(c_o)|
       <= (2L+R) J
       <= (2L+R)(alpha+beta).

The proof separates paired posterior-value changes from observation-probability changes. This is the relevant comparison for Bellman control. It does not make a false assertion about total variation between distributions on distinct posterior points.

Source: `AVOC/BayesianObservationTransport.lean`.

## 5. Exact metadata plus approximate belief

The model state has the product form

    z = (approximate belief, exact metadata).

The raw state space may be different and need not be finite. A map phi compiles raw states to model states. For every reference-feasible action, the certificate requires

    A_raw(s) = A_model(phi(s)).

For each paired action/observation branch, the metadata component of phi(rawStep(s,a,o)) must agree with the model successor metadata. The model successor belief must be its declared total Bayesian update. These are explicit equations, not consequences of posterior closeness.

Let W_k be a supplied continuation table. Within a fixed metadata component assume W_k is L_k-Lipschitz in belief L1 and is bounded in absolute magnitude by R_k. Let chi_k bound the probability-weighted discrepancy between the compiled raw successor belief and the raw Bayesian posterior. Then the continuation transport contribution is

    t_k = L_k chi_k + (2L_k+R_k)(alpha+beta).

The first term accounts for an additional posterior codec/quantization step. If the raw belief update is Bayes and the belief encoder has uniform L1 error at most chi, a proved corollary gives the required average codec bound with the same chi.

State-dependent experiments are allowed. Their row errors must actually satisfy the stated bound at the paired states. Exact action feasibility and metadata cannot be silently replaced with approximate belief similarity.

Source: `AVOC/BayesianGuardedBridge.lean`.

## 6. Approximate value tables, not an oracle for exact model values

The planner supplies W_k rather than being assumed to know an exact optimal value. Define

    Qhat_k(s,a) = r_model(phi(s),a)
                  + E_model[W_k(next state) | phi(s),a].

Its model Bellman backup is the maximum over the exact model feasible set. The residual condition is

    |Backup_model(W_k)(phi(s)) - W_(k+1)(phi(s))| <= xi_k.

Also assume W_0(phi(s))=0 and a reference/model reward error at most epsilon on feasible actions.

Define

    D_0 = 0
    D_(k+1) = D_k + epsilon + t_k + xi_k
    H_k = D_k + epsilon + t_k.

Lean proves

    |V_raw,k(s) - W_k(phi(s))| <= D_k
    |Q_raw,k(s,a) - Qhat_k(s,a)| <= H_k.

The convention is that Q_raw,k contains one immediate reward and k further steps, while V_raw,k has k total steps. The indexing is deliberate.

The proof works with state-dependent action sets and potentially infinite state spaces; only action and observation branching is finite. The model certificate assumes backup residuals, not true Bellman-Q errors. Constructing or efficiently certifying the residual over an infinite domain is a separate algorithmic obligation.

Source: `AVOC/GuardedModelError.lean`.

## 7. Whole deployed-policy guarantee

Suppose an implemented estimate Qtilde differs from Qhat by at most kappa_k on feasible actions. Suppose its chosen action is feasible and maximizes Qtilde to additive tolerance tau_k. Then

    0 <= V_raw,n(s) - J_raw,n(s, deployed policy)
      <= sum_(k=0)^(n-1) [2(H_k+kappa_k)+tau_k].

This is the actual return of the complete deployed horizon-dependent policy in the reference system. It is not the first-action bound repeated without proof. Future actions are chosen after observations and recompilation of the resulting reference state.

Specializing the raw system to the v0.14 research protocol additionally preserves the entire certified-task, dependency, queue, and budget invariant over every allowed branch. Value-estimation accuracy controls the performance bound. Guard admissibility and checker soundness independently control the formal invariant.

Main integrated declaration:

    Komorebi.AVOC.Research.certified_bayesian_model_policy

Source: `AVOC/ResearchModelGuarantee.lean`.

## 8. A concrete certifiable regularity class

For a finite nonempty set of rational coefficient rows v, let

    W(b) = max_v sum_w b(w) v(w).

If every |v(w)| <= B, Lean proves

    |W(b)| <= B
    |W(b)-W(c)| <= B ||b-c||_1.

Thus table boundedness and Lipschitz regularity can be supplied by finite coefficient bounds. This avoids assuming that every arbitrary controller or LLM value function is regular. It does not prove that every useful approximation can be represented compactly by such rows or that its Bellman residual is automatically small.

Source: `AVOC/BeliefValueTables.lean`.

## 9. Checked nontrivial examples

### Rare-observation example

Two normalized binary channels have a true-observation predictive mass of 1/200. Their posterior L1 discrepancy on that rare branch is 2. Their joint-law L1 discrepancy is 1/50, and their probability-weighted posterior discrepancy is exactly 1/50. The general average inequality holds, while the attempted per-branch version is formally refuted.

Source: `AVOC/BayesianTransportExamples.lean`.

### Imperfect model and imperfect continuation table

Two always-available actions have raw rewards (1/2, 2/5), while the learned model uses (3/10, 2/5). The observation is uninformative. The supplied table is W_k=k/3, although the model optimum is 2k/5.

The complete primitive certificate has reward error epsilon=1/5, zero observation/codec error, and a nonzero backup residual xi_k=1/15. The model chooses the second action. Lean proves for every horizon n

    V_raw,n = n/2
    J_deployed,n = 2n/5
    actual regret = n/10.

The derived model-Q and whole-policy bounds hold. This checks that the theorem tolerates genuine model and planner-table errors and does not silently assert zero regret. The general bound is conservative, not claimed tight.

Source: `AVOC/ModelBridgeExamples.lean`.

## 10. What has been closed

The audit's G17 is closed for the explicit finite-observation, exact-metadata, residual-certified model class: prior/channel/codec/table/reward errors now produce reference feasible-Q errors and a complete-policy guarantee. This closes the important approximation adapter in G16 as well.

The proof does not establish the numerical hypotheses for a production model, an efficient certified planner, all guarded history/archive adapters, or real candidate-to-receipt authentication. See `GAP_LEDGER.md` and `PROOF_BOUNDARY.md`.

## Mathematical positioning

The general strategy belongs to the established use of regularity and model-error bounds in model-based control. A relevant primary reference is K. Asadi, D. Misra, and M. Littman, “Lipschitz Continuity in Model-based Reinforcement Learning,” ICML 2018, PMLR 80:264–273. This release makes no historical-priority claim. Its contribution to AVOC is the explicit finite rational proof chain and its connection to the existing guarded research protocol.
