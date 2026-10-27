# Persistent formalization ledger

**Machine-Native Reasoning · Reviewed Core 0.2 · Cumulative companion 0.15.0**

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
| 13 | 7.4 | 21/27 |
| 14 | 8.1 | 22/27 |
| 15 | 8.2 | **23/27** |

The denominator counts selected source results, not relative difficulty, percentage of the whole research program, or all Operation Komorebi theorems. Current release assurance depends on the completed `final15` and `fresh15` gates and their strict production-object comparison. Historical PASS records retain their own source bindings.

## Current mathematical work

Core 8.2 now uses actual labels, enabled-action sets and deterministic legal successors. A canonical partial-system representation marks disabled actions by absence, with an explicit exact translation from supplied enabled sets and dependent legal successors. Under a surjective projection, quotient data exist exactly when equal fibres agree on labels, availability and projected enabled successors. The representative construction is explicit, and the actual partial quotient data are unique.

Arbitrary finite action-list execution commutes with projection. Legality is preserved and reflected. The entire label sequence, including the initial label and every intermediate state, is retained. Small exact examples distinguish valid history compression from invalid merges that lose permission or successor information. Unattained quotient states and arbitrary disabled-action totalizations illustrate the limits of uniqueness. These are structural theorems and exact examples, not empirical evaluations.

## Current-source verification and preservation

Current evidence is `evidence/final15/report.json`, `evidence/fresh15/report.json`, both supervisor receipts, `evidence/FRESH_REBUILD_BLOCK15.json`, `evidence/COLD_SOURCE_BLOCK15.zip` and `evidence/RELEASE_RESULTS_BLOCK15.md`. The final release-results file reports actual execution, declaration counts and remaining limits. All 60 predecessor substantive Lean modules and five source-book files are pinned unchanged in `PREDECESSOR.json`.

Workspace maintenance removed the previous working copy. The complete saved Block 14 archive was recovered and all 8,258 payload hashes checked before source extraction. It remains byte-identical under `evidence/history/block14`. Current sources and Block 15 evidence are directly accessible; all earlier detailed evidence remains inside that complete historical archive. This is a packaging layout change, not lost history or a claim that historical receipts verify edited sources.

Recovery encountered a full filesystem, a missing old runtime executable and an incomplete changing alternate runtime manifest. A stable existing installation supplied the exact compiler, all nine pinned repositories and matching artifacts. The owned runtime facade reuses those files without modifying shared installations. Current complete gates must still check every actually imported upstream object against the saved inventory. Failures and corrections are documented in `REVIEW_NOTES.md`.

## Four remaining selected source results

| Core result | Remaining proof scope |
|---|---|
| 2.4 | Equivalence between common observable behaviour, invisible invariant discrepancy space, and a shared linear quotient; switching candidates between operations. |
| 2.5 | Positive cone-preserving packet mixtures, zero-weight components, and classification of complete positive idempotents on the coordinate cone. |
| 3.2 | Occupancy classification of correction signatures, exact count 2^r, and r-bit necessity/sufficiency. |
| 8.3 | Finite sure-ending and safe-continuation fixed points, one policy with an observable stop switch, and the ending-rank bound. |

These four statements contain several separate proof obligations. The count is not a time estimate.

## Exact next restart

Formalize **Core 8.3**, safe continuation retaining an ending strategy, at `source/core_v0.2.tex:918–927`, with all setup at lines 903–916. Use a finite observed configuration space, finite action catalogues, nonempty successor sets, safe set S, ending target G contained in S, and a safe hold action at G. Build the increasing sure-ending sequence T and the decreasing safe-running sequence L, prove stabilization, and prove the policy equivalence at L*. Keep the command authentic and observable before the next action as an explicit premise. Prove every post-command successor path reaches G within the first-entry rank, without choosing an action after seeing its successor.

Then close the earlier deferred results 2.4, 2.5 and 3.2. Preserve all four until their actual admission gates pass. No complete-book or unrestricted real-world governance claim follows from the companion version. No live process is required after delivery. Verify the package inventory before editing and preserve the reviewed source book.
