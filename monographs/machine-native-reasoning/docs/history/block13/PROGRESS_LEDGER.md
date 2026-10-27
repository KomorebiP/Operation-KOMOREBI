# Persistent formalization ledger

**Machine-Native Reasoning · Reviewed Core 0.2 · Cumulative companion 0.13.0**

| Block | New source results | Cumulative |
|---|---|---:|
| 01 | 1.1, 1.2, 2.1, 2.3, 3.1, 3.6 | 6/27 |
| 02 | 3.4, 3.5 | 8/27 |
| 03 | 5.4 | 9/27 |
| 04 | 3.8, 5.6 | 11/27 |
| 05 | 4.1 | 12/27 |
| 06 | 4.2 | 13/27 |
| 07 | 5.1 | 14/27 |
| 08 | 5.3 | 15/27 |
| 09 | 6.1, 6.2 | 17/27 |
| 10 | 6.4 | 18/27 |
| 11 | 7.1 | 19/27 |
| 12 | 7.3 | 20/27 |
| 13 | 7.4 | **21/27** |

The denominator counts selected source results, not relative difficulty or all Operation Komorebi theorems. Current release assurance depends on the terminated `final13` and `fresh13` gates and their production-object comparison. Historical PASS records retain their historical source bindings.

## Current mathematical work

Core 7.4 now has a general measure-theoretic formalization: conditional expectation of the measurable actual false-event indicator, almost-sure conditional domination, the marginal probability bridge, finite and countable union bounds, and deterministic nonnegative summable real budgets. The actual chosen-candidate event has a direct interface. Gates and outcome-dependent stopping preserve the unconditional bound by containment. Measurability lemmas distinguish probability events from arbitrary outer-measure sets.

Exact finite examples cover selection after a revealing history, disjoint and dependent errors, a nonempty null event, certain failure beyond any chosen finite prefix, retained-event conditioning, and unsupported numeric labels. The divergent constant-one real schedule is explicitly not summable, although its Lean real `tsum` is zero. No independence or finite sample-space restriction was added to the source proposition.

## Current-source verification

Authoring compilation and API preflight are distinct from the cumulative gate. Release evidence is `evidence/final13/report.json`, `evidence/fresh13/report.json`, both supervisor receipts, `evidence/FRESH_REBUILD_BLOCK13.json`, `evidence/COLD_SOURCE_BLOCK13.zip`, and `evidence/RELEASE_RESULTS_BLOCK13.md`. These receipts record actual outcomes. All 56 preceding substantive modules and the source book are pinned unchanged in `PREDECESSOR.json`.

Runtime reuse required the preserved executable-location adapter. A 3,072 MiB import smoke failed and the 4,096 MiB retry passed. The new verifier uses the latter internal limit. Both attempts remain recorded. Authoring and orchestration corrections are detailed in `REVIEW_NOTES.md`; no failed import or incomplete run counts as a negative-control success. Both initial cumulative gates failed an inherited fixture diagnostic after successful production builds and kernel replay. Explicit qualification of its intended `Instrument.normalize` name preserves its mathematical assertion and diagnostic contract. Those failed receipts and their source snapshot are retained under `evidence/failed13_attempt01`, separately from the final successful gates.

## Six remaining source results

2.4 common observable quotient; 2.5 positive probability packets; 3.2 partition correction-memory count; 8.1 target-relative joint reconstruction; 8.2 legal-operation quotient; 8.3 safe continuation preserving an ending strategy.

## Exact next restart

Formalize **Core 8.1**, target-relative joint reconstruction, at `source/core_v0.2.tex:873–878`. Use actual linear maps over a field. Prove existence of a linear decoder D with Q = D ∘ A exactly when ker A ≤ ker Q. Construct the induced map on the image and extend it to the full record space. Prove the full-state specialization and the kernel intersection identity for stacked participant records. Preserve the source's target-relative distinction: sharing can determine the protected target without determining all nuisance coordinates. A linear factorization does not itself implement a communication protocol or a bounded fixed-recipient interpreter.

Then proceed to 8.2 and 8.3, with the earlier three deferred results still tracked explicitly. Do not claim a complete 1.0 from the companion version number. No live process is required after delivery. Verify the package inventory before editing and preserve the reviewed book.
