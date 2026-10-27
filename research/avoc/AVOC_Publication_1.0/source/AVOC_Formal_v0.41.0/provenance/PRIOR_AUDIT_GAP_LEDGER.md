# AVOC v0.14.0 — audited gap ledger

The status describes the exact named objective, not all imaginable extensions. No completion percentage is assigned.

## G01. Task-relative information and collision calculus

**CLOSED_RELEASE** — `Core, Refinement, OpenWorldRefinement`

Factorization, fiber tests, joins, strict finite collision descent are proved.

**Boundary / next step:** No claim that useful features or decoders are cheap to discover.

## G02. Finite Bayesian updating and evidence algebra

**CLOSED_RELEASE** — `Bayesian, BayesianEvidence, BayesianLaws`

Normalized rational posterior and predictive laws, total fallback, product conditioning, martingale identities.

**Boundary / next step:** A supplied likelihood model is not a measured or automatically correct model.

## G03. Blackwell forward comparison

**CLOSED_RELEASE** — `Blackwell, StochasticBlackwell`

Garbling implies ideal decision-value dominance.

**Boundary / next step:** The converse characterization of garbling from dominance over all decision problems is not proved here.

## G04. History-to-state exact sufficiency

**CLOSED_RELEASE_CONDITIONAL** — `HistoryState`

Independent recursive values agree for the declared Markov compiler.

**Boundary / next step:** History reward and predictive laws are defined using that compiler. Real transcript sufficiency is not inferred.

## G05. Likelihood archival replay

**CLOSED_RELEASE_CONDITIONAL** — `ArchiveReplay, HistoryArchive`

Positive-evidence history replay recovers the posterior, at later resolutions of the same fine world space.

**Boundary / next step:** Not certification-log replay, raw-file authenticity, new latent worlds, or optimal retention cost.

## G06. Finite stochastic approximation

**CLOSED_RELEASE_CONDITIONAL** — `ApproximateStochastic, ApproximateComposition`

L1 reward/transition error gives explicit value and action bounds; error ledgers compose.

**Boundary / next step:** Older finite-state/global-action interfaces must be linked to the new guarded system.

## G07. Combined Bayesian perturbation with no intermediate evidence floor

**CLOSED_AUDIT_COROLLARY** — `AuditBridges.combined_stability_endpoint_only`

The existing normalization lemma yields 2(beta+K alpha)/zeta with one endpoint floor and positivity of the other endpoint.

**Boundary / next step:** Does not turn posterior error into arbitrary research-transition or Q error.

## G08. Exact scalar and full-Q finite coding

**CLOSED_RELEASE** — `ExactRateDistortion*, QRateDistortion*`

Attained minima, scalar greedy optimum, Q midpoint reconstruction, regret and margin consequences.

**Boundary / next step:** Minimum full-Q reconstruction is not minimum action-only memory. No general efficient Q-cover solver or token count.

## G09. Decision-only fiber criterion

**CLOSED_AUDIT_COROLLARY** — `AuditBridges.decision_decoder_iff_common_good_action`

A decoder exists iff every code admits an action good for all source states in its fiber.

**Boundary / next step:** The minimum-cost/code-number optimizer for this weaker objective remains to be developed.

## G10. Semantic bottleneck and verifier-risk inequalities

**CLOSED_RELEASE_CONDITIONAL** — `Specification, VerifierRisk*`

No decoder repairs an erased semantic distinction; risk cover/factorization/floor implications are proved.

**Boundary / next step:** A lower floor needs S subset W. Factorization and semantic fidelity remain explicit premises.

## G11. Fixed-DAG readiness and certified scheduling

**CLOSED_RELEASE** — `Scheduling*`

Ideal/frontier/batch laws, legal schedules, structural completion, width/work bounds, certificate-gated insertion.

**Boundary / next step:** No guarantee of proof-search success, dynamic AND/OR tasks, or optimal real worker allocation.

## G12. State-dependent Bayesian controller with queue and budget

**CLOSED_RELEASE** — `ResearchController, ResearchPolicy, GuardedControl`

Bayesian action selection, readiness, actual proof admission, queue and budget are integrated.

**Boundary / next step:** It is no longer correct to list this integration as wholly missing.

