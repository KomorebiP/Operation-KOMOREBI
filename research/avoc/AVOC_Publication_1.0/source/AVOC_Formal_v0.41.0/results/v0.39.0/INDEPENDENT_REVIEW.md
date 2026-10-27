# Independent mathematical and implementation review

## Normalized claim and primary verdict

**Primary verdict: conditional on a named input.** For rational true probabilities, exact finite probability spaces, and a supplied binomial marginal count law at every fixed checkpoint, the finite schedule has simultaneous failure mass at most its sum of allocated alpha values. An arbitrary outcome-dependent selector among those checkpoints preserves that bound. The integrated `learned_episode_coverage` theorem uses supplied deterministic quote membership to give mass at least `1 − Σ alpha` to existence of a compatible realization with the specified warm/cold probabilities, exact setup/gross values from the supplied deterministic realization, and the inherited fixed-episode robust planning guarantee. The reviewed sources support this conditional statement. No blocking mathematical error was found in these statements.

The finite binomial mass inequality itself is proved as written, without a sampling-law assumption. Its interpretation as coverage of operation logs is conditional. This review does **not** promote it to empirical authentication, an IID derivation from physical logs, unrestricted optional stopping, arbitrary real probability parameters, changing-model policy regret, or universal Python/Lean refinement.

This is an isolated subagent review of raw source and fresh exact computations, not acceptance of the author's verdict. Source files were read without edits. The only file written by this reviewer is this report. A separate release audit must establish compilation, declaration axioms, negative-test quality, and reproducibility against the final source hashes. This report is not a substitute for those gates.

## Claim card

- Domains: `n,k,m : Nat`, true probability `p : ℚ`, with `0 ≤ p ≤ 1`; grid size `m > 0`. The miss-mass theorem allows any `alpha ≥ 0`; meaningful reported confidence additionally uses `alpha < 1`.
- Count distribution: `choose(n,k) p^k (1-p)^(n-k)`, summed for `k=0,...,n`.
- Interval: hull of all uniform cells whose product envelope is strictly larger than `alpha/(n+1)`; empty retained sets return `[0,1]`.
- Schedule: finite index type, fixed sample sizes, grids, error allocations and stratum probabilities. Counts can be correlated across checkpoints. Each individual count must have the stated exact binomial marginal.
- Selection: any function from the whole finite outcome space to one of the scheduled indices. Selection can inspect all observed information. It cannot change the family for which the marginal hypotheses and total error allocation were established.
- Planning: one fixed quote model and one compatible realization for an entire episode; deterministic setup/gross membership is supplied. The benchmark uses the nominal upper-setup reservation guard.
- Runtime: a protected immutable summary snapshot is supplied. Exact replay and filtering are implemented. Authentication, log completeness/order, status validity and noninformative exclusions are external assumptions.

## Dependency graph

1. Internal algebra: `mass_nonneg`, `mass_sum_one`.
2. Internal order geometry: `grid_covers`, `mass_le_envelope`, `retained_cell_in_hull`.
3. Internal exclusion implication: parameter outside the interval implies count mass at most `alpha/(n+1)`.
4. Internal finite sum: summing the excluded masses over at most `n+1` counts gives `missMass_le`.
5. **Supplied leaf:** each operation-count statistic has the binomial fiber masses in `count_law`.
6. Internal pushforward: `statistic_eventMass`, `binomial_failure_eq`, `binomial_failure_le` transfer the algebraic inequality to that law.
7. Internal finite union and event inclusion: `scheduled_binomial_failure_le`, `selected_binomial_failure_le`, `selected_binomial_coverage`.
8. **Supplied leaves:** deterministic quote membership and learned-band membership at the selected realization.
9. Internal constructors and deterministic bridge: `learnedBand`, `calibratedRealization`; inherited robust Q/value and whole-policy regret theorems establish `calibrated_frozen_episode_guarantee`.
10. Integrated event inclusion: `learned_episode_coverage` maps simultaneous count coverage into `EpisodeCertified` with mass at least `1 − Σ alpha`. Both selected indices use the same schedule, so no second factor of two or duplicate alpha spending is needed.
11. Runtime boundary: Python builds the same interval formula and a fresh request. Agreement with Lean is tested on finite cases, not proved as a compiler/runtime refinement.

