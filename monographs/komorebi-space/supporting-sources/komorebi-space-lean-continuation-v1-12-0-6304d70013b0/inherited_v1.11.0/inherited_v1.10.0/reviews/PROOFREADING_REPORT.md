# Komorebi Space v1.10.0 manuscript and proofreading report

This revision incorporates the WR03–WR05 budget continuation into the full monograph. It retains the v1.9.0 proofreading changes and the underlying mathematical figure assets. Its formal acceptance and final rendered coverage are recorded in `PUBLICATION_VERIFICATION.json`. The clean replay and independent postflight both passed.

## Changed scope

Reviewed the edition description, edition metadata and evidence labels, the bounded-realization scope box, the budget-image/residual paragraph, the closing coverage discussion, the hypothesis atlas, the source concordance, and the extension appendix. The extension appendix gains a clause-to-declaration map for the four budget modules. Historical v1.2.0, v1.6.0, and v1.8.0 counts retain their original meaning. The v1.10.0 current counts use separate macros.

The current WR coverage is nine complete principal-statement counterparts (WR01–WR07, WR13, WR14), two partial groups (WR09, WR16), and five written-only groups (WR08, WR10–WR12, WR15). Completing fixed-budget geometry does not complete the regularization-limit theorem WR08 or its dependent limits.

## Mathematical erratum

Location: `source/chapters/05g_budget_certificates.tex`, paragraph immediately following the discussion of closed budget images.

The v1.9.0 sentence incorrectly identified the best residual as the projection of the datum onto the reachable image set. The projection is the nearest reachable **image**, and the residual is the datum minus that image.

The corrected paragraph introduces `y_M = P_{T({a: norm(a)≤M})} r`, identifies the residual as `r-y_M`, and refers to corrections mapping to `y_M`. Those corrections can differ by kernel vectors. This precisely separates nearest-image uniqueness, residual uniqueness, and correction uniqueness. The surrounding theorem statements and proofs are unchanged. The correction follows the fixed-budget projection argument and was specifically requested after focused proof review.

This is the sole changed existing mathematical formula in the monograph. The new appendix describes already compiled declaration types and their hypotheses; it does not insert a new printed theorem or replace a proof.

## Routine and layout edits

- Synchronize all current WR coverage statements and update the next central target to WR08.
- Add the exact public names for budget-image closedness, minimum attainment, infimum interpretation, floor limits, feasibility equivalences, profile geometry, attained duality, and robust certificates.
- Separate historical verification records from the current budget continuation.
- Keep the new short declaration tables with their namespace introductions.
- Preserve all figure-source and image-asset bytes.

The review was conservative and limited to the changed passages and their necessary context. This edition does not claim another full theorem-by-theorem referee audit or a fresh full proofreading of the historical visual and Lean companion guides.

## Validation and observed failures

The first three-pass PDF build succeeded with no blocking diagnostics. Static checking found no malformed environments, missing labels, unresolved citations, missing graphics, or duplicate reference targets. The draft rendering had no out-of-page words or unresolved-reference markers.

A guarded editing operation stopped because an apostrophe had been escaped differently from the source text. It made no replacement at that paragraph. The paragraph was then selected explicitly and corrected. No source content was lost.

Initial rendered review found short declaration tables split across pages and one namespace separated from its table. The new groups were kept together before final review. The detailed draft and final visual records identify the reviewed PDF hashes and exact coverage. Underfull-box diagnostics are evaluated visually rather than represented as absent.

The formal compiler failures, mathematical controls, and their corrections are documented in the budget development records. They are separate from manuscript validation. Historical numerical suites were preserved and not rerun for this publication revision.

The full-type and axiom export took 385.582 seconds. A possible replacement replay was discussed while it was computing, and a draft manuscript path was briefly changed to `clean_budget_02`. The original export completed before any interruption or verifier edit occurred. The unused path draft was preserved, the publication path was restored to `clean_budget_01`, and the actual audit total was added. No replacement replay was needed. Final publication acceptance is tied to the original accepted run and its independent postflight record.
