\begingroup\footnotesize\setlength{\cftbeforesecskip}{0pt}\tableofcontents\endgroup\newpage

# Reading the large signal model as one mathematical object

**Foundations 1.0.0. Scope frozen at 87 propositions.**

A large signal model should not be defined by a long inventory of transforms. Its defining question is whether an observed signal can be represented, transformed, compressed and used for inference without losing the information required by those operations.

This guide gives a single route through the existing results. It introduces no new numbered propositions and does not claim that the reference software implements every theorem. Proposition numbers refer to the cumulative foundations volume. The proof register records their hypotheses and restricted code counterparts.

## The central definition

The deterministic sector begins with a typed signal space $X$, an exact archive, a predictive state map $\gamma$, and a declared family of operations $F_u$. Its central contract is

$$
\gamma F_u=\bar F_u\gamma.
$$

The probabilistic sector adds an admissible state domain, a mass functional, and observation operators. Its contract is not merely matrix multiplication. It must give nonnegative event probabilities, normalized observations and admissible updated states.

The model is therefore a representation **together with the operations that are allowed to pass through it, the conditions under which they preserve meaning, and the defects when those conditions fail**.

The word *large* describes the structured hypothesis family: coordinate systems, packet resolutions, operators, compositions, memory mechanisms and statistical alternatives. It is not a measured parameter count or a theorem of universal discovery.

# 1. Preserve the observation, then declare the prediction

An observation is a typed object. A finite periodic signal is not the same object as a zero-extended signal with the same displayed values. A categorical palette is not an arbitrary real vector space. Boundary conventions, shape and scalar field belong in the type.

An archive has analysis and synthesis maps

$$
A:X\to C,\qquad S:C\to X,\qquad SA=I_X.
$$

This preserves the accepted observation. It does not recover physical variables that were never measured. It also does not say that a smaller feature vector is sufficient for future prediction.

A predictive state $z=\gamma(x)$ is adequate only relative to specified future quantities and actions. Two different signals may share a sufficient predictive state. Conversely, a lossless archive can feed an insufficient summary.

The exact quotient criterion is Proposition 6: whenever two admissible signals have the same summary, their next summaries must agree under every declared action. If that implication fails, no deterministic memoryless transition on that summary can be exact on the stated domain.

**Reading route:** Propositions 1–2 establish exact realization and coherent coordinate transport. Propositions 6–8 establish quotient sufficiency, its linear defect and a known-model completion.

# 2. Packets decompose both signals and operations

For a complete orthogonal resolution,

$$
x=\sum_iP_ix,\qquad I=\sum_iP_i.
$$

A packet includes the component, its projector, atlas, type and resolution. Energy alone is not the packet. Refining a complete projector tree preserves reconstruction. Dropping a branch or retaining only its energy changes that contract.

A linear operation has transfer blocks

$$
L_{ji}=Q_jLP_i,\qquad L=\sum_{j,i}L_{ji}.
$$

Composition sums over intermediate packets. This gives an exact way to identify an omitted route through the representation.

For a retained projector $P$ and $Q=I-P$,

$$
PLMP-(PLP)(PMP)=PLQMP.
$$

The defect is the path that leaves the retained space and returns. It is not necessarily controlled by omitted energy alone. A small unresolved component can have a large future effect through a large transfer block.

Nonlinear operations require interactions. A polynomial map admits a multilinear packet expansion, but the mixed terms cannot be discarded merely because the inputs were decomposed. The missing $2uv$ in $(u+v)^2$ is the simplest example.

**Reading route:** Propositions 3–5 give complete refinement and transfer identities. Propositions 7, 20 and 57 describe compositional, nonlinear and averaging defects.

# 3. Closure has two repairs, and both have costs

For known finite linear dynamics, repeatedly adding the pullbacks of required observables constructs the smallest invariant observable row space. That construction is exact, but it may reach the full state space. Its additional observables may also be inaccessible from the measurements actually available.

Memory offers another description. Splitting a linear state into retained and unresolved variables gives

$$
z_{t+1}=Az_t+Bq_t,\qquad q_{t+1}=Cz_t+Dq_t.
$$

Eliminating $q_t$ produces

$$
z_{t+1}=Az_t+\sum_{k=0}^{t-1}BD^kCz_{t-1-k}+BD^tq_0.
$$

The kernel records unresolved evolution and return. State enlargement and retained memory are related constructions, not unrelated architectural options.

The distinction between a formula evaluated on the true history and a recursively generated forecast is essential. Proposition 10 bounds a tail evaluated on the true retained history under a contraction assumption. Proposition 19 separately controls recursive finite-memory prediction under a gain condition.

A proposed refinement also needs initialization. A finer summary $\eta(x)$ can be obtained from a coarse summary $\gamma(x)$ alone exactly when $\eta$ is constant on every fiber of $\gamma$. In the linear case this requires $\ker\gamma\subseteq\ker\eta$. An archive, a new observation or uncertainty over the finer states is necessary when that factorization fails.

