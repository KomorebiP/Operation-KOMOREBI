# Block 15: completed current-source release results

**Machine-Native Reasoning · Formal companion 0.15.0 · Reviewed Core 0.2 · Komorebi P.**

Generated from both completed cumulative cold gates, their successful supervisor exits, and the completed extracted-source comparison. Core 8.2, a quotient preserving declared legal operations, is the one newly admitted source result.

| Check | Actual result |
|---|---:|
| Selected source results formalized | 23/27 |
| Authored theorem declarations | 1003 |
| New supporting theorem declarations | 50 |
| Authored declarations overall | 1528 |
| Elaborated theorem constants, including generated auxiliaries | 1935 |
| Transitive axiom-audited declarations | 2460 |
| Production modules compiled per gate | 64 |
| Substantive same-kernel replays per gate | 63 |
| Expected negative-control outcomes per gate | 152 |
| Newly added negative controls | 9 |
| Inputs unchanged before and after each gate | 371 |
| Predecessor substantive modules preserved | 60 |
| Predecessor files preserved, including source book files | 65 |
| Pinned upstream artifacts matched | 15852 |
| First cold gate | PASS, 714.644 seconds |
| Fresh extracted-source gate | PASS, 714.650 seconds |
| Cold-rebuild comparisons | 502, all passed |
| Production proof objects byte-identical | 64/64 |
| Historical Block 14 payload files retained and hash-checked inside original ZIP | 8258 |

The actual transitive axiom union is Classical.choice, Quot.sound, propext. Production compilations treat warnings as errors. Each of the 63 substantive modules was replayed through the same Lean kernel. Of the 152 controls, 151 deliberately false or unfinished fixtures reject for their stipulated diagnostics and 1 deliberately introduced axiom fixture compiles and is rejected by the axiom policy. Neither completed gate failed a required command contract or timed out.

The 50 added supporting theorem declarations formalize one source result and its extensions and examples. They are not 50 independent discoveries. All 60 predecessor substantive modules and the reviewed source book remain byte-identical.

## Mathematical outcome

For the source's finite state and action setting, a surjective state map supports quotient labels, enabled sets and legal successors exactly when equal fibres have equal labels, equal enabled sets and equal projected successors for every enabled action. The quotient protects both what a state reports and which actions the supplied model permits.

The quotient labels, enabled sets and **enabled-action successors** are unique. Arbitrary values used to pad a total step function on disabled actions are outside that uniqueness claim. The legal trace theorem preserves every finite legal action sequence and the complete associated label sequence, not just the final output or a tested trace horizon.

A predictive summary that merges states with different enabled actions can fail this contract even if its sensor predictions agree. The theorem formalizes declared operational permissions. It does not derive moral or external legal authority from an enabled-set label.

## Current authoring failures and corrections

The following is copied from the current pinned review notes. Historical preparation or authoring failures are not relabeled as new Block 15 failures.

Workspace maintenance had removed the earlier working tree. Initial creation of a helper directory failed with `No space left on device`, despite an earlier free-space observation. Later free space became available; no other task's files were deleted. One system-process diagnostic also failed with `fatal library error, lookup self` and provided no validation evidence. The saved Block 14 archive was recovered successfully and verified before use.

The old runtime path lacked its Lean executable. A second portable directory launched the exact compiler but its workspace manifest was empty or changing during apparent concurrent repair, producing JSON decoding errors. A stable surviving installation supplied the matching compiler and all nine pinned repositories. The owned facade points to that unchanged toolchain and package cache; matching adapter and inventory files are regular local copies. No shared runtime files were changed and no duplicate runtime was downloaded. `evidence/runtime15` retains the failed probes and successful identity checks. Startup identity alone is not proof verification; actual imported artifact hashes are checked by the complete gates.

The first main-proof compile failed because case analysis had already rewritten expressions that the proof then tried to rewrite again. A second attempt contained a redundant `rfl` after the goal was already closed. Removing the redundant tactic steps fixed the proof; the third compile passed. The additional exact raw-source bridge then compiled successfully on the fourth attempt. No theorem was weakened and no unfinished proof was admitted. Logs are in `evidence/development15/main_*`.

A preliminary trace-interface probe failed because its minimal imports did not provide `Finite`. The corrected probe imported `Fintype.Basic`. That probe used a hypothesized interface only and is explicitly not production proof evidence. Both actual production compiles against the real main module passed. The final trace compile records the final main-source hash. An initial informal count of 18 trace theorems was corrected to 15 by source inspection; release counts are computed from the actual source inventory.

The example module compiled on its first build and on its final recompile. The first API build failed because its imports lacked the `Fintype`-to-`Finite` instance. Adding `Mathlib.Data.Fintype.EquivFin` fixed that import/instance issue without changing hypotheses; subsequent API builds passed. All nine new negative fixtures passed their stipulated mathematical rejection diagnostics on their first preflight, with no bad imports or timeouts. The separate inherited-control preflight then passed all 143 expected outcomes against the new aggregate, with zero timeouts or import/name-resolution failures. Its custom-axiom fixture compiled and was correctly rejected by policy. That two-worker preflight took 124.13 seconds and preserved all inherited fixture hashes. Complete cold gates remain separate obligations with their own receipts.

## Preservation and assurance boundaries

The current gates use a 4,096 MiB internal Lean limit and record the preserved executable-location adapter. There is no separately imposed operating-system memory cap. The per-command wall allowance is 45 seconds. The first and fresh supervisors recorded wall limits of 900 and 900 seconds respectively. Runtime checks are recorded separately in `evidence/runtime15`.

Nonproduction object differences in this actual comparison: **Audit.olean**. Generated audit source and complete axiom records match. Every production proof object is byte-identical. No cause is guessed for a differing helper binary, and no production-object exception is allowed.

Both complete gates start from empty local object directories, with the second using a separately extracted frozen source snapshot. They reuse the same pinned upstream imports. Their measured gate durations are execution receipts, not performance claims. Upstream dependencies were hash-checked, not rebuilt from source or independently authenticated. Same-kernel replay is not an independent kernel implementation or peer review.

The filled legacy-v1 computation manifest also passed the current computation-audit skill validator, with the package root supplied for output-hash verification. Its complete result and legacy provenance limits are retained in `evidence/skill_manifest15.log`. This schema check does not independently authenticate the proof runs or supply a repository revision. The separate completed gate receipts bind the local inputs and command outcomes.

No physical sensor calibration, external legal-authority validation, hardware benchmark, Windows execution or hosted publication occurred. No runtime or standalone font binaries are shipped. Four selected source results remain outside this formalization. Core 8.3, safe continuation retaining an ending strategy, is the next connected target.

## Historical evidence layout

The complete original Block 14 archive remains byte-identical under `evidence/history/block14`. Its 8258 payload files were streamed through their frozen byte-length and SHA-256 checks during recovery and rechecked during packaging. Historical evidence is retained inside that original ZIP rather than expanded again into this release. Current source, documentation and checks, the essential predecessor receipt, and the new Block 15 evidence are directly accessible. The final outer payload count and the nested historical payload count are separate quantities.

## Current evidence

`evidence/final15/report.json`, `evidence/fresh15/report.json`, both supervisor receipts, `evidence/FRESH_REBUILD_BLOCK15.json`, `evidence/COMPUTATION_MANIFEST_BLOCK15.json`, `evidence/runtime15/recovery.json` and `evidence/COLD_SOURCE_BLOCK15.zip` bind the current source and actual outcomes. Final archive integrity is recorded separately beside the delivered ZIP, avoiding a circular archive checksum.
