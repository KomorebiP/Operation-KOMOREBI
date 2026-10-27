# Fresh predecessor verification and corrections

The pinned Lean 4.34.0-rc2 runtime and all nine dependency revisions were verified. Cached external dependencies were reused; they were not rebuilt from source. A fresh local build started with zero local .olean files and passed all 205 predecessor targets, including AVOC.lean and the Lean entrypoints, with warnings treated as errors. The exact-name inherited audit returned all 2,044 expected public theorem/lemma names and only propext, Classical.choice, and Quot.sound. This inherited inventory is not a fresh inventory of v0.39 declarations.

## Corrected predecessor negative-suite evidence

The predecessor wrapper overstated substantive rejection. Five retained tests failed while elaborating their statements because a local primality instance was missing: FalseAddMinorRanks, FalseAffineAnyLinearKey, FalseAffineOffsetReuse, FalseFreeRankProbe, and FalseUnfundedMinor. FalseZeroCostWitness failed because decide refused a goal with an unused free variable. None of those six initial failures establishes the intended mathematical rejection.

The first five now introduce the same local Fact (Nat.Prime 5) used by their example modules. The sixth changes the cost goal explicitly to 1 = 0 before decide. False propositions and intended proof attempts are otherwise preserved. Original files and hashes are in provenance/v0.38_negative_setup; the initial diagnostic logs are under negative_setup_failures. The corrected inherited suite has 111 substantive rejections, with no import, typeclass, timeout, or tactic-setup failures counted. New tools/run_negative_v039.py rejects setup failures and unrecognized diagnostic classes, verifies exact source/log/import hashes, and recognizes only three explicitly inspected type-mismatch tests.

## Executable evidence

- Independent Fraction regression passed 21 Lean planning comparisons and 1,523 compatible realizations.
- Both selected-only robust workflows passed: warm with cold absent, cold with warm absent.
- Commit-before-ack recovery passed with one warm external operation and zero cold operations, including duplicate resume.
- All four inherited lazy staged scenarios passed: warm, cold, crash/recovery, and invalid artifact.

Initial robust workflow fixtures contained absolute paths into the previous workspace. Those first runs failed before selected execution. Relocated fixture copies change only the selected artifact path and preserve the absent unselected path. Inherited runtime source and original fixtures were not edited. See workflow_path_failures.json.

All new evidence is separate from the retained v0.38 release evidence. The runtime-recovery helper initially received four HTTP 502 failures while retrieving archived runtime files; a separately located existing runtime supplied by another agent was verified and used instead. No downloaded runtime success is claimed.

## Portable rerun command

With AVOC_LEAN_KIT set, `python tools/run_inherited_regression_v039.py --case all` runs all four predecessor check scripts while relocating only evidence and selected fixture paths. Each adapted check records its original and transformed source hash. The helper initially failed before executing the oracle because dynamically loaded dataclasses require a registered Python module; that helper defect was fixed by registering the temporary module, and the initial failure record is preserved.

A later check of the combined helper passed the oracle but stopped at the cold workflow because its run directory already existed. The precise source of the preexisting directory was not established. Evidence is preserved in reproduction_existing_directory_failure.log. The helper now allocates a unique timestamp/UUID directory for each invocation under results/v0.39.0/inherited_replays; it never removes prior evidence. The final invocation is summarized in results/v0.39.0/inherited_regression_summary.json.