**Reading route:** Propositions 8, 10, 18–19 and 22. Do not treat a small spectral radius as the induced-norm contraction hypothesis stated in a particular bound.

# 4. Learning identifies a model inside a declared class

The autonomous linear construction uses observation windows. When the true observation-map ranks stabilize at delay $h$, the realizable history space closes under a linear transition. Paired exact windows identify that transition on their spanned space.

The worked scalar example learns

$$
y_{t+1}=\frac56y_t+\frac1{12}y_{t-1}
$$

without receiving the hidden transition matrix. Its general predictive claim requires that the observed windows span the true realizable history space. An empirical rank plateau does not establish that global assumption.

For controlled stochastic signals, the predictive state instead describes probabilities of future experiments under prescribed actions. A complete finite-rank history/test representation leads to

$$
B_s=G_sH^{-1}.
$$

Here $H$ is the selected core table and $G_s$ inserts the next action/observation pair. The inverse is justified only under its specified rank and coverage conditions.

A finite prefix can always be matched by a larger hidden mechanism that changes the future later when no dimension restriction is supplied. Proposition 17 supplies an explicit delayed-response example. The role of assumptions is not to weaken an otherwise unconditional claim; they define what is identifiable.

**Reading route:** Propositions 14–17, 25, 27–28 and 37. The nonlinear dictionary and global rank bound are not learned merely by fitting these finite tables.

# 5. Probability meaning requires a domain

For finite observations, write $B_{a,o}$ for the joint action-and-observation operator, $\lambda$ for total mass, and $C$ for the cone of admissible unnormalized states. The basic laws are

$$
B_{a,o}C\subseteq C,\qquad
\lambda\sum_oB_{a,o}=\lambda.
$$

If $z\in C$ has unit mass, the next observation has probability $\lambda B_{a,o}z$. Conditioning divides the branch state by this positive mass. A zero-probability branch has no model-determined posterior.

A finite positive-lift witness supplies normalized generators $V$ and nonnegative matrices $A_s$ with

$$
B_sV=VA_s,\qquad A_s\geq0,\qquad \lambda V=\mathbf1^{\mathsf T}.
$$

Iterating this identity establishes validity at every finite horizon. Checking thousands of words illustrates the identity but is not what proves the all-horizon conclusion.

Not every small valid model admits such a polyhedral witness. The rank-three rotation/probe example has a disk as its normalized state domain. It instead admits a finite symmetric-matrix certificate. This is a change in the language used to certify the same exact model, not evidence that the earlier polyhedral impossibility was wrong.

Signed spectral packets remain useful. They generally are not probability components individually. Full synthesis preserves the represented state; packetwise probabilistic interpretation needs its own positivity conditions.

**Reading route:** Propositions 29–30, 38–39, 46 and 50–53.

# 6. Continuous observations require a reference measure

For an operator density $B_a(u)$ relative to a probability reference measure $\mu$,

$$
P(A\mid z,a)=\int_A\lambda B_a(u)z\,\mu(du),
\qquad
\lambda\int B_a(u)\,\mu(du)=\lambda.
$$

A density can exceed one. A single observed value can have probability zero while its density is positive. Conditional states for general measurable kernels are defined up to the appropriate null-set convention.

Moment-based reconstruction needs a correct observation basis and an invertible moment matrix. Distinct positive densities can agree on finitely many moments. The basis assumption cannot be removed by checking positivity.

Binning by exact operator integration preserves binned event probabilities. Averaging a matrix factor before applying its quadratic action is different:

$$
\mathbb E[KXK^{\mathsf T}]
=\bar KX\bar K^{\mathsf T}
+\mathbb E[(K-\bar K)X(K-\bar K)^{\mathsf T}].
$$

The covariance term is a typed averaging defect. Dropping it can lose probability mass. Positive integral approximations provide a valid alternative under stated regularity assumptions, with approximation bias kept separate from estimation error.

**Reading route:** Propositions 52, 54–59 and 64–65. Continuous-valued observations do not make this a continuous-time process theory.

# 7. There are three kinds of acceptance

**Numerical proposal.** A fitting or geometric procedure proposes coefficients, a center or a metric. A small residual can guide a search. It is not an all-domain probability certificate.

**Exact structural acceptance.** A finite witness is checked against the submitted operators, measure and domain. It can establish that the model is internally valid for every admissible input and observation. It does not identify the unknown generating process.

**Statistical coverage.** A justified uncertainty set contains the true model with the stated probability, under its model and data assumptions. A robust witness must cover that whole set to transfer the structural guarantee to the true member on the coverage event.

These layers can be combined only when their types, coordinates, initial states and uncertainty quantifiers agree. A witness for the center of a confidence set does not cover all members. A repaired model can lie outside a confidence set for the unmodified process. Transforming only the fitted center while leaving the uncertainty in old coordinates changes the statement.

