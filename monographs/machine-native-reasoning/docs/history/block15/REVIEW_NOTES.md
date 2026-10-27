# Block 15 review and execution notes

The target is Core 8.2, Reviewed Core 0.2, `r:governance`, at source lines 888–898 with the legal-operation setup at line 886. This block starts from the recovered Block 14 archive, SHA-256 `5c709adbf7c3d45216804f4d6c27e27fd778115d79618ea23b7705d52d6867d4`. Every one of its 8,258 recorded payload members passed streamed SHA-256 and byte-length checks before extraction. The complete archive is retained unchanged under `evidence/history/block14`. All 60 predecessor substantive Lean modules and all five source-book files are pinned unchanged.

## Source and proof review

The model represents deterministic partial successors canonically: `none` means disabled and `some y` records the legal successor. The exact translation from supplied labels, enabled sets and dependent legal successors preserves the given availability and transition values. A round-trip theorem shows that this representation loses no partial-system data.

Three actual fibre conditions precede the quotient construction: equal labels, equal enabled sets, and equal projected legal successors. Under surjectivity, representatives define quotient labels and steps, and compatibility proves they factor the source data. Necessity and uniqueness are proved separately. The source-facing theorem states the criterion directly for the original supplied inputs and retains finite state/action assumptions. Empty types need no additional nonempty premise.

Finite-word execution records the entire state path. Arbitrary-word induction proves projected execution equality, legality in both directions, and the full protected-label sequence including the initial label. Quotient traces lift from any representative of their initial state. These are universal finite-word theorems, not bounded enumerations.

The source's uniqueness concerns legal successors. Arbitrary totalized values at disabled actions are not unique. Canonical absence represents the source domain faithfully while avoiding that unsupported stronger claim. The manuscript remains unchanged. A separate agent reviews the raw source, code and interfaces in `evidence/CORE82_SOURCE_AND_CODE_AUDIT.md`. This is an additional reasoning pass in the same model family, not independent peer review or a distinct proof kernel.

## Corrections and actual failures

Workspace maintenance had removed the earlier working tree. Initial creation of a helper directory failed with `No space left on device`, despite an earlier free-space observation. Later free space became available; no other task's files were deleted. One system-process diagnostic also failed with `fatal library error, lookup self` and provided no validation evidence. The saved Block 14 archive was recovered successfully and verified before use.

The old runtime path lacked its Lean executable. A second portable directory launched the exact compiler but its workspace manifest was empty or changing during apparent concurrent repair, producing JSON decoding errors. A stable surviving installation supplied the matching compiler and all nine pinned repositories. The owned facade points to that unchanged toolchain and package cache; matching adapter and inventory files are regular local copies. No shared runtime files were changed and no duplicate runtime was downloaded. `evidence/runtime15` retains the failed probes and successful identity checks. Startup identity alone is not proof verification; actual imported artifact hashes are checked by the complete gates.

The first main-proof compile failed because case analysis had already rewritten expressions that the proof then tried to rewrite again. A second attempt contained a redundant `rfl` after the goal was already closed. Removing the redundant tactic steps fixed the proof; the third compile passed. The additional exact raw-source bridge then compiled successfully on the fourth attempt. No theorem was weakened and no unfinished proof was admitted. Logs are in `evidence/development15/main_*`.

A preliminary trace-interface probe failed because its minimal imports did not provide `Finite`. The corrected probe imported `Fintype.Basic`. That probe used a hypothesized interface only and is explicitly not production proof evidence. Both actual production compiles against the real main module passed. The final trace compile records the final main-source hash. An initial informal count of 18 trace theorems was corrected to 15 by source inspection; release counts are computed from the actual source inventory.

The example module compiled on its first build and on its final recompile. The first API build failed because its imports lacked the `Fintype`-to-`Finite` instance. Adding `Mathlib.Data.Fintype.EquivFin` fixed that import/instance issue without changing hypotheses; subsequent API builds passed. All nine new negative fixtures passed their stipulated mathematical rejection diagnostics on their first preflight, with no bad imports or timeouts. The separate inherited-control preflight then passed all 143 expected outcomes against the new aggregate, with zero timeouts or import/name-resolution failures. Its custom-axiom fixture compiled and was correctly rejected by policy. That two-worker preflight took 124.13 seconds and preserved all inherited fixture hashes. Complete cold gates remain separate obligations with their own receipts.

## Verification contract

Release status comes only from terminated current-source receipts in `evidence/final15`, `evidence/fresh15`, both supervisors and `evidence/FRESH_REBUILD_BLOCK15.json`. Each gate builds every production module in an empty object directory, checks direct source-facing interfaces, audits actual declarations and transitive axioms, replays substantive modules through `leanchecker`, and satisfies the complete negative-control manifest. The second gate starts from a separately extracted frozen source snapshot. Every production proof object must match byte for byte.

The foundational allowlist remains `propext`, `Classical.choice` and `Quot.sound`. Compilation uses one thread, warnings as errors, a 4,096 MiB internal Lean limit and a 45-second command wall limit. The whole-gate supervisor limit is 900 seconds. No separately imposed operating-system memory cap is claimed.

Prior blocks observed differing nonproduction `Audit.olean` files despite identical generated audit source and axiom records. The current comparison reports its own actual outcome. No cause is presumed and production identity has no exception. Failed imports, wrong diagnostics, timeouts and incomplete runs never count as successful mathematical rejection or proof completion.

## Delivery and limits

The current package preserves the prior complete archive and verifies its identity. Earlier history remains inside that archive; it has not been discarded or recertified against the new sources. The current block's source and evidence are directly accessible. The final ZIP receives an independent extraction and payload check, with temporary extraction using available memory-backed scratch space to avoid filling the main filesystem. This verifies delivery bytes, not another theorem replay.

Encoded operational permissions do not establish external moral or legal authority. No institutional deployment, communication protocol, empirical agent, hardware benchmark or Windows execution is claimed. The pinned upstream cache is reused, not rebuilt or independently authenticated. Four selected source results remain: Core 2.4, 2.5, 3.2 and 8.3. The next connected target is Core 8.3.
