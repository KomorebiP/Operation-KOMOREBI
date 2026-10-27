# Independent integrated-runner audit

**Verdict: PASS_BOUNDED_SOFTWARE_AUDIT.** No unresolved blocking issue was found in the frozen runner's design, source inventory, control identities, or the bounded tests described here. This review does not substitute for a completed fresh replay of the publication. The reviewer did not run the full project build.

The parent publication archive was independently hashed as `73e9c5caa36f4ba05029c01481b345ce24cf9b1905dfb012ed21dd4bcfe86dc0`. The reviewed source was frozen in `records/verifier_frozen_01.json`:

| File | SHA-256 |
|---|---|
| `runner.py` | `a60efb13a30bd50691dd4ae5506b9570d108b5e0a8ddf70043d7494d1437c3ca` |
| `Inventory.lean` | `bb38712843c3509a0fc9eeaca27de909661c59684e6445d347090d5baf301f15` |
| `control_manifest.json` | `7ab322b549532a248fcd777cf013c739ab8b90f4e24da86d294b4a739085565e` |
| `README.md` | `99c359392f67df5ae892371dcec3718f0c44ba657aaa663acc904b8d5349f430` |

All 60 source/control files matched the freeze before and after the final checks. Python bytecode under `__pycache__` is excluded, consistently with the runner's input inventory. The companion JSON records all reviewed file hashes, individual classifier tests, isolated Lean fixtures and resulting declaration inventories.

## Scope and implementation findings

The independently enumerated production source tree contains exactly 166 Lean files: 162 modules and four import roots. Every file is covered by the runner's dependency graph, is reachable from a root, and is assigned exactly one compilation command. The four roots are `KomorebiSpace`, `KomorebiSpaceCombined`, `KomorebiSpaceDiagonal`, and `KomorebiSpaceRegularization`. The lexical count is 1,859 explicit theorem/lemma declarations; this is distinct from the generated declaration inventory.

Every production target, declaration auditor, and control receives `-j1`, `-DwarningAsError=true`, and `-DautoImplicit=false`. The static source check rejects obvious policy weakening and forbidden production tokens. The runner creates a new output directory and source snapshot, directs all project objects to its initially empty build directory, replaces `LEAN_PATH` with that directory followed by pinned dependency caches, and removes `LEAN_SRC_PATH`. It does not use the previous project `.lake/build` tree. Imports are compiled in dependency order, and the resulting project object set must equal the target set.

The Lean auditor selects declarations using their recorded originating module, not their printed namespace. It examines all matching constants, including private and generated constants; records declaration kind and safety; rejects direct project axioms and unsafe declarations; and uses Lean's recursive `collectAxioms` machinery with the whitelist `propext`, `Classical.choice`, `Quot.sound`. The Python layer independently checks the resulting rows, unique names, module coverage, and whitelist.

The final receipt can become `PASS` only after all compilation and control checks succeed, exact command ordering is checked, and source snapshots, fresh objects, generated audit inputs, command logs, declaration evidence, installed compiler bytes, and dependency-cache bytes satisfy endpoint checks. Compiler failure, unexpected control results, timeouts, and exceptions retain a non-PASS receipt and produce a nonzero exit. Static validation is explicitly labeled `STATIC_VALIDATION_ONLY` with no Lean verdict.

The implementation uses Python's standard library, the installed Lake/Lean toolchain, and Git. Paths are derived from arguments and discovered environment values; no host-specific path or compatibility shim is embedded. Sequential compilation limits concurrent memory use without claiming a fixed memory bound.

## Control identities and intended outcomes

All 44 inherited cumulative controls were independently byte-compared with the original nested continuation archive, SHA-256 `6304d70013b0baf30619b7c724bef4710dbd085ee590b825f9e4eecf4fc375e6`. All eight inherited diagonal controls were independently byte-compared with the parent's embedded diagonal evidence archive, SHA-256 `fb1bc014fa980f0c47f81ac05d865187519584ae6ff9a6e1ca6545c295c11653`. Manifest control hashes and all 56 baseline-log hashes were also checked.

The complete manifest specifies 18 successful elaborations, 35 expected elaboration rejections, and three policy rejections. Two policy controls deliberately emit an embedded policy error. The diagonal project-axiom control elaborates successfully and is then rejected by the external axiom-policy check. The records preserve this distinction.

The four added controls have the advertised narrow scope:

| Control | Intended check |
|---|---|
| `PositiveInexactRate` | Applies the exact theorem with the rounded parameter, measured-data normal residual, tolerance budget, and explicit rate constant. |
| `RejectMissingSolverResidual` | Attempts to replace the measured-residual hypothesis with the scalar tolerance hypothesis; expects the application type mismatch at that argument. |
| `PositiveRangeObstruction` | Checks the actual diagonal operator's nonclosed range, closure/range witness, normalized coordinate vectors, and their image norms. |
| `RejectClosedRange` | Deletes the negation of the nonclosed-range conclusion; expects the resulting type mismatch. |

These controls check theorem interfaces and selected mutations. They do not establish an exhaustive mutation-testing result or replace the separate mathematical statement review.

## Bounded tests on the frozen files

1. **Historical/current diagnostics:** All 56 exact baseline logs were loaded independently from their recorded archives or current smoke-test records. The frozen classifier accepted each intended outcome.
2. **Classifier adversarial cases:** All 261 mutations were rejected: extra located errors, extra unlocated errors, timeouts, wrong exit statuses, and changed error positions. The classifier checks the complete ordered diagnostic list and required body markers, rather than accepting a required substring accompanied by unrelated errors.
3. **Private/generated declaration inventory:** A small core-only positive module compiled successfully and produced 23 provenance-matched declarations, including a private theorem, generated constructors/recursors/projections, injectivity facts, and pattern-match auxiliaries. The frozen auditor accepted it.
4. **Unused forbidden declarations:** Separate tiny modules containing an unused private axiom or an unused unsafe definition each compiled, then caused auditor exit 1 with the precise forbidden row recorded.
5. **Recursive foreign axiom:** A foreign axiom in a dependency propagated through a dependency theorem, private project theorem, and exported project theorem. The auditor excluded dependency declarations by provenance, retained both project declarations, recorded the foreign axiom for both, and rejected both.
6. **Output/exit behavior:** A static invocation returned exit 0 with `STATIC_VALIDATION_ONLY`, 166 targets, no commands, and `lean_executed=false`. A missing-toolchain invocation returned exit 1 and retained a `FAIL` receipt identifying the missing `lake` executable.

The isolated tests used the pinned Lean 4.34.0-rc2 compiler. This host's external `LD_PRELOAD` compatibility adapter was supplied only by the test environment. It is absent from the portable runner's source.

## Findings resolved before freeze

The first reviewed draft classified negative controls using required substrings plus an infrastructure-error blacklist. This could accept the intended failure together with an unrelated error. The frozen revision adds exact complete diagnostic identities; the 261 adversarial cases above exercise the correction.

The first inventory draft implicitly relied on the production imports to expose `Lean.Elab.Command`. A tiny core-only fixture exposed the missing import. The frozen inventory imports `Lean.Elab.Command` explicitly and all isolated cases execute directly against that final file.

## Remaining boundaries

The full 166-target/56-control fresh replay must be judged from its own final receipt and preserved logs. The tests here do not claim that replay already completed. Installed external caches are byte-bound and revision-checked, but are not rebuilt or authenticated by this runner. Endpoint equality does not detect transient changes restored before the terminal snapshot. Statement correspondence and mathematical correctness remain separate review obligations. None of these limits is concealed by the runner's README or receipt trust boundary.
