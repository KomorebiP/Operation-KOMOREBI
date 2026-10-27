# Continue from AVOC v0.15.0

Read `FORMAL_THEORY.md`, `PROOF_BOUNDARY.md`, `GAP_LEDGER.md`, `AUDIT.json`, and `results/VERIFICATION_v0.15.0.md` before continuing. The input is the frozen v0.15 source release, not an assumed persistent runtime.

## Current result

734 theorem/lemma declarations, 55 new in seven modules, all freshly compiled and axiom-audited. The 68 inherited non-audit modules remain byte-identical to v0.14. The old audit's nine separate corollaries are not silently included in this count.

The missing model-error-to-Q bridge is now supplied for an explicit class. Prior L1 and observation-channel row L1 control joint world/observation error. Probability-weighted posterior error is at most twice joint error, including impossible observations, without an evidence floor. Bounded belief-Lipschitz approximate tables, exact metadata and action-guard matching, quantified encoding error and model Bellman residuals yield constrained Q error. The existing controller then supplies whole-policy regret and certificate/budget safety.

Main declaration: `Komorebi.AVOC.Research.certified_bayesian_model_policy`.

## Preserve these boundaries

- Average posterior stability is not pointwise posterior stability.
- Belief L1 does not imply small L1 between Dirac laws on next belief states.
- Matching action guards and metadata are exact hypotheses, not consequences of numerical belief similarity.
- Backup residuals are model-level approximation obligations, not automatically small or cheap to certify.
- The reference system is a declared mathematical model, not a proven identification of a production LLM.
- The sound proof gate still uses supplied soundness and modeled receipts.
- Python regression is independent finite evidence, not formally extracted code.
- Do not advertise every mathematical helper as an independent discovery.

## Highest-value next direction

Address audit G18: bind an attempted candidate to exact statement, dependency/environment revision, immutable artifact bytes, and the subsequent checker receipt. The current inherited pending set stores task IDs only. Separate byte/identity binding from the soundness and semantic-fidelity obligations. Preserve the existing controller proofs and create an explicit refinement/adapter rather than relabeling a modeled receipt as an authenticated proof file.

Alternative research direction: a costed executable value-table planner with checkable residuals, followed by the new derived-Q guarantee. Do not reopen G17 as wholly missing; extend the stated compatibility class only where necessary.

Use the commands in `REPRODUCE.md`. No asynchronous job is promised or running on behalf of this handoff.