## G13. Whole adaptive-policy optimality and Q/planner regret

**CLOSED_RELEASE** — `GuardedControl, GuardedPolicyRegret`

Optimal deterministic adaptive finite-horizon plan exists; whole-policy loss bounded by sum(2 eta+tau).

**Boundary / next step:** True feasible Q-errors are inputs. This is not the complete physical-model/deployment theorem.

## G14. Separate Q-model and Q-compression error ledger

**CLOSED_AUDIT_COROLLARY** — `AuditBridges.composed_policy_regret`

Two justified Q-error budgets add before application of whole-policy regret.

**Boundary / next step:** No empirical or Bayesian-to-Q calibration is manufactured by the triangle inequality.

## G15. Arbitrary suggestions plus exact guard preserve formal safety

**CLOSED_AUDIT_COROLLARY** — `AuditBridges.shielded_suggestions_preserve_certification_and_budget`

Use suggested action if Allowed, else stop; all branches remain BudgetSafe.

**Boundary / next step:** The exact guard requires full safety metadata somewhere; rejecting everything is safe but need not perform well.

## G16. Guarded compression/history/replay adapters

**OPEN_INTEGRATION** — `Guarded.System versus older interfaces`

Some elementary transport is direct; dynamic feasibility, certificate identity, and state-dependent experiments need explicit maps.

**Boundary / next step:** Prove a guarded abstraction contract and port only genuinely needed preservation results.

## G17. Posterior/model error to feasible Bellman-Q error

**OPEN_MATHEMATICAL** — `ApproximateBayesian versus GuardedPolicyRegret`

Small belief L1 is not small L1 between distributions on next belief states. Arbitrary rewards/experiments can be discontinuous.

**Boundary / next step:** Specify regularity and an appropriate coupling/Wasserstein or finite-observation continuation bound.

## G18. Exact candidate-to-receipt and semantic identity binding

**OPEN_IMPLEMENTATION** — `Protocol.check_sound, State.pending, step`

The current attempt stores only a pending task ID; verification consumes a new modeled receipt.

**Boundary / next step:** Bind task, exact statement, dependencies, environment revision and actual artifact to a checked receipt; preserve provenance.

## G19. Fallible empirical claims alongside proof-carrying claims

**OPEN_INTEGRATION** — `Sound Protocol versus VerifierRisk`

The sound core and fallible probability model are separate.

**Boundary / next step:** Use typed empirical/admitted states, bounded harm, and an explicit coupling to sound proof admission. Never equate high posterior with proof.

## G20. Costed computation of the controller and context

**OPEN_MATHEMATICAL_AND_IMPLEMENTATION** — `noncomputable optimalAction; exact Q-code definitions`

Declared research fees omit an automatic cost model for solving Bellman, computing Q, decoding and certifying context.

**Boundary / next step:** Provide an executable approximate planner and cost its metareasoning, context construction, retrieval and verification.

## G21. Real-system identification and effectiveness

**OPEN_EMPIRICAL** — `All declared models`

No real LLM calibration, proof-search distribution, token distortion, objective alignment or productivity gain is established by this audit.

**Boundary / next step:** Estimate and validate inputs on held-out tasks with matched total resource budgets.

## G22. Artifact capital, general queue laws, multi-agent allocation

**OPEN_SPECIALIZATION** — `Generic Guarded system can host richer finite alphabets`

Concrete protocol only instantiates attempt/verify/stop; queue is already present.

**Boundary / next step:** Add explicit investment/retrieval/repair operations and prove model-specific dominance or allocation results.

## G23. Dynamic AND/OR tasks, retractions and concurrency

**OPEN_MODEL_EXTENSION** — `Fixed partial order and sequential control`

No changing proof routes, proof applicability invalidation or concurrent resource semantics.

**Boundary / next step:** Extend task semantics and reprove dependency/certificate invariants; do not assume all retractions retract mathematical truth.

## G24. Broader horizon, robustness and randomized theories

**OPTIONAL_EXTENSION** — `Current finite deterministic-policy and fixed-latent models`

Discounted infinite horizon, full randomized constrained comparison, robust misspecification and new latent worlds remain outside scope.

**Boundary / next step:** Prioritize only when demanded by a concrete use case; they are not required to use finite-horizon assurance.
