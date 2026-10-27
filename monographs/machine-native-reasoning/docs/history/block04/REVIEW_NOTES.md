# Lean Block 04 — review and verification record

**Machine-Native Reasoning · Reviewed Core 0.2 · Cumulative formal companion 0.4.0 · Komorebi P. · 10 October 2026**

## Scope

Two source results join the nine from Block03: Core **3.8**, whole-history approximation with sharp conditioning, and Core **5.6**, uniform policy error and changed-policy regret. Coverage is **11 of 27**. Core 4.1's additional response approximation remains among the sixteen unformalized results.

The new modules are `Variation`, `ApproximateHistory`, `ApproximateDecision`, and `ApproximationExamples`. Every one of the fourteen predecessor substantive modules remains byte-identical. The book, original source index, prior mathematical fixtures, and inherited API check remain unchanged. The aggregate module and verification infrastructure are intentionally extended.

## Formal inventory and release gates

| Item | Current source inventory or gate contract |
|---|---:|
| Source results admitted | 11 / 27 |
| Authored theorem declarations | 322, including 85 additions |
| Authored declarations overall | 503, including 113 additions |
| Elaborated theorem constants | 676, including generated auxiliaries |
| Transitive axiom-audited declarations | 857 |
| Production modules | 19, including one import-only root |
| Same-kernel substantive replays | 18 |
| Negative-control outcomes | 36, including nine additions |
| Predecessor files required unchanged | 51 |
| Matched upstream object/runtime entries | 10,430 |

The completed cumulative preflight established these counts. Current release conclusions must be read from `evidence/final04/report.json`, `evidence/fresh04/report.json`, and `evidence/FRESH_REBUILD_BLOCK04.json`, which bind their own source hashes and actual execution outcomes. Elapsed times and any proof-object comparison exception are recorded there rather than inferred from previous blocks. The final and extracted-source gates are required to complete before this package is delivered as checked.

The only permitted and observed foundational axioms are `propext`, `Classical.choice`, and `Quot.sound`. No production placeholder, custom axiom, `native_decide`, unsafe primitive, or external proof shortcut is admitted. Thirty-five intentionally invalid fixtures must fail compilation for specified proof or placeholder diagnostics. The remaining inherited fixture intentionally compiles with an invented axiom and must then be rejected by the axiom policy.

These counts describe supporting proof code and its elaboration, not independent discoveries or statistical samples.

## Mathematical review

The history law is defined from the actual fine instrument before projection, including the initial state and all successors. The policy consumes only observed action/report histories. Time-dependent instruments and separate per-time defects are allowed. Joint report/state rows are required; matching two marginals is not enough. The cap one follows from normalization of the constructed laws.

The conditioning theorem uses the discrepancy on the complement of the event to obtain coefficient one and the maximum of the two positive event masses. It does not substitute a weaker factor-two estimate, omit the denominator, or normalize an impossible event as a posterior. Both the equal-mass rare-report example and an unequal-mass sharpness example are kernel-checked. A separate example establishes the strictness of the positive-counterpart threshold.

The regret theorem proves a fixed-policy expectation bound uniformly over a common finite catalogue before invoking approximate optimality. The same bounded complete loss must be used across the two models for each policy. Finite minimizers are actually constructed. The theorem is directly composed with the full-history law construction. A generic host-program or arbitrary stopping-tree compiler is not supplied; any stopped/padded law representation remains part of the model contract. Expected-risk control does not imply hard admissibility or a zero-risk guarantee.

The source's sensor likelihood change from 3/4 to 37/50 is represented by a new actual fine instrument. Its full report/coarse-successor row error is proved exactly 1/100 for every hidden world. All finite same-policy histories receive the corresponding H/100 bound. The values 69/2000 and 69/1000 are exact bound coefficients for H=3 and complete loss range [0,23/20], not a measured sensor regret or a new proof that its old adaptive policy remains optimal under changed likelihoods. The factor-two selection theorem is independently instantiated on a sharp binary classification example.

## Actual authoring failures and repairs

1. The active Lean runtime was absent. The five saved compact runtime parts were recovered, their hashes compared with the predecessor recovery record, concatenated and extracted. The combined archive hash is `f7548038f94ea30789ce28fc2ff769c40e9c37d8879ea133e9bea821056342c7`. This is local consistency with the saved runtime, not new independent source authentication.
2. Early proof drafts encountered ordinary Lean elaboration and tactic failures involving finite sums, missing finite-product imports, rewrite direction, implicit binders, denominator algebra, simplification and warnings treated as errors. Raw attempts remain in `evidence/development04`. Failed elaborations are not counted as checked statements.
3. Two combined authoring invocations were interrupted by their outer execution allowance. A separately supervised `ApproximateHistory` attempt also reached its recorded 45-second limit. These attempts produced no accepted proof result. A smaller diagnostic compilation exposed a universe mismatch in the recursive path type. The corrected type uses one explicit universe and a reducible chronological construction; it then compiled within the unchanged per-command limit. The mathematical state/history contract was not weakened.
4. The reset-history example initially left finite kernel sums unresolved. Explicitly unfolding the finite kernel application discharged the original exact claim. The theorem continues to compare full histories, not merely final states.
5. The first complete cumulative `preflight04` gate passed compilation, API checks, axiom checks, all local replays and all 36 controls. Documentation and release metadata were subsequently updated, so final release claims require the new final and fresh gates on those updated inputs. An old preflight receipt is not silently substituted for the release receipt.

No source-book theorem required a mathematical correction in this block. That is not a claim that all proof attempts succeeded or that an independent reviewer could find no modeling error.

## Reproduction boundary

Each full gate starts with an empty local object directory, compiles every production module, checks independently restated API types, inspects the actual environment, audits transitive axioms, replays every substantive module with `leanchecker`, executes the expected-outcome controls, and verifies predecessor and upstream object hashes. The fresh run starts from a source ZIP with compiled objects omitted. Development seed objects are never used by these cold gates.

`evidence/FRESH_REBUILD_BLOCK04.json` compares every production `.olean`, source pins, inventories, source admission, axiom records, controls, and dependency records. Absolute paths, timings and timestamps are not mathematical equality criteria. Generated audit-helper binary identity is reported separately because Block03 recorded a nonproduction serialization difference; its generated source and actual complete axiom output remain mandatory exact comparisons. No production-object mismatch is silently exempted.

Lean is 4.34.0-rc2 at `6a10ac8c22beadecabdbb0919c2b50214762f91d`, with mathlib `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. Per-command execution uses one thread, warnings as errors, a 3,072 MiB Lean-internal allowance and a 45-second wall limit. The supervising invocation has a 900-second whole-gate limit. There is no separately enforced OS memory or affinity cap.

The project-authored receipt, source and archive tools are not the Lean kernel. Same-kernel replay reuses pinned upstream objects rather than rebuilding Lean or mathlib from source or independently checking the complete dependency tree. Checksums establish byte consistency, not truth of environmental premises or source provenance.

No source-book PDF revision, parent Python suite, neural training, physical sensor test, hardware benchmark, external account action, hosted repository change or Windows run is included. The mathematical claims use exact real arithmetic and explicit probability laws. No runtime, standalone font, private transcript or third-party full paper is distributed.
