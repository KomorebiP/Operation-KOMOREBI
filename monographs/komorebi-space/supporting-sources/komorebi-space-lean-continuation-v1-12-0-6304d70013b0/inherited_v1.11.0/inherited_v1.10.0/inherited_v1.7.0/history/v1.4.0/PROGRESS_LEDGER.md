# Komorebi Space publication progress ledger

**Version:** 1.4.0  
**Date:** 11 October 2026  
**Status:** Expanded publication complete. Accepted formal baseline unchanged.

## Authoritative restart

Begin with `Komorebi_Space_Complete_v1.4.0.zip`. Editable reader sources are under `source/`. The canonical Lean project remains under `formal/`, byte-for-byte unchanged from the accepted version 1.2.0 baseline. The predecessor snapshot is `history/v1.3.0/`, alongside older history. Its archive hash and all formal-file hashes are in `audit/deepening/baseline.json`.

## Completed in this edition

| Workstream | Result |
|---|---|
| Monograph | **105 pages**, six parts, 29 numbered sections, four appendices. Previously 84 pages. |
| Approximation theory | Complete summable and variable-rate exactification development, protected limits, path comparison, and profile boundaries. |
| Residual floor | Closure versus exact membership, persistent floors, and separation from preimage bounds. |
| Hilbert model | Complete written protected escape example, infinite-tail estimates, all-candidate norm divergence, finite inverse gains, and semantic-image distinction. |
| Costs and phase | Directed cost geometry and collapse example; coherent nonremovable pair phase, matrix lifts, and eight-element extension. |
| Source correspondence | **80 principal IDs, 211 resolved references**. New KS71–KS80 use existing accepted declarations. |
| Worked-model scope | Explicit formal/written/finite distinction in `data/deepening_models.json`. |
| Reader aids | Nine solved problems and a new hypothesis atlas. |
| Visual guide | **33 pages**, 30 plates, including six new vector figures. |
| Lean/evidence guide | **33 pages**, updated source catalogue and scope notes. |
| Formal preservation | All **156 formal-tree files** retain predecessor hashes. No new compiler or axiom run. |
| Exact tests | **144,366 assertions** across five freshly rerun suites; new suite has 13,817 and eight rejection controls. |
| Build | Accepted supervised build returned exit code zero; receipt `audit/deepening/build_attempt05.json`. |
| Review | All **171 final reader pages** rendered. Draft contact sheets inspected, changed final pages individually checked, and unchanged pixels compared. |

## Retained formal baseline

Version 1.2.0 supplied 138 production modules and one root, 139 accepted compilation targets, 4,745 audited project declarations, and 1,507 explicit named theorem/lemma declarations. It closed KS54–KS58. This edition preserves that result without changing formal sources or executing Lean again. The new printed infinite-dimensional model is not a new compiled Lean instance.

## Failures retained

The first outer build timed out before terminal evidence and remains INTERRUPTED. Supervised replacements completed. Review corrected an orphaned source paragraph, an awkward equation transition, a duplicated figure/table, reversed nonzero cost labels in the first directed-graph draft, and crowded inner labels. Only the final rebuilt and rendered version is accepted. See `REVIEW_NOTES.md` and `audit/deepening/attempts.json`.

## Scope and next work

No item has reopened on the completed KS54–KS58 list. The principal additions KS71–KS80 have existing source correspondences, but the Hilbert escape model, matrix lifts, central-extension example, and other printed calculations have not gained new Lean instantiations. Those are explicit optional future formalization tasks, not concealed verification claims.

No universal view doctrine, unrestricted semantic realization, arbitrary higher-stack theorem, universal Python refinement, native Windows replay, independent kernel, or source rebuild of mathlib is claimed.

## Next restart procedure

Run `python3 checks/verify_payload.py` before changing anything. For editorial work, preserve stable KS identifiers, modify the relevant LaTeX and source notes, and run `bash build.sh` with enough execution time. Render the full reader set, inspect changes, then renew hashes last. The publisher does not invoke Lean. For new formal mathematics, preserve the accepted evidence, create a separately versioned formal baseline, and perform a genuine fresh compiler and axiom replay before claiming coverage. Never weaken the unchanged-source check to make edited formal files pass.
