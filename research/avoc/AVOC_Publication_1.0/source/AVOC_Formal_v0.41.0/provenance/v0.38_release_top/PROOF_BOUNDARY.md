# AVOC v0.38.0 — exact proof and execution boundary

## Kernel-checked in this release

1. Exact authority-bound identities for warm/cold quotes, protected affine source, call count, cost model, provider, checker, environment, and schema.
2. Well-formed exact natural/rational/probability bands and exact decoded-record quote validation.
3. Rejection of identity, setup-band, gross-band, and probability-band substitutions.
4. Compatible exact warm/cold realizations and a conservative nominal staged model.
5. Reward and binary observation-law error bounds derived from the quote-band widths.
6. Finite-horizon lower/upper Q and value bounds for every compatible exact realization.
7. State-dependent admissibility of the lower-Q robust selector.
8. Certified dominance: one action's lower Q above every competitor's upper Q implies true optimality in every compatible model.
9. Complete adaptive-policy regret bounded by the sum of certified per-stage gaps.
10. Exact singleton collapse of all radii and recovery of the v0.37 recommendation under the same tie-breaking rule.
11. Proof-carrying selected artifacts whose exact setup/gross values lie in the authorized bands.
12. Deterministic setup/gross refinement to singleton bands while retaining the probability band unchanged.
13. Executable transition equality with the declarative transition.
14. Infrastructure fault is not a model report and cannot advance the runtime state.
15. Selected-only installation and exact preservation of the unselected artifact and evidence.
16. Budget, coherence, source, and proof invariants across accepted transitions.
17. Quote evidence included in durable intent/commit identity.
18. Rejection of quote mutation, state mutation, sequence mutation, and incompatible outcomes at acknowledgement.
19. Idempotent duplicate acknowledgement without duplicated spending, evidence, artifacts, or sequence advancement.
20. Unfinished intent is non-evidence and is not silently retried.

## Executed bounded evidence

- Exact Python `Fraction` oracle: 21 Lean planning comparisons and 1,523 compatible exact-realization checks.
- Selected-only normal workflows: warm path with missing cold artifact; cold path with missing warm artifact.
- Transactional commit-before-ack recovery: retained selected artifact, no duplicate selected-operation call, exact duplicate resume.
- Inherited v0.37 lazy staged regression: warm, cold, invalid-boundary, and crash-recovery cases rerun.
- Complete local source build: 205/205 targets from an empty local build directory, including aggregate `AVOC.lean` and all executable Lean entrypoints.
- Exact-name theorem audit: 2,044/2,044 declarations.
- Negative suite: 111/111 substantive rejections through the project environment.

These executions support the implementation.  They do not replace the general Lean proofs.

## Supplied assumptions and explicit non-claims

1. **Quote calibration.** Interval endpoints and success-probability coverage are supplied model evidence.  Formal well-formedness does not establish empirical calibration.
2. **Compatible-model guarantee.** Robust optimality and regret apply to exact realizations lying inside the authorized intervals.
3. **Affine backend.** The executable artifact examples use exact GF(5) affine programs and the existing checked factorization backend.  This is not arbitrary Lean/mathlib artifact execution.
4. **Physical cost.** Setup, gross saving, call count, and control reward are declared exact model data.  Parsing, process startup, storage, rational bit complexity, and all physical resource costs are not fully priced.
5. **Probability refinement.** A successful artifact refines deterministic setup/gross facts only.  It does not calibrate success probability without a separate observation model.
6. **Fault semantics.** The interface chooses not to treat infrastructure fault as scientific/model evidence.  This is not a theorem that every real infrastructure event is uninformative under every joint model.
7. **Storage/runtime trust.** Python, SQLite, filesystem, OS, installed Lean compiler/kernel, and pinned dependency caches remain trusted implementation boundaries.  The workflow tests controlled process interruption, not electrical power loss or hostile rollback.
8. **No automatic retry.** Unfinished intents are blocked.  The older paid retry/cancel protocol was not ported into this new quote workflow.
9. **No universal Python/SQLite refinement.** The formal transition and recovery functions are proved; the adapter is independently tested, not universally derived from the Lean state machine.
10. **No real-LLM claim.** This release does not establish calibrated LLM success rates, scientific productivity gains, autonomous research, or universal optimal AI use.
11. **No historical novelty claim.** Bellman control, interval bounds, and robust decision rules have broader prior literature.  This release claims the checked AVOC integration stated here.
12. **External dependencies.** The local project was rebuilt against nine exact pinned dependency caches.  Mathlib and Lean were not rebuilt from all source, and no independent kernel implementation was used.
13. **Lake frontend interruption.** Several redundant `lake build` frontend runs hit the host's long-command limit and are not counted as evidence.  The fail-closed evidence is the complete 205-target direct project rebuild, including `AVOC.lean`.

## Provenance boundary

v0.37 is the sole authoritative verified predecessor.  Its source lineage records reconstruction from complete v0.35 source plus retained v0.36 specification because a complete v0.36 source archive was unavailable.  No missing v0.36 source is treated as independently verified.
