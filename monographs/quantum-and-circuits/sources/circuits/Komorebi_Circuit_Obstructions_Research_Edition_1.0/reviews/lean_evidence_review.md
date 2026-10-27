# Lean evidence and source review

Review date: 2026-10-07T14:23:41.372900+00:00

Mode: read-only source/evidence review and conservative mathematical proofreading. The manuscript and generators remain root-owned; this reviewer changed neither.

Reviewed manuscript SHA-256: `2320ce63287bc8c2fb853e490542679e314d01ff55c2868ab8c04db33d417781`

## Final status: PASS

Root corrected the uniquely forced predicate identifier to `CompleteSafeDegreeLE f d`, tightened both negative-control descriptions, separated the positive parity exclusion from the wrong-type rejection mechanism, and clarified command requirements. This reviewer reread each corrected sentence in context. Root also added the initial degree-certificate premise, the later restoration role, and the distinction between proof construction and an exposed executable compiler.

No unresolved source/evidence or local mathematical-notation issue remains within the reviewed scope. One optional precision improvement was suggested for the finite circuit-word sentence: name its documented canonical alphabets of 12 and 28 gates, since the exact checker deduplicates swapped Toffoli-control order.

## Checked facts

- General C01 uses arbitrary `W : Type` with `DecidableEq W`. No finiteness premise is present. The canonical model has the finite sum type described in the guide.
- `Restores` quantifies all logical inputs and both target values; it is a theorem premise, not an assertion that every circuit restores.
- The direction/discrepancy definitions and exact `H_i=f AND D_i` transport give coordinatewise safety and existential complete coverage, rather than packet XOR reconstruction.
- `DegreeLE` is the stated inductive finite XOR-monomial certificate; `degreeLE_iff_polynomial` supplies the concrete representation bridge. Repetitions are allowed. No formal ANF normalization algorithm is asserted.
- `beta` and `betaStar` have proved least-bound existence and specifications. `betaStar` is the least common upper bound over all affine output XORs; it agrees with the finite maximum reading, not a minimum.
- Natural subtraction saturates at zero; the guide correctly relates `2*betaStar-3` to the integer maximum. Balanced cuts concern Toffoli cost, rather than gate-list midpoint.
- The two-Toffoli dirty AND example is distinct from the universal AND2 lower bound. The general k-input monomial optimum is not marked formal.
- Exact inventory scan succeeded on all eight proof modules after nested-comment removal. It found no active forbidden construct from the verifier's set and produced exactly the committed 115 indexed theorem records. This is a fresh text-level check, not Lean elaboration.
- All 115 catalog names, module/file/line records, source hashes, and archived axiom sets match. All 15 formal source/infrastructure hashes in the archived success record match the preserved source bytes.
- Module counts: `{'CircuitObstructions.AffineOutput': 14, 'CircuitObstructions.CutComparison': 13, 'CircuitObstructions.Degree': 19, 'CircuitObstructions.DegreeChecks': 8, 'CircuitObstructions.Examples': 11, 'CircuitObstructions.Gates': 16, 'CircuitObstructions.MultiplicativeDegree': 12, 'CircuitObstructions.SafeDegree': 22}`.
- Archived axiom set distribution: `{('propext',): 17, ('Quot.sound', 'propext'): 40, ('Classical.choice', 'Quot.sound', 'propext'): 30, (): 25, ('Quot.sound',): 3}`. This equals 25 none, 17 propext only, 3 Quot.sound only, 40 propext+Quot.sound, and 30 all three.
- Archived September 21 status is PASS with 115 declarations, eight replayed modules and eight expected negative rejections. Those rejections all have nonzero exit status and recorded success.
- October 7 formal attempt is FAIL with `commands=[]` and missing `lean`; no new compilation, axiom audit, replay or negative-control result occurred.
- Current full scientific replay completed successfully in 18.47 seconds. Its finite scope does not certify a new universal theorem.
- 278 functions for arities 0..3 versus 276 for arities 1..3 are consistent: exactly two zero-arity Boolean functions.

## Proofreading outcome

Routine corrections: one source predicate identifier, two negative-control descriptions, one command-requirement clarification, all applied by root and reread in context.
Mathematical-token changes by this reviewer: none.
Unresolved proof/evidence issues: none identified within this bounded source/evidence review. PDF layout is reviewed by root separately.
