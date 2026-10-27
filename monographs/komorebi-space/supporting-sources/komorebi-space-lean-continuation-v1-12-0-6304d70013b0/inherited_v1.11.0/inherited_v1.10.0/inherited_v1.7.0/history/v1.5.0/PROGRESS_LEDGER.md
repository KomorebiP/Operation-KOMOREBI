# Komorebi Space publication progress ledger

**Version:** 1.5.0  
**Date:** 12 October 2026  
**Status:** Bounded-budget publication expansion complete. New written results are not newly Lean-verified.

## Authoritative baseline

Begin with `Komorebi_Space_Complete_v1.5.0.zip`. The predecessor ZIP SHA-256 is `b483142e46513ab0076b0ab8ac66555b45c6b003944f4ab63bbe36b0c6b56d4a`. Its 1,455-file manifest and archive integrity were checked before editing. `history/v1.4.0/` preserves the prior publication sources and records. All original evidence archives remain unchanged.

The canonical `formal/` tree is byte-identical to the accepted v1.2.0 baseline through the v1.4.0 predecessor. The current 156-file preservation check is `audit/regularization/formal_preservation.json`.

## Completed work

| Workstream | Result |
|---|---|
| Monograph | **125 pages**, six parts, 33 numbered sections, five appendices. Previously 105 pages. |
| Bounded existence | WR01–WR02: weak bounded feasibility and strong convergence of minimum repairs for nested affine constraints. |
| Budget geometry | WR03–WR05: attained finite-budget profile, sharp dual witness, robust model/data error. |
| Regularized repair | WR06–WR09: exact protection, Gram metric, quadratic energy identity, four limit cases, sharp noise response. |
| Diagonal model | WR10–WR12: exact regularized family, infinite-tail enclosures, pi/4 matched-budget asymptotic, attainable noisy datum. |
| Evidence labels | **80 KS items / 211 source references** retained; **12 WR groups** have complete printed proofs and no new Lean coverage. |
| Software | Exact rational protected solver with symbolic-normalized budget certificate and independent adjugate/KKT tests. |
| Finite checks | **178,754 assertions** in six rerun suites, including 34,388 new assertions, nine false-claim controls, and ten invalid-input cases. |
| Reader aids | Twelve solved workshop problems; extended hypothesis atlas and separate WR catalogue. |
| Visual guide | **39 pages, 36 plates**, six new mathematical figures. |
| Lean/evidence guide | **34 pages**, with historical formal and new written evidence explicitly separated. |
| Build and review | Accepted terminal exit zero in build06. All 198 final pages rendered; reviewed draft and final pixels are hash-bound. |

## Retained formal result, not new execution

The v1.2.0 record contains 138 production modules and a root, 139 accepted targets, 4,745 audited project declarations, and 1,507 explicit named theorem/lemma declarations. No new Lean compilation, axiom query, or formal module was added. KS54–KS58 remain completed. WR01–WR12 are distinct future formalization work.

## Failures and corrections

The first build failed on an unescaped caret in a generated hypothesis-table cell. Its log remains FAIL. The second build was interrupted without a terminal receipt and is not counted as PASS. Build03 passed but was superseded after scope-label and visual corrections. Build04 returned zero, then was superseded by a pagination correction. Build05 returned zero, then was superseded by inline placement of the six new figures. Build06 returned zero and produced the final reviewed PDFs. Review moved two end-of-chapter figures into the discussion, shortened an orphaned reference continuation, and corrected stale v1.4.0 evidence wording. An inspection command requested a nonexistent `checks/manifest.py`; the actual `checks/hash_manifest.py` was then used. This lookup failure did not modify a proof or contribute pass evidence.

## Next restart

Run `python3 checks/verify_payload.py` before changing the package. For editorial work, retain KS01–KS80 and WR01–WR12, edit sources, run `bash build.sh`, render and inspect, then renew hashes last. For formal work, first select a WR theorem group and connect it to the existing actual protected Hilbert interfaces. Preserve the old accepted record and run a genuine new compiler/axiom replay before claiming new coverage. Do not remove a preservation check merely to make a changed source tree pass.

No universal view doctrine, arbitrary higher-stack theorem, unrestricted semantic realization, universal Python refinement, native Windows replay, independent kernel, or source rebuild of mathlib is claimed.
