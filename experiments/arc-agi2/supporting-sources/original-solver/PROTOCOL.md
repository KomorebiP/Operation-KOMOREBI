# Block 17 frozen experiment

Author: Komorebi P.

The experiment integrates the live core/Block 2/Block 4 solver and Blocks 6–15 compilers. Block 5 is the shared execution IR. No sealed champion or per-task promotion mask is accepted by the prediction API. The exposed 1,000-task public training corpus is development data; none of these results estimates unseen accuracy.

The primary policy is `typed_recent`: preserve live-base Attempt 1 and select the most recent bank's strongest distinct prediction for Attempt 2. Blocks 14 and 15 share a priority tier, with active descendants superseding their ancestor. Within the tier, distinct compiler lineages vote, then lower recorded complexity wins. These votes are a provenance heuristic, not a proof of statistical independence. The same core exposed by the Block 13 adapter does not override its own larger-budget live base.

Controls frozen before scoring are `base`, `recent_control` (identical dispatch without typed vetoes), `typed_joint` (both slots selected from candidate behaviors before the live base), and `typed_agreement` (source votes precede bank recency). Each output uses two distinct predictions when available. Deterministic hash ties are recorded, not represented as certainty.

The scoped repair applies only to the old multiscale scalar structural codebook. A noninjective learned codebook emits a veto with the colliding keys and program hash. The explicit binary symmetry predicate is outside that veto's scope. A repaired compiler's mere abstention never acts as a veto. This repair was motivated by an already-exposed Block 16 failure, so it is score-seeded development. All policies retain every prediction and are scored without filtering individual outputs.

The inherited core's nominal 8-second setting selects a deterministic operation tier; it is not a wall-clock cutoff. The Block 13 core adapter retains its inherited 2-second tier. Candidate/replay limits are inherited and included in the census. Block 11/12 provisional operators are enabled to expose the full development bank; this is not a new validation of those operators.

The 48-source Block 14–15 census is reused only after checking all source hashes, complete challenge identity and each record's semantic input hash. This is a disclosed compute reuse from Block 16's live replay, not a fresh full-bank compilation. `engine.py scan --include-new` is the independent path that recomputes the complete bank on arbitrary challenge files. Neither prediction path reads test labels.

Evidence has different strengths: modern entrants execute serialized programs through the tournament replay hook; Block 13's inherited interfaces supply recorded exact demonstration executions, without that common hook; earlier native compilers execute their own exact-fit checks, and Block 9 additionally checks native/IR equivalence. The report must preserve these distinctions.

The success criterion is higher autonomous full-corpus coverage than the live base, with the typed veto compared directly against its no-veto control. The G47 retrospective frontier (864/1,076 outputs, 804/1,000 whole tasks) stays immutable. Any new correct cases outside G47 are diagnostic unless separately promoted through an explicitly retrospective protocol.

Before any Block 17 scoring, the first scan was stopped after profiling repeated pure feature-map construction in the inherited Block 13 feature compiler. Its partial checkpoints and source freeze are archived under `evidence/pre_optimization`. The restarted scan adds task-local memoization keyed by array dtype, shape, exact bytes, and feature names. No search space, budget, candidate ordering or learned rule changes. The cache is discarded and original module functions restored after each task. Reference/optimized candidate equality is checked explicitly.

A second pre-score profiling pass added cached feature columns as well as maps and conjunction rows, avoiding repeated conversion of the same nested cell feature in different conjunctions. The intermediate map-only implementation and partial scan are in `evidence/map_cache_only`. This is still exact memoization of unchanged feature values. Candidate equivalence against both earlier implementations is required before scoring.

## Final fixed compute budget

Before any scoring, the full-depth feature-induction run was stopped because its depth-four, width-64 search dominated runtime. Its partial checkpoints are preserved under `evidence/full_feature_depth`. The recorded complete run fixes **only `feature_induction`** at maximum conjunction depth 2, beam width 32 and maximum 32 emitted programs; other compiler limits remain inherited. This is an explicit budget reduction, distinct from the semantics-preserving cache optimization. It is not claimed to reproduce the deeper bank's candidate set. The source freeze and each feature-compiler receipt record these values. On the inspected profiling input, this budget emitted 13 behaviors versus 19 at the deeper budget, without opening labels. Selection policies remain unchanged.

The final live-core budget is also fixed at nominal tier **2.0**, matching the inherited Block 13 core adapter: depth 4, beam 48, 2,200 composition expansions, at most 16 exact composition candidates, 28 operations per stage, completion width 1 and repeat limit 30. The initial live-core tier 8.0 (8,000 expansions) is retained only in the archived `evidence/core_high_tier` partial experiment. This pre-score adjustment changes the live-base compute budget. No score comparison between the uncompleted high-tier run and the final run is claimed. Both live-core entry points use the same tier in the reported experiment; the `core_search` duplicate does not override its own base under the primary policy.

## Additional pre-score trace-support control

Inspection of candidate evidence, without opening any test labels, motivated one additional control: `typed_supported`. It is identical to the primary `typed_recent` policy except that a Block 13 feature-table candidate must report zero unseen test feature keys. Otherwise that control records `abstained_unknown`. This is a lack-of-support decision, not a claim that the candidate is disproved. It does not apply a universal leave-one-out veto. The primary policy is unchanged. The earlier five-policy source snapshot remains under `evidence/dispatch_before_trace_control`; the final pre-score source freeze includes all six policies. This dispatch-only addition does not change the ongoing compiler census or its code hash.