There is no circular coverage premise in steps 1–4. The law is introduced explicitly at step 5. The planner uses learned probability membership at step 8; it does not establish that membership itself.

## Obligation matrix

| Obligation | Status | Finding |
|---|---|---|
| Excluded parameter implies small count mass | Passed | A cell containing `p` cannot be retained; its envelope bounds the mass. |
| Finite-sample miss mass at most alpha | Passed | Every excluded count contributes at most alpha divided by `n+1`; no union independence needed. |
| Boundary parameters and no data | Passed | `p=0,1` and `n=0` are included. With the executable alpha restriction, no data yields `[0,1]`. |
| True parameter need not lie on grid | Passed | `grid_covers` covers every rational parameter in `[0,1]`. |
| Arbitrary real true probability | Not addressed | Theorems quantify `ℚ`, not `ℝ`; no real-extension theorem was reviewed. |
| Binomial marginal from IID observations | Conditional | The exact marginal is an explicit hypothesis. No IID sequence/product-law derivation appears here. |
| Finite correlated schedule | Passed | The finite union bound uses only the individual marginals. |
| Arbitrary selection within the fixed family | Passed | Selected failure is contained in the union of scheduled failures. |
| Data-dependent invention of new schedule | Out of scope | The parser cannot prove registration preceded the sample. |
| Frozen episode planning | Passed, conditional on membership | The model and realization are fixed; deterministic membership remains supplied. |
| Integrated learned-band episode coverage | Passed under named law/parameter assumptions | The simultaneous event supplies both selected memberships and a compatible realization. |
| Cross-episode or mid-episode adaptive regret | Not addressed | The inherited fixed-model bound does not prove this. |
| Competitor-only dominance | Passed | Equal action is discharged by reflexivity; distinct action uses upper-to-lower comparison. |
| Exact replay and conflict rejection | Passed for stated abstract log | Event equality gives idempotence and operation-ID collision rejects. |
| Fault/unfinished sample exclusion | Passed | They contribute no Boolean observation; no physical sampling conclusion follows. |
| Evidence authentication and scientific validity | Conditional | A status label or evidence identifier is not a checked artifact proof. |
| Python/Lean formula correspondence | Passed by source comparison; bounded executions only | Uniform-cell formulas, strict threshold comparison and hull fallback agree. |
| Python/Lean lifecycle refinement | Not addressed | Abstract Lean events and Python immutable summaries are not connected by a universal refinement theorem. |

## Independent reconstruction of the critical implication

Fix `p` in a cell `[i/m,(i+1)/m]`. Both factors are nonnegative, and

`p^k ≤ ((i+1)/m)^k`,

`(1-p)^(n-k) ≤ (1-i/m)^(n-k)`.

Multiplying by the nonnegative binomial coefficient proves the envelope bound. If the interval hull excludes `p`, this containing cell cannot be retained; otherwise the hull would contain it. The cell envelope is therefore at most `alpha/(n+1)`. Consequently each excluded count has mass at most that threshold. Summing the `n+1` possible counts proves the claimed miss-mass inequality. Strict retention and non-strict exclusion have compatible boundary directions. Returning `[0,1]` when no cell is retained introduces no excluded parameter.

For a finite schedule, failure at a selected index implies failure at some scheduled index. Pointwise indicator domination and the finite union bound prove the allocation sum. No checkpoint independence is introduced. To interpret the algebra as operation-sampling coverage, the exact fiber-mass hypothesis must hold; syntactically valid logs do not establish it.

The composition with planning is deterministic: on the event that both relevant probabilities belong to their learned bands, `calibratedRealization` constructs a compatible realization using those memberships plus supplied setup/gross memberships. The existing Q/value and policy-regret theorem then applies. The new `CalibratedPolicy.learned_episode_coverage` theorem performs this event-level composition explicitly. The fixed parameter equalities `hwparam` and `hcparam` prevent adaptive selection from changing the warm/cold true probabilities. The final conclusion `EpisodeCertified` is existential in the compatible realization but explicitly pins its probabilities and all four deterministic setup/gross values to the supplied true values. Its witness is constructed from `d`; it is not an arbitrary cost model substituted for the supplied realization.

## Source and runtime findings

