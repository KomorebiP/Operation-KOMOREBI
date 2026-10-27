# Komorebi Space publication progress ledger

**Version:** 1.3.0  
**Date:** 11 October 2026  
**Status:** Expanded publication completed. Accepted formal baseline retained unchanged.

## Authoritative restart

Begin with `Komorebi_Space_Complete_v1.3.0.zip`. Editable reader sources are under `source/`. The canonical Lean tree is `formal/`, preserved byte-for-byte from the accepted version 1.2.0 baseline. Its evidence remains under `audit/formal/`. The previous publication snapshot is `history/v1.2.0/`, alongside older history. The predecessor ZIP and formal-file hashes are recorded in `audit/expansion/baseline.json`.

## Completed in this expansion

| Workstream | Result |
|---|---|
| Monograph | 84 pages, five parts, 24 sections, three appendices. Previously 57 pages. |
| Main development | Full proofs and explanations for stronger prescription, finite observation, eventual maps, cofinal transport, repair mismatch, full-framing boundaries, and uncertainty certificates. |
| Worked problems | Complete four-cycle and reflection-triangle calculations, plus five solved workshop problems. |
| Source map | 70 principal IDs, 180 resolved references. KS59–KS70 use existing verified declarations. |
| Visual guide | 27 pages and 24 plates; six new vector plots. |
| Lean guide | 28 pages, expanded scope notes and catalogue. |
| Formal preservation | Every formal file unchanged. No new compiler or axiom run claimed. |
| Exact finite checks | 130,549 assertions across four freshly rerun suites. The new suite contributes 96,345 and eight rejection controls. |
| Publication build | Terminal exit code zero under supervised execution. |
| Layout | All 139 final pages rendered and reviewed; mechanical preflight passes. |

## Formal baseline, not new execution

Version 1.2.0 supplied the accepted combined 138-module project and root, 139 compilation targets, 4,745 audited declarations, and 1,507 explicit named theorem/lemma declarations. It closed KS54–KS58. This expansion retains those results without changing source bytes or calling the compiler again. Source correspondence is an editorial relation, and finite examples do not automatically become newly compiled theorems.

## Failures retained

The first outer build window timed out during typesetting. A subsequent preflight rejected an overfull module-name paragraph. A later outer invocation timed out after reaching successful mechanical output, so it was replaced as terminal evidence by the final supervised zero-exit build. The visual pass also corrected an awkward contents break and short final continuations. See `REVIEW_NOTES.md` and `audit/expansion/attempts.json`. No failed attempt is represented as the accepted build.

## What remains outside this edition

No new universal doctrine, arbitrary higher-stack theorem, unrestricted semantic realization, universal Python refinement, native Windows replay, independent Lean kernel, or source rebuild of mathlib is claimed. No item has been reopened on the completed KS54–KS58 formalization list. Future mathematical extensions require their own hypotheses and evidence.

## Next restart procedure

Run `python3 checks/verify_payload.py` first. For editorial work, preserve KS01–KS70, edit the LaTeX and source correspondence, run `bash build.sh`, render the full reader set, inspect changed pages, and renew hashes last. For new formal mathematics, preserve the existing evidence and create a separately versioned formal baseline with an actual clean compiler and axiom replay. Do not remove the unchanged-source check simply to make a changed formal tree pass.