The production runtime remains 2.3.0. These are mathematical constructions and reference-checking programs. No integrated production learner that automatically supplies all assumptions is claimed.

**Reading route:** Propositions 40–41, 48–49, 62–63, 71–78 and 87.

# 8. Two later examples must remain separate

## Deterministic repair

The perturbed-operator example starts with a known rational coefficient family and a numerically proposed geometry. Its smaller certified reset weight is $1/32$. For the fixed geometry, path and required margin, a separating functional and complete certificate give

$$
\frac{864543451}{37599646576}\leq\eta_*\leq\frac1{32}.
$$

A second witness validates the comparison domain. The resulting complete-record bound is

$$
\min\left(1,\frac{87471T}{2560000}\right).
$$

It is informative through integer horizon 29 and trivial from 30. There is no empirical coverage claim for that deterministic uncertainty tube.

## Dependent observable learning

A different example supplies the feature map $v(u)=(1,u,u^2)$, a reference measure, and a two-parameter conditional family. The state after observing $u$ is exactly $v(u)$, so its regressors are accessible rather than estimated hidden states.

For the saved five-node trajectory, the outward-rounded intervals are

$$
0.356\leq a\leq0.462,\qquad 0.116\leq b\leq0.290.
$$

Every member has density at least $0.248$ relative to its declared measure. A 95 percent time-uniform coverage theorem applies under the supplied conditional model and predictable data protocol. The reference run illustrates it; one seeded path does not estimate its coverage frequency.

The discrete reference measure and continuous uniform measure share the moments used in the construction. Their total-variation distance is nevertheless one. Neither law is substituted for the other.

These two examples do not form one general noisy hidden-state learner. Their shared machinery is explicit, while their supplied information and statistical guarantees remain different.

**Reading route:** Propositions 79–80 for the repair and 81–87 for the observable learning sector. `SCENARIO_REGISTER.json` records this separation directly.

# 9. Choose the bound that answers the question

A bound should name its mathematical target, not merely say that predictions are close.

| Target | Required comparison | Limitation |
|---|---|---|
| Reconstructed observation | Exact archive or numerical reconstruction error | Does not establish predictive closure |
| Recursive state forecast | Lipschitz or gain control plus local defects | Must contain both trajectories in its domain |
| Full observation record | Common policy and instrument or conditional-law error | Can grow with the horizon |
| Posterior after an event | Full-law error and positive evidence | Rare evidence amplifies error |
| Single future-time marginal | Markov structure, minorization and one-step discrepancy | Does not bound arbitrary-length records |
| Rejected residual test | Predictable bounded test and time-uniform budget | Gives a lower discrepancy statement, not a nonrejection guarantee |

For the dependent example, the uniform next-observation bound is $2437/90000$. The complete-record bound is $\min(1,2437T/90000)$. Under its additional Markov minorization, the single-time marginal bound is uniformly $2437/22320$. These are different claims, not competing estimates of one quantity.

# 10. What the preceding audit established

No new propositions were added. The 0.9.0 candidate retained 87 written results, all preserved in this release. The proof register covers all of them, records principal dependencies and assumptions, and links 40 restricted implementation sectors. These links do not assert that a general theorem has been mechanically verified.

One mathematical boundary is now explicit. Proposition 72 requires at least one spatial coordinate. In the mass-only case, a mass-preserving perturbation must be zero, so the old unrestricted wording did not state the necessary dimension restriction. The worked two-spatial-coordinate examples are unaffected. The remaining 86 statement-and-proof passages are unchanged.

The replay runner now binds a continued batch to the same source files, fixed example inputs, script order and execution environment. The old runner could reuse a successful prefix after files changed. A local temporary-folder regression reproduces that gap, and the revised runner rejects it. This does not show that historical runs were incorrect.

The exact rational parser now rejects zero-denominator strings with a validation error. They already failed previously through division by zero. This is a cleaner failure boundary, not a repair of a false accepted witness.

# 11. What this frozen release claims

The finite foundations connect exact realization, transfer blocks, predictive closure, known-model completion, restricted observable learning, probability-valid instruments, exact domain witnesses and quantified approximation. The later statistical sector adds a conditional data-to-domain theorem for a supplied observable model.

A stable release need not solve unrestricted nonlinear dictionary discovery, unknown hidden-state learning from arbitrary streams or all-horizon full-record accuracy to state those finite results. It must not present those further research directions as completed.

Edition 0.9.0 is the scope-frozen audit candidate. Its evidence consists of written proofs, executable finite examples, independently replayable supplied certificates, source identity checks and a reviewed dependency/assumption register. No proof kernel, independent external review or production integration is asserted.

The remaining freeze decision is editorial and reproducibility-focused: accept the scoped statement set and its correction record, keep the code and source hashes fixed, and publish under an explicit license choice. New research results belong in a later edition rather than silently extending what this release promises.