1. **Counter accounting is internally consistent.** Python excludes exact duplicate summaries before all status counts and sample extraction. `successes` uses the first `n` unique checked reports. `selected_stratum_status_counts` describes all unique records in that stratum, including reports beyond the checkpoint; it is deliberately not the `n`-prefix histogram. `checked_reports_beyond_checkpoint` makes this difference visible.
2. **Operation ID is the replay key.** Reusing an operation ID with a changed evidence identifier, status or identity is rejected. Reusing an evidence identifier with a fresh operation ID is not itself a conflict. Trust that operation identifiers designate distinct real operations is an input assumption.
3. **An immutable snapshot is not a lifecycle journal.** Appending terminal success for an operation already present as an `intent` conflicts. The README correctly requires an external durable system to reconcile and produce a new protected summary snapshot.
4. **Fault exclusion needs a statistical assumption.** The proof that a fault contributes no sample is an accounting fact. If faults censor latent failures preferentially, checked outcomes need not estimate all-attempt success probability. The README explicitly discloses this distinction.
5. **Identity is logical, not authenticated.** Exact decoded record comparison prevents accidental mixing inside a supplied request. It does not prove a purported authority was fixed before sampling, the log is complete, or its success/rejection labels were generated by the claimed checker.
6. **Fresh planning is conditional on actual freshness.** The Python adapter blocks replanning if an unresolved intent appears anywhere in the supplied snapshot. A false or incomplete snapshot can hide an unresolved operation. `refresh false` and absence of supplied `intent` labels are not an independently verified storage-state observation.
7. **Probability bands are replaced, not intersected with previous bands.** This avoids silently inheriting an unproved old-band coverage premise. Setup/gross, source, calls and quote identity remain unchanged in the constructor; changed probability evidence obstructs acknowledgement of the prior exact quote record.
8. **The exact-cost oracle is not the benchmark.** `FrozenEpisodeGuarantee` explicitly retains nominal reservation guards and fixed nominal transitions. It does not compare with a more permissive controller using the true lower setup cost as its feasibility rule.
9. **Original dominance was restrictive, not unsound.** Comparing the selected action's own upper bound with its lower bound forces its radius to zero. The new competitor-only test removes this unnecessary self-comparison and proves the remaining comparisons sound.
10. **Execution-domain caps differ without a formula contradiction.** Python supports at most 2,000 observations and 1,000 cells; the Lean numeric codec permits larger individual `n` but adds a product cap. Equality evidence should be described on the common accepted domain. Both calculate exactly there.

## Fresh computations performed by this reviewer

A standalone Python here-document imported only the production interval/parser functions. It computed probabilities independently by multiplying Bernoulli factors over every binary sequence, without using binomial coefficients or the Lean evaluator.

- **576 coverage cases:** all `n=0,...,7`; grids with `m∈{1,2,3,7}`; alpha in `{1/100,1/3,9/10}`; true probability in `{0,1/13,3/8,1/2,11/13,1}`. Every exact miss mass was at most alpha.
- **Four correlated-schedule checks:** count prefixes at sample sizes `3,5,7`, grids `3,7,7`, alpha `1/20` each. The selector deliberately chose a failing checkpoint whenever one existed and was even allowed to use the true parameter. Enumeration covered all `2^7` outcomes. Failure masses were respectively `11749/62748517`, `2187/2097152`, `0`, and `8928/62748517` at parameters `1/13,3/8,1/2,11/13`, all below `3/20`.
- **Replay/counter checks:** changed evidence ID under an existing operation ID rejected; identical replay preserved all selected status counts and success count; an unresolved intent in the other stratum blocked replanning.
- **Boundary probe:** relabeling every supplied record as success in a newly supplied unauthenticated snapshot was accepted and produced 100 successes. This confirms the explicitly documented trust boundary. It is not evidence of a violated promised authentication feature.

These are bounded implementation checks. They are not a second universal proof or a Lean kernel audit. The source argument above is the independent universal mathematical review.

## Concrete raw-Lean wire defect found and corrected

The initially reviewed raw `tools/CalibrationMain.lean` endpoint accepted an exponent-form numeric token `1e0` as integer `1`. `CalibrationCodec.exactInt` checked the parsed `JsonNumber.exponent`, but pinned Lean JSON parsing normalizes positive exponent syntax via `shiftl`; lexical information is lost. A direct execution of

