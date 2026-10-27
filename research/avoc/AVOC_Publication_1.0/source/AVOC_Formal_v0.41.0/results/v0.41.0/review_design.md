# Independent design review — AVOC v0.41

Primary verdict at design stage: **incomplete, with the whole-run refinement and optional-planner implication still to be proved.** No contradiction was found in the proposed target. The physical interpretation remains conditional on the named source-generative model.

## Normalized target

For arbitrary finite identities with decidable equality, arbitrary finite per-identity Boolean sources, and arbitrary finite command histories, a successful source-generative run beginning at the empty registry produces a well-formed global operation-ID registry and terminal log. Its projection executes successfully in the raw lifecycle recorder, every recorded success/rejection consumes exactly the next source bit of the matching identity once, and the terminal samples equal those of a derived reveal trace. Faults, exact retries, and late matching intents consume no bit. Bad command histories and globally pending runs cannot issue a new plan. Composing this pointwise equality with the existing finite scheduled calibration yields only an unconditional bad-issuance bound.

This is a fresh protocol. The historical CalibrationLog.record and tools/calibrate_quote.py store an unfinished intent as an immutable event; changing that event to a terminal result with the same ID conflicts. The new lifecycle recorder must not be described as a refinement of that complete historical protocol. It may use CalibrationLog.record on its separate terminal-only projection.

## Critical test obligations

1. Global operation IDs: begin(0,A), begin(0,B) with A != B rejects.
2. Exact terminal replay: begin(0,A), report(0,A), report(0,A) has one sample and consumes one source bit, including when the second source bit differs.
3. Terminal kind conflict: begin/report/fault and begin/fault/report reject.
4. Key conflict: any late begin, report or fault with the same ID but different key rejects.
5. Late intent: begin/report/begin with matching ID/key remains completed and consumes one bit.
6. Unknown terminal: report or fault before begin rejects.
7. Empty source: begin/report with an empty identity source rejects. A failed report must not silently release pending or manufacture a count.
8. Whole-run error: a valid prefix followed by one invalid command yields no plan. The optional planner must not salvage the prefix or mask the failed transition.
9. Global pending gate: a completed selected identity plus an unrelated pending identity blocks issue.
10. Both checked outcomes count: a source [false,true] yields two observations; rejection is not censored.
11. Source independence scope: raw recorder accepts caller-supplied binary terminal labels, but the generative machine produces labels from its source. Refinement of the latter cannot certify arbitrary externally supplied labels.
12. Boundary: zero commands and zero-sized checkpoints may issue only with an empty pending registry; no completion-rate guarantee follows.

## Dependency graph

Raw recorder transition rules -> reachable well-formedness, terminal-only CalibrationLog projection, global pending gate.

Generative source transition -> whole-run raw command projection and reveal trace equality -> actual terminal-log prefix equality -> available checkpoint faithfulness -> existing source-law and finite-schedule calibration -> optional frozen-policy coverage.

The source ConditionalLaw, protected complete event stream, exact identity meaning, fixed schedule, prescribed parameter strata, and deterministic realization memberships remain supplied inputs. No empirical stationarity, authentication, physical spend identity, universal Python refinement, or completion-conditioned coverage follows.

## Initial source inspection

Read AVOC/CalibrationLog.lean, ObservationReveal.lean, ObservationPolicy.lean, ObservationStream.lean, the inherited calibrate_quote.py parser, and the initial ObservationRecorder.lean implementation. The raw step definitions implement the intended lifecycle branches. Their definition permits arbitrary input states; universal reachable-state claims must start at initial or assume WellFormed. Exact terminal replay need not require a pending intent, because completion removed it already. The apparent exception is necessary and safe from a well-formed reachable state.
