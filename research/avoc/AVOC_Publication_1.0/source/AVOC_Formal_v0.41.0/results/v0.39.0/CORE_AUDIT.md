# v0.38 core audit for the calibration continuation

Audit date: 2026-09-19. This is a source-level independent subagent review of the inherited statements and definitions. Compilation, axiom reports, and executable results are separate evidence. No inherited source was edited by this review.

## Claim and verdict

Normalized claim: for one fixed quote model `md`, one fixed `Realization md`, and the upper-setup reservation action guard and state transition encoded by `trueSystem md r`, quote-derived bounds enclose finite-horizon Q/value functions and bound the expected regret of the complete fixed-model robust policy. Accepted checked runtime transitions preserve the stated safety/coherence predicates. Durable acknowledgement preserves those predicates and is exactly idempotent.

Primary verdict: **conditional on a named input**. The input is a fixed compatible exact realization, including supplied deterministic quote bounds and success probabilities. The proofs reviewed support this normalized claim. They do not prove calibration, changing-model regret, or comparison with a less conservative feasible set.

## Dependency graph

1. `QuoteAuthority.ExactQuote` membership assumptions provide reward and observation-law error bounds.
2. `RobustQuote.nominal_certificate` transports those errors through the inherited guarded Bellman model certificate.
3. `value_error`, `local_q_error`, and `q_between` give certified intervals.
4. `robustChoice_lower_max` and those intervals give a uniform Bellman action gap.
5. `robust_policy_nearGreedy` establishes that gap at every branch of one fixed-system policy tree.
6. `Guarded.plan_regret_le` telescopes expected policy loss over the complete horizon.
7. The runtime separately verifies exact identity, affine artifact correctness, interval membership, admissibility, budget conservation, and artifact/evidence coherence.
8. Recovery separately replays the pure checked transition, compares durable views, and returns the existing checkpoint unchanged for a recognized duplicate.

The bridge between statistical data and premise 1 is new work. Runtime/storage authenticity remains an implementation boundary.

## Obligations and findings

| Obligation | Status | Decisive source and consequence |
|---|---|---|
| Quote membership implies Q/value enclosures | Passed by source inspection | `AVOC/RobustQuotePlanning.lean`, `nominal_certificate`, `value_error`, `local_q_error`, `q_between`. |
| Complete-policy telescoping | Passed by source inspection | `robust_policy_nearGreedy`, `robust_policy_regret`, and `AVOC/GuardedPolicyRegret.lean`, `plan_regret_le`. The bound concerns expected model reward. |
| Arbitrary compatible exact-cost feasibility | Not addressed | `RobustQuotePlanning.lean:56`, `trueSystem`, sets both actions and step from `nominal md`. Costs are reserved at upper endpoints. |
| Mid-episode probability updates | Not addressed | `robustPolicy` and `robust_policy_regret` fix one `md` and one `r` across every branch. Quote updates change the system and require an additional theorem or a frozen-episode restriction. |
| Useful dominance with positive selected radius | Failed as a feature of the old checker, not as theorem soundness | `certified_dominance` and `RobustQuoteCodec.dominatesCheck` include the selected action itself. Thus `Qhat+rho <= Qhat-rho` forces `rho=0`. |
| Deterministic artifact refinement | Passed by source inspection | `RobustQuoteRuntime.BoundedArtifact.refined` creates exact setup/gross evidence and retains the probability band. |
| Automatic replanning from refined deterministic evidence | Not addressed | Runtime stores the evidence but keeps its original `md`; confirmation uses `LazyStaged.step (nominal md)`. There is no budget refund or model replacement. |
| Quote mutation after an authentic fixed intent | Passed under the stated provenance invariant | `RobustQuoteRecovery.acknowledge` compares the intent evidence with supplied current evidence. |
| Authority authenticity for arbitrary fabricated intent/current-evidence pairs | Not addressed | Acknowledgement does not itself require either supplied record to equal `evidence md`; the caller must preserve the invariant that the intent was produced by `prepare` and current evidence is authoritative. Hostile record substitution is outside the retained storage boundary. |
| Fresh outcome-tag validation | Passed by source inspection | The fresh acknowledgement path compares `out.tag` with the committed tag. |
| Duplicate acknowledgement revalidates supplied outcome tag | Not addressed by design | The recognized duplicate branch returns the old checkpoint before consulting `out.tag`. Idempotence is sound, but blanket claims that every incompatible tag is rejected need the fresh-acknowledgement qualification. |
| Kernel-checked concrete changed selector/dominance examples | Incomplete relative to the earlier detailed task specification | `RobustQuoteExamples.lean:212-234` proves radii 208/0 and bare rational inequalities, not the concrete selector equalities. Concrete choices and dominance examples are executable bounded evidence. |

## Small separating examples

The conservative feasible-set distinction is substantive. With initial budget 1, warm setup interval [1,2], warm gross 3 and success probability 1, upper-setup reservation excludes warm inspection. A two-step exact-cost controller with realized setup 1 can inspect and deploy for net value 2. The inherited benchmark reserves 2 and therefore has value 0. The theorem compares against the latter benchmark.

The documented uncertainty example has warm setup 0, gross 200 and success probability in [3/5,1], while cold gives exact gross 60 with success probability 1. At total horizon two, warm's true value is in [120,200], so warm beats cold in every compatible realization. The coarse radius method nevertheless chooses cold because its certified surrogate is -88 versus 60. This is a valid conservative lower-bound selector with a loose regret certificate, not an exact maximin solver. The new documentation should not imply minimax optimality without a dominance certificate.

## Corrections implemented in the new bridge

`AVOC/CalibrationBridge.lean` adds a competitor-only dominance predicate and executable checker. Its soundness proof handles the self case by reflexivity and distinct competitors by interval bounds. It also proves that the inherited self-comparison forces the selected radius to zero.

The bridge replaces only probability fields while preserving identity, source, workload, and deterministic bands. On a simultaneous probability-coverage event and supplied deterministic memberships, it constructs the exact compatible realization needed by the inherited theory. Its `FrozenEpisodeGuarantee` explicitly fixes the resulting model and realization throughout one episode and retains the conservative reservation benchmark.

## Strongest safe release wording

Finite-sample calibration provides a probability, over the calibration data under a specified sampling law, that both true success probabilities belong to the new bands. On that event, with deterministic quote memberships also supplied, the frozen-episode Bellman bounds, admissibility, and expected whole-policy regret theorem apply. This does not provide a per-run realized-reward bound, a data-free calibration guarantee, or a guarantee across online model updates.

The bridge compiled with warnings as errors against the freshly rebuilt inherited imports. Its 17 explicit theorem declarations have exact-name axiom reports, each using only `propext`, `Classical.choice`, and `Quot.sound`. Evidence: `CalibrationBridge.json`, `CalibrationBridge_AxiomAudit.json`, `CalibrationBridge_AxiomAudit.log`, and `CalibrationBridge_declarations.json` in this directory.

The final prose and mathematical notation in the new bridge and this note were self-reviewed with the mathematical proofreading checklist. No substantive proof change arose from that proofreading pass. The source-level audit remains distinct from the broader release audit.

Cheapest remaining behavioral check: a positive-radius dominance case that fails the inherited self-comparison and passes the corrected competitor-only test.