`["calibration-binomial-v1",1e0,1,10,"1/10"]`

returned exit code 0 and `{"status":"calibrated","n":1,...}`. The Python launcher already rejected this token. The root agent corrected the raw Lean CLI with `hasNonIntegerNumberToken` before `Json.parse`. The scanner tracks quoted strings and escapes so numeric-looking identity text is preserved. The original acceptance was a strict-wire contract defect, not a mathematical or numeric-value defect.

After the corrected codec/Main compiled, this reviewer reran **14 raw pinned-Lean CLI cases**, all passing their expected result:

| Input probe | Expected and observed result |
|---|---|
| Numeric `1e0`, `1E+0`, `1e-0`, `1.0`, `1.0e1`, `1E1`, `1e-1` | Exit 2, lexical numeric-token rejection |
| `true`, `null`, and quoted `"1e0"` supplied as a natural | Exit 2, type rejection |
| Ordinary integer `1` | Exit 0, valid calibration |
| Malformed JSON with duplicate comma | Exit 2, JSON parse rejection |
| Unreduced fraction `"2/20"` | Exit 2, rational-format rejection |
| Valid planning request with escaped quotes/backslashes and decimal/exponent-looking text inside identity strings | Exit 0, accepted |

The direct wire defect is resolved in the final reviewed snapshot below. The test used fresh temporary request files and the pinned Lean `--run tools/CalibrationMain.lean` path, without relying on the Python launcher's lexical filter.

## Exact remaining gap and strongest safe statement

There is no mathematical blocker for releasing the **conditional rational finite-schedule theorem and frozen-episode membership bridge**, once the independent compilation/audit gates pass against the final source.

The smallest missing implication for a claim of automatically calibrated operational guarantees is that the actual authenticated count process has the supplied binomial marginals, with noninformative fault exclusion and a prospectively fixed schedule. That is a scientific/runtime modeling obligation, not something established by parsing a log. A formal IID-to-binomial construction could discharge a mathematical sub-obligation but would still not prove the physical operation model.

The strongest safe release statement is: **under the stated finite rational sampling law and protected-input assumptions, conservative exact bands enjoy a fixed finite-schedule coverage bound, and their simultaneous membership yields the existing fixed-model episode guarantee with supplied deterministic quote membership.**

Cheapest follow-up checks: finish source-hash-matched Lean compilation and axiom/negative audits and preserve these exact limitations in release documentation. The direct wire issue found during review has been corrected and independently retested. A real-parameter extension is needed only if the release claims it.

## Reviewed source snapshot

SHA-256 values identify the exact source contents reviewed. Any change to these files requires an impact check before citing this review as applying to the final release.

| File | SHA-256 |
|---|---|
| `AVOC/FiniteCalibration.lean` | `9ac4af6bb0d4165fe9c178520c3b834b990a3303c6197110a0cf168af99fd483` |
| `AVOC/CalibrationLog.lean` | `1c5b69e5b13ccdb14e05aae4f73906bb749ca23c652ddc08c811cf923831b6f9` |
| `AVOC/CalibrationBridge.lean` | `54357f9bb1ea9d92fc083688a94865ff01a6bd3b9a293ecf56107875aed50738` |
| `AVOC/CalibrationSchedule.lean` | `0010f469500d5ed0a8a875aee89ed05e2e7864f82e6bc41c51f9eb006e1f9031` |
| `AVOC/CalibratedPolicy.lean` | `2255bb4039a640ea2b16da78ebdba96805c4760962f18dd8d3527aa0abe5fe76` |
| `AVOC/CalibrationCodec.lean` | `bb10d71c582d0a5c7f64778bb50118d112c510475f908d1973d0f142d4e597fd` |
| `tools/CalibrationMain.lean` | `5648bf50bf8421a81dbfaf9f594b2a5795ea37532cec37e9269d385c7c1cfbe3` |
| `tools/calibrate_quote.py` | `1f063a4e4d0814e05fd98ef59f113d28650315c99d709fddca07e7321c8d9659` |
| `examples/calibration/README.md` | `0fe8a2b61a3eeeb09f5c132f6825deb9e1f9878a4678e3855f8a22e2afbd6f74` |

Review timestamp: 2026-09-19T14:40:21.834468+00:00
