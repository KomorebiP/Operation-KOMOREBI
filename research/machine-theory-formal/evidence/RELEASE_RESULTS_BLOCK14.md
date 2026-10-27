# Block 14: completed current-source release results

**Machine-Native Reasoning · Formal companion 0.14.0 · Reviewed Core 0.2 · Komorebi P.**

Generated from both completed cumulative cold gates, their successful supervisor exits, and the completed extracted-source comparison. Core 8.1, target-relative joint reconstruction, is the one newly admitted source result.

| Check | Actual result |
|---|---:|
| Selected source results formalized | 22/27 |
| Authored theorem declarations | 953 |
| New supporting theorem declarations | 35 |
| Authored declarations overall | 1455 |
| Elaborated theorem constants, including generated auxiliaries | 1865 |
| Transitive axiom-audited declarations | 2367 |
| Production modules compiled per gate | 61 |
| Substantive same-kernel replays per gate | 60 |
| Expected negative-control outcomes per gate | 143 |
| Newly added negative controls | 8 |
| Inputs unchanged before and after each gate | 341 |
| Predecessor substantive modules preserved | 58 |
| Predecessor files preserved, including source book files | 63 |
| Pinned upstream artifacts matched | 15852 |
| First cold gate | PASS, 639.338 seconds |
| Fresh extracted-source gate | PASS, 639.326 seconds |
| Cold-rebuild comparisons | 467, all passed |
| Production proof objects byte-identical | 61/61 |

The actual transitive axiom union is Classical.choice, Quot.sound, propext. Production compilations treat warnings as errors. Each of the 60 substantive modules was replayed through the same Lean kernel. Of the 143 controls, 142 deliberately false or unfinished fixtures reject for their stipulated diagnostics and 1 deliberately introduced axiom fixture compiles and is rejected by the axiom policy. Neither completed gate failed a required command contract or timed out.

The 35 added supporting theorem declarations formalize one source result and its extensions and examples. They are not 35 independent discoveries. All 58 predecessor substantive modules and the reviewed source book remain byte-identical.

## Mathematical outcome

The source-facing theorem retains a finite-dimensional state space over a field. For actual linear record and target maps A and Q, a linear decoder D defined on the **full record space** satisfies Q = D.comp A exactly when ker A is contained in ker Q. The decoder is not merely defined on attainable records. The kernel condition makes the image-level definition independent of representatives, and the linear extension supplies a decoder on the whole codomain.

For the identity target, reconstruction is equivalent to injectivity of the record map. The kernel of a stacked record map is the intersection of the kernels of its components. Reconstruction is target-relative: unresolved nuisance directions are permitted when the target map ignores them. Stronger supporting library results do not silently expand the source-admitted finite-dimensional scope.

The theorem concerns accessible records and mathematical existence of a linear decoder. It does not send those records, establish truthful interpretation or permission to disclose them, or install an executable decoder at a fixed recipient. Those remain separate contracts. Exact examples are bound to actual linear maps, not substituted truth-table labels.

## Current authoring failures and corrections

The following is copied from the current pinned review notes. Historical Block 13 preparation or authoring failures are not relabeled as new Block 14 failures.

The main module's first authoring compile failed on quotient/range coercion transparency, an unavailable `LinearMap.rangeRestrict_apply` name, unused simplifier arguments and an existential-proposition normalization. The revised proof uses explicit type changes, the actual quotient equivalence lemma and `exists_prop`. The second authoring compile passed with warnings treated as errors. The theorem was not weakened and no unfinished proof was admitted. Logs are in `evidence/development14`.

The first example build failed on overaggressive product extensionality and characteristic-two normalization. Explicit pointwise extensionality and `decide` corrected it; the second build passed. Adding a bridge to the general field theorem caused a third build to hit Lean's deterministic heartbeat limit during type inference and fail a decoder rewrite. The fourth build exposed the missing `Field F₂` instance directly. Importing `Mathlib.Algebra.Field.ZMod` supplied the actual field structure, and the fifth build passed without increasing the heartbeat limit or weakening a theorem. Logs are in `evidence/development14`. These are development failures, not final gate successes or evidence against the source theorem.

The new source-facing API compiled on its first preflight. All eight new negative fixtures rejected for their required mathematical diagnostics on their first preflight, with no import failures or timeouts. The full inherited-fixture preflight also passed: the new aggregate compiled and all 135 existing contracts satisfied their required diagnostics or axiom-policy rejection, with no timeouts or import/name-resolution failures. Thus all 143 controls were exercised before the frozen cold gates. These rehearsals remain distinct from complete cold-build and kernel-replay evidence.

The first runtime-report preparation script assumed every manifest entry had a sha256 field. Directory entries do not, so it raised KeyError before producing the recovery report. The corrected script selects the six regular artifact files. The failure and successful recovery are both retained in `evidence/runtime14`. No compiler or runtime bytes were changed.

One documentation edit was rejected by the patch tool because it combined deletion and addition of the same path in one patch. It did not alter the review notes; a subsequent single-file replacement wrote the intended text. This was an editing error, not a failed mathematical check.

The current runtime is reused read-only with the previously established executable-location adapter and 4,096 MiB Lean internal memory limit. Recovery rechecks the compiler identity, all nine dependency revisions and selected artifact hashes. This does not redownload or rebuild upstream libraries. Earlier runtime and fixture failures belong to their preserved historical records and are not recounted as new Block 14 failures.

## Preservation and assurance boundaries

The current gates use a 4,096 MiB internal Lean limit and record the preserved executable-location adapter. There is no separately imposed operating-system memory cap. The per-command wall allowance is 45 seconds. The first and fresh supervisors recorded wall limits of 900 and 900 seconds respectively. Runtime checks are recorded separately in `evidence/runtime14`.

Nonproduction object differences in this actual comparison: **Audit.olean**. Generated audit source and complete axiom records match. Every production proof object is byte-identical. No cause is guessed for a differing helper binary, and no production-object exception is allowed.

Both complete gates start from empty local object directories, with the second using a separately extracted frozen source snapshot. They reuse the same pinned upstream imports. Their measured gate durations are execution receipts, not performance claims. Upstream dependencies were hash-checked, not rebuilt from source or independently authenticated. Same-kernel replay is not an independent kernel implementation or peer review.

The filled legacy-v1 computation manifest also passed the current computation-audit skill validator, with the package root supplied for output-hash verification. Its complete result and legacy provenance limits are retained in `evidence/skill_manifest14.log`. This schema check does not independently authenticate the proof runs or supply a repository revision. The separate completed gate receipts bind the local inputs and command outcomes.

No physical sensor calibration, communication implementation, hardware benchmark, Windows execution or hosted publication occurred. No runtime or standalone font binaries are shipped. Five selected source results remain outside this formalization. Core 8.2, the quotient preserving legal operations, is the next connected target.

## Current evidence

`evidence/final14/report.json`, `evidence/fresh14/report.json`, both supervisor receipts, `evidence/FRESH_REBUILD_BLOCK14.json`, `evidence/COMPUTATION_MANIFEST_BLOCK14.json`, `evidence/runtime14/recovery.json` and `evidence/COLD_SOURCE_BLOCK14.zip` bind the current source and actual outcomes. Final archive integrity is recorded separately beside the delivered ZIP, avoiding a circular archive checksum.
