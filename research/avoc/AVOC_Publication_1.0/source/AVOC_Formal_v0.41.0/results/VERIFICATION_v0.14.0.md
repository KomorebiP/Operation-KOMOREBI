# AVOC v0.14.0 — verification record

## Actual result

PASS: 69 final local compilation targets, 679 theorem axiom reports, and 21 expected negative rejections. The exact counts are 593 inherited + 86 new theorem/lemma declarations, 265 definition-like declarations, 11,515 non-audit source lines, and 68 non-audit modules.

All 63 inherited non-audit source modules are byte-for-byte unchanged from the restored v0.13 archive. The aggregate import and audit files were extended. The original archive passed all 587 recorded payload hashes and its ZIP CRC check.

## Toolchain and build scope

Lean 4.34.0-rc2, commit 6a10ac8c22beadecabdbb0919c2b50214762f91d. Mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06. All nine dependency revision pins match.

The portable runtime's seven parts passed CRC/member-SHA checking. Its combined archive hash was 66dfa8ce4627489bc61e44a77782931d36c1b626a177790a5d4599034b70ec34.

The local build directory was initially emptied. All inherited local sources were rebuilt. The five new modules and the final aggregate were compiled after their final edits, against that local library and the exact external cache. `final_local_build_summary.json` requires a successful current-source record for every one of the 69 final targets. This is not described as a single uninterrupted clean command or as a fresh mathlib rebuild.

The host interrupted one inherited build slice and one negative-suite slice. Neither was counted as success. Every target included in the final summaries has a successful/non-timeout current-source record or the expected substantive negative rejection, as appropriate.

## Axioms and source audit

`AVOC/FullAudit.lean` explicitly names all 679 declarations. The expected and actual name sets match. The union of axiom dependencies is exactly the standard set:

- propext
- Classical.choice
- Quot.sound

No project-specific axiom or native-evaluation axiom appears. The comment-aware positive-source scan has no sorry, admit, native_decide, project axiom, or unsafe declaration hits. All Lean invocations use one worker and warnings-as-errors.

## New negative tests

- FalseAttemptAdmission: claims a task was admitted during an attempt; reduces to False.
- FalseBudgetBypass: claims a one-unit attempt is allowed with zero budget; reduces to False.
- FalseMyopicStop: claims the two-step optimal value is zero instead of the proved 3/2; reduces to False.
- FalseRootCertificate: attempts to supply a local proof rule for the false root task; reduces to False.

The corresponding obstruction statements are positively proved in the library. A failed tactic alone is not presented as proof of unprovability.

## Independent exact rational regression

`checks/test_research_controller.py` passes using Python 3.13.5 and fractions.Fraction:

- 11 distinct dependency orders from forward-edge DAGs on 0 through 3 tasks;
- 22 model configurations including two congestion coefficients;
- 5,712 safe states;
- 17,616 transition/invariant checks;
- 5,712 independent Bellman versus policy-enumeration comparisons;
- 21,744 enumerated two-step adaptive policy trees;
- three attempted illegal actions rejected.

The exact Bayesian example matches the Lean values: horizon one 0, horizon two 3/2, successful path spend 2. All toy task propositions are True. The experiment checks the implementation in its declared finite range; it is not Lean extraction or empirical LLM evaluation.

## Evidence locations

AUDIT.json, SOURCE_PROVENANCE.json, and results/v0.14.0 contain source counts, exact commands, return codes, timings, source/log hashes, final local output hashes, dependency pins, full axiom output, negative logs, and finite regression results. Integrity checks are additional packaging checks, not substitutes for kernel verification.
