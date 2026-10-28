# Machine Societies: stochastic closure and error bounds

**27 October 2026 · Komorebi P. · AI-assisted sequential self-review · Batch 3**

Six additional statement/proof pairs were checked against [commit c1ac19ba8e5c](https://github.com/KomorebiP/Operation-KOMOREBI/commit/c1ac19ba8e5c5557be02145f56d2f0e5bf37dd69). **All six are proved as written under their declared hypotheses.** The main boundaries are uniform rather than training-average error, the permitted control policy, the report/transition independence convention, and a fixed review schedule.

Combined coverage is now **32 distinct pairs out of 62: 31 recorded passes, one qualified memory bound, and 30 unreviewed**. The original 15-claim record and the previous [three-claim](MACHINE_SOCIETIES_PROOF_REVIEW_2026-10-27.md) and [eight-claim](MACHINE_SOCIETIES_PROOF_REVIEW_BATCH2_2026-10-27.md) review batches retain their dates, exact scope, and provenance. Their verdicts are not presented as a fresh independent review. The memory statement still needs its positive finite-index condition integrated into a revised source edition.

The [review record](../manifests/machine-societies-review-batch3-2026-10-27.json) preserves each exact statement/proof block and hash. The [coverage index](../manifests/machine-societies-review-index.json) checks unique labels, source identity, and separate qualified/pass counts. The manuscript SHA-256 remains `600a8100804c4c91d7cf79a4985e9312eacc19195395aee01debb240cb0a6be0`. No manuscript, PDF, or earlier review was rewritten.

## Shared finite-probability obligations

The proofs use the following elementary facts, reconstructed here to expose their dependencies. For finite laws $p,q$, the positive and negative parts of $p-q$ have the same mass, equal to $\operatorname{TV}(p,q)$.

- **Common stochastic kernel:** for row-stochastic $K$, summing $\left|\sum_x(p(x)-q(x))K(x,y)\right|$ over $y$ and applying the triangle inequality gives $\operatorname{TV}(pK,qK)\leq\operatorname{TV}(p,q)$. The same inequality gives convexity when mixing row errors with common nonnegative weights summing to one.
- **Bounded observation:** for $0\leq f\leq1$, the positive/negative mass decomposition bounds $|\mathbb E_p f-\mathbb E_q f|$ by $\operatorname{TV}(p,q)$. The indicator of the positive difference attains the positive bound.
- **Finite maximal coupling:** the common masses $\min\{p(x),q(x)\}$ sum to $1-\operatorname{TV}(p,q)$. Couple those masses identically and distribute the remaining masses with the required marginals. The remaining supports are disjoint. At common mass zero or one, use only the applicable branch. Thus the mismatch probability equals total variation. For any coupling, the probability of mismatch bounds total variation because event membership can differ only when the outcomes differ.

These are details of the written proof routes, not numerical experiments or external theorem assumptions. The references surrounding the source propositions provide context. This pass does not verify bibliography, attribution, or priority claims.

## Claim reviews

<a id="controlled-lumpability--proplump"></a>

### Controlled lumpability: `prop:lump`

**Primary verdict: proved as written.** Source: [publication manuscript](../monographs/machine-societies/publication/Machine_Societies_v1.0.0.tex), line 312.

**Claim.** A common macro-kernel represents every projected microstate row exactly if and only if projected transition probabilities are constant on each fibre. Under a common macro-history policy, all projected history laws agree with the reduced model. Output agreement additionally requires fibre-constant output laws under the source’s conditional-independence convention.

**Hypotheses.** Finite nonempty microstate, control, and output sets, row-stochastic transition/output kernels, a surjective macrostate map, the same policy depending only on macro-history, and matched initial macro-laws. The model explicitly makes the current report and next state conditionally independent given the current microstate and control.

**Argument.** The common fibre values are nonnegative and sum to one, hence define a stochastic macro-row. Conditional on a reachable macro-history and chosen control, the microstate distribution is supported on the current fibre. Averaging identical projected rows preserves that macro-row. Induction gives history-law equality. Point-mass initializations and a fixed control give necessity. Fibre-constant output rows and the conditional-independence convention also make the joint next-macrostate/current-output row constant on each fibre.

**Dependencies.** Finite row sums and surjectivity → well-defined macro-kernel. Conditional distribution on a fibre → common next-state law → induction. Point-mass tests → necessity. Conditional independence + fibre-constant output rows → joint output/state preservation. All leaves are hypotheses, conventions, or the internal proof.

**Boundary checks.** Singleton and identity quotients, stochastic and deterministic rows, zero-probability histories (no conditional law is asserted there), and randomized macro-history policies. A controller reading the discarded microstate is outside the policy class. Equality of the two marginals is insufficient for a dependent report/transition mechanism. The joint law must then be preserved.

**Strongest safe statement.** Exact projected histories and, with the stated output assumptions, output histories are preserved under the specified common policy class. This does not establish that an arbitrary learned summary satisfies the fibre test.

**Remaining gap:** none in this implication under the declared hypotheses. **Next discriminating check:** For an applied abstraction, compare every projected row for each allowed control and check the joint output convention before extending the policy class.

<a id="approximate-closure-over-time--proptime"></a>

### Approximate closure over time: `prop:time`

**Primary verdict: proved as written.** Source: [publication manuscript](../monographs/machine-societies/publication/Machine_Societies_v1.0.0.tex), line 345.

**Claim.** A uniform one-step projected-kernel error at most epsilon gives marginal error at most min(1, e0 + t epsilon) under the same predeclared open-loop controls. If every reduced kernel contracts total variation by a factor kappa < 1, the error is at most kappa^t e0 + epsilon(1-kappa^t)/(1-kappa). Matched macro-history policies retain the linear path-law bound. Their contraction estimate needs an additional closed-loop contraction premise.

**Hypotheses.** The finite controlled model, a uniform bound over all microstates and allowed controls, an initial macro-law discrepancy at most e0, and the same predeclared controls for the marginal/contraction estimates. The contraction coefficient has its usual nonnegative meaning. For the adaptive path claim, both models use the same macro-history policy.

**Argument.** Average the row error over the actual microstate distribution. Comparing the two current macro-laws after the common reduced kernel gives e(t+1) ≤ epsilon + e(t), or epsilon + kappa e(t) under contraction. Iteration gives the displayed bounds. For the adaptive claim, couple initial macrostates with failure probability at most e0. While histories agree, use the same sampled control and a finite maximal coupling of the next macro-laws. A first-mismatch union bound gives e0 + t epsilon for the complete macrostate path.

**Dependencies.** Uniform row error + convexity of total variation → one-step comparison. Common-kernel nonexpansiveness or the stated contraction → recurrence → finite geometric sum. Matched history policies + maximal coupling → first-mismatch bound. Finite total-variation facts are reconstructed above. No external stability theorem is needed.

**Boundary checks.** t = 0, epsilon = 0, kappa = 0, and bounds above one. At t = 0 the empty product is one. For feedback, individual control kernels can all be constant (contraction zero) while a state-dependent choice of control makes the closed-loop chain the identity. Thus the source correctly keeps the open-loop contraction claim separate from its adaptive path claim.

**Strongest safe statement.** The stated open-loop error estimates and matched-policy finite path estimate hold. Small training-average error is not the uniform row premise, and per-control contraction is not closed-loop contraction.

**Remaining gap:** none in this implication under the declared hypotheses. **Next discriminating check:** For a proposed feedback controller, certify the closed-loop contraction separately or use the weaker finite-horizon path bound.

<a id="implementation-dependence--proplift"></a>

### Implementation dependence: `prop:lift`

**Primary verdict: proved as written.** Source: [publication manuscript](../monographs/machine-societies/publication/Machine_Societies_v1.0.0.tex), line 382.

**Claim.** If all admissible reset implementations have outcome laws within epsilon of one proposed law, their diameter eta(x,z′) is at most 2 epsilon. If two admissible implementations are distance eta apart, no one law can approximate both with error strictly below eta/2.

**Hypotheses.** A feasible target, a nonempty declared reset family supported on the target fibre, and one fixed outcome experiment on a common outcome space. Each outcome law is compared with the same proposed macro-intervention law.

**Argument.** For any pair, insert the proposed common law and apply the triangle inequality. Then take the supremum over pairs. Conversely, if both errors were below half the pair distance, the triangle inequality would make their sum strictly smaller than that distance, a contradiction.

**Dependencies.** Common outcome space and reference law → total-variation triangle inequality → pairwise upper bound → supremum. The same inequality in reverse-obstruction form → half-distance lower bound. No attained maximum is needed for the first implication.

**Boundary checks.** A singleton reset family, epsilon = 0, and large epsilon where 2 epsilon exceeds one. Two disjoint point-mass laws have distance one and their equal mixture attains error one-half for that pair. This is a necessary radius bound, not a theorem that every larger family has a common center at half its diameter.

**Strongest safe statement.** Implementation ambiguity is bounded by twice a certified common-law error, and a separated pair obstructs a smaller common error. Feasibility, permission to reset, and the proposed common-law certificate are separate obligations.

**Remaining gap:** none in this implication under the declared hypotheses. **Next discriminating check:** Specify the admissible resets and common outcome experiment, then exhibit either a common-law bound or a separated admissible pair.

<a id="accumulation-of-cultural-transport-defects--proptransport"></a>

### Accumulation of cultural transport defects: `prop:transport`

**Primary verdict: proved as written.** Source: [publication manuscript](../monographs/machine-societies/publication/Machine_Societies_v1.0.0.tex), line 1379.

**Claim.** For metric spaces Z_j, updates F_j, Lipschitz translators T_j with constants L_j, and finite one-step commutation defects epsilon_j, the composite defect after m translations is at most the sum over j of epsilon_j times the product of all later L_k.

**Hypotheses.** Every update is a self-map of its stated metric space and every translator maps to the next space. The local defects are uniform suprema over their whole domains, and the Lipschitz constants are finite and nonnegative.

**Argument.** At the last translation, insert the translated prior-generation update. The first distance is at most L_(m-1) times the prior defect. The second is at most epsilon_(m-1) at the translated input. This gives D_m ≤ L_(m-1) D_(m-1) + epsilon_(m-1). Expanding that recurrence yields exactly the product over the later translators for each local defect.

**Dependencies.** Map typing → valid intermediate point. Lipschitz estimate + local defect supremum → recurrence. Induction → weighted sum. The already-reviewed repair-budget recurrence is consistent with this argument, but this proof gives its own induction.

**Boundary checks.** One translation gives epsilon_0. Two give L_1 epsilon_0 + epsilon_1. A zero later Lipschitz constant removes earlier contributions. Constants above one can amplify them. The zero-translation case is the identity with zero defect. No supremum attainment, compactness, or Lipschitz property of F_j is needed.

**Strongest safe statement.** The composite preserves the declared update up to the displayed weighted defect. Injectivity, reconstruction, all obligations, and all provenance are not implied by commutation of this one declared operation.

**Remaining gap:** none in this implication under the declared hypotheses. **Next discriminating check:** For an actual translation chain, establish uniform local defects and translator Lipschitz constants on the declared domains, including every operation that must be preserved.

<a id="finite-block-institutional-averaging--thmblock-averaging"></a>

### Finite-block institutional averaging: `thm:block-averaging`

**Primary verdict: proved as written.** Source: [publication manuscript](../monographs/machine-societies/publication/Machine_Societies_v1.0.0.tex), line 1535.

**Claim.** Under the uniform m-step mixing bound, every reachable institutional-history conditional next-review law is within epsilon of the stationary endpoint average. With the same initial institutional law, total variation between T-review path laws is at most 1-(1-epsilon)^T, hence at most min(1,T epsilon).

**Hypotheses.** Finite institutional and fast-state spaces, a predeclared integer m ≥ 1, a fixed institution during each block, a stationary law for each fast kernel, a uniform row mixing bound with 0 ≤ epsilon ≤ 1, and a common endpoint-to-institution stochastic channel. Subsequent fast resets cannot revise the already selected institutional outcome.

**Argument.** Push the fast endpoint law and stationary law through the same revision channel. Stochastic-kernel nonexpansiveness preserves the epsilon bound. Average over the conditional fast state for a positive-probability institutional history. Starting with identical institutional states, maximally couple successive review outcomes while histories agree. Each conditional agreement probability is at least 1-epsilon, so complete agreement has probability at least (1-epsilon)^T. The coupling inequality and union bound give the two estimates.

**Dependencies.** Uniform mixing + common endpoint channel → uniform review-row bound. Conditional averaging → history-dependent bound. Identical initial institutions + finite maximal coupling → product of conditional agreement bounds → path-law estimate. The proof does not invoke a singular-perturbation limit or an external averaging theorem.

**Boundary checks.** T = 0 uses an empty product of one, including epsilon = 1. With epsilon = 0, path agreement is exact. Successive fast states may be correlated through resets and history. A data-dependent stopping time or a revision depending on the full fast trajectory violates the stated endpoint/fixed-block model and is not covered.

**Strongest safe statement.** Institutional paths at the specified review epochs are approximated for the declared finite horizon. The bound does not preserve every intervening action or establish actual fast mixing, safety between reviews, or empirical institutional stability.

**Remaining gap:** none in this implication under the declared hypotheses. **Next discriminating check:** Establish the uniform mixing bound for each actual fast kernel and verify that the review schedule and revision rule use exactly the declared fixed endpoint experiment.

<a id="a-robust-margin-for-reduced-model-enforcement--proprobust-deterrence"></a>

### A robust margin for reduced-model enforcement: `prop:robust-deterrence`

**Primary verdict: proved as written.** Source: [publication manuscript](../monographs/machine-societies/publication/Machine_Societies_v1.0.0.tex), line 1578.

**Claim.** The sanction chosen by the positive reduced-law difference makes compliance weakly preferable when g ≤ F(dbar-epsilon_C-epsilon_D). No bounded observation-based sanction deters if g > F min(1,dbar+epsilon_C+epsilon_D). Its true compliance-sanction probability is at most its reduced-model probability plus epsilon_C.

**Hypotheses.** The source’s one-deviation model: g > 0, fixed F > 0 in the same utility units, risk neutrality, a committed sanction in [0,1], feasible authorized collection, and all other utility differences included in g. True and reduced observation laws share the finite alphabet and have the stated total-variation error bounds.

**Argument.** A [0,1]-valued sanction changes expectation by at most the law’s total-variation error. In the reduced model, the positive-difference indicator attains dbar. Subtracting the two expectation errors gives the lower bound on its true sanction gap. The source payoff identity gives sufficiency. The triangle inequality bounds the true total variation by dbar+epsilon_C+epsilon_D, capped at one. The previously reviewed bounded-sanction optimum gives the impossibility condition. The compliance inequality is the one-law expectation bound.

**Dependencies.** Finite signed-mass identity → bounded-function expectation estimate. Reduced positive-difference indicator → gap dbar. Certified law errors → true gap bound → payoff identity. Triangle inequality + prop:deterrence-tv → impossibility. The raw proof of that already-counted dependency was rechecked for this use. It is not counted twice.

**Boundary checks.** Zero approximation errors recover the exact discrimination threshold. Equality in the sufficient condition gives weak preference and permits indifference. Tied reduced probabilities contribute zero and may be excluded from the indicator. A negative lower margin supplies no positive-g certificate. The impossible region is strict. The unclassified gap between the two sufficient criteria remains undecided. The final compliance bound can be capped at one without changing its validity.

**Strongest safe statement.** These are conditional incentive bounds for one specified deviation and fixed penalty model. They do not establish voluntary participation, legitimate enforcement, feasible collection, or a useful certificate when the error margin is too large.

**Remaining gap:** none in this implication under the declared hypotheses. **Next discriminating check:** Certify the two conduct-specific law errors and the penalty/payoff assumptions before applying the sufficient deterrence margin.

## Two small checks on assumptions

**Feedback can destroy per-control contraction.** Take two states and two controls, with both rows of $K_0$ equal to the point mass at 0 and both rows of $K_1$ equal to the point mass at 1. Each fixed-control kernel contracts total variation to zero. The common feedback policy $u=z$ instead gives the identity transition. Initial laws concentrated at 0 and 1 stay distance one apart. This is why `prop:time` explicitly requires a separate closed-loop contraction condition for the adaptive setting. It is not a counterexample to the stated proposition.

**Equal marginals do not determine the output/state joint law.** Let the microstate include a hidden bit $h$ and a retained bit $z$. Sample a fresh fair bit $b$, keep $h$ fixed, set the next retained state to $b$, and report $y=b\mathbin{\oplus}h$. For either value of $h$, both marginals are fair. The joint law has $y=b$ when $h=0$ and $y\ne b$ when $h=1$. This mechanism violates the source's conditional-independence convention. Its marginal tests cannot be used to claim the full output/state preservation of `prop:lump`.

Both checks are direct finite arguments about the premises. No executed numerical test or empirical claim is attached to them.

## Downstream scope and remaining work

The adjacent compositional finite-horizon estimate at source line 545 uses `prop:composition` (reviewed in batch 2) together with `prop:time` (reviewed here). With the same predeclared controls and initial macro-law error $e_0$, the one-step defect is at most the sum of the layer errors, so the time-$t$ marginal bound is $\min\{1,e_0+t\sum_j\varepsilon_j\}$. The matched-history path version retains the policy restriction. Contraction requires the additional applicable contraction premise. This checks that named dependency link without counting the corollary as another one of the 62 pairs.

The reduced-model enforcement result can use the block-averaging law bound only when each conduct-specific fast kernel satisfies the uniform mixing premise and the same endpoint-to-evidence channel is used in the actual and reduced models. No inferred mixing time or enforcement effectiveness for real agents has been added.

| Obligation | Result for the six claims |
|---|---|
| Object types, quantifiers, and domains | Passed under the stated finite-model or metric-space contracts |
| Written implications and dependency direction | Passed. Shared finite-probability facts reconstructed above |
| Boundary cases and initial-time conventions | Passed. No hidden division by zero or assumed supremum attainment |
| Dependency cycles | None identified |
| Executed computation or Lean evidence | None used or newly claimed |
| Actual mixing, learned abstraction error, implementation access, or enforcement feasibility | Out of scope. Explicit next checks above |
| Independent peer review or literature priority | Not claimed |

The count is a source-bound review inventory, not a correctness percentage or whole-book certification. The next written-proof batch can inspect safety invariants, finite-horizon viability, and amendment normal forms, resolving any external proof dependencies before recording a pass. Thirty statement/proof pairs and the memory source-edition clarification remain open. The 13 recently imported collections also retain their separate unassessed status and F16 review gate.
