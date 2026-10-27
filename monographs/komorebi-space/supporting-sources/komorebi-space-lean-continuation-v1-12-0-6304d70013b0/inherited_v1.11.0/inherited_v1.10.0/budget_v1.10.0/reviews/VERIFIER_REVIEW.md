# Independent clean replay harness review

Review date: 2026-10-12. Reviewer: `/root/budget_replay_audit`. Status: **PASS for the exact helper revisions in `reviewed_helpers.json`**. This status approves the implementation for the intended replay; it does not assert that the integrated replay or its postflight has already completed.

## Contract and scope

The intended finite assertion is that the frozen cumulative Lean source tree compiles under Lean 4.34.0-rc2, commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`, with one worker, warnings treated as errors, and automatic implicit variables disabled; that all project declarations in the resulting imported environment satisfy the permitted-axiom and safety policy; that every declaration from the four budget modules has an exported full type; and that the complete frozen control inventory produces its prescribed success or rejection outcome.

The source checkpoint is the accepted `continuation/integration/runs/wr01_wr02_overlay_01/source` tree, whose receipt SHA-256 is `ed08da780d623b1b53936a80207a76f63b9fd3ca02fa8f43e47ee7ca5660467b`. I independently checked this receipt hash, its full source snapshot identity, and its 147-target/144-production-module graph. A temporary cumulative assembly using the actual four new modules gave 151 targets and 148 production modules. The expected control scope is 8 positive files, 20 compiler rejection files, and 2 axiom-policy files. With nine dependency pins checked before and after, the complete command count is 219.

The mathematics uses exact Lean proof terms over real complete Hilbert spaces; these are not floating-point numerical experiments. The harness checks the formal declarations actually supplied. Whether those declarations express every printed WR03–WR05 clause is a separate mathematical/type review.

Reviewed files: `integration/scripts/common.py`, `assemble.py`, `verify.py`, `ExportAudit.lean`, and `integration/postflight/validate.py`. I read the raw implementations and the target contract, inspected inherited and new control bodies, and inspected the exporter smoke evidence. I did not edit these helpers.

## Acceptance gates checked

**Fresh project objects.** Assembly copies the accepted source-only tree and adds modules without replacing inherited production files. The combined root imports the new modules. The graph rejects missing local dependencies, cycles, and production modules omitted from the combined root. The replay creates a new attempt and an initially empty build directory, then compiles every graph target in dependency order. The Lean search path starts with this fresh build and contains only the selected external caches afterward. It does not reuse the previous project's object directory. The object inventory must be exactly one `.olean` per target and must remain unchanged through the exporter and controls.

**Complete declarations, axioms, and types.** The exporter iterates the actual imported environment rather than a handwritten theorem list. Originating-module filtering includes project entrypoint declarations when present, private/generated declarations, definitions, and other constant kinds. `collectAxioms` traverses each declaration's dependencies. Both Lean and Python reject unsafe declarations or axioms outside `propext`, `Classical.choice`, and `Quot.sound`. Duplicate names, empty/inconsistent reports, omitted production modules, and outside-module rows are rejected. All declarations from every new module are selected for fully explicit type printing; empty types or the Lean truncation marker `⋯` are rejected. The sorted and new-declaration catalogues are checked against the actual report.

**Required commands and outcomes.** The replay constructs a closed expected command sequence. The independent postflight reconstructs it without importing the verifier, including exact targets, flags, working directory, initial and terminal Git commands, exporter, and every control. Missing, extra, duplicated, or reordered records and log files fail. Positive commands require exit code 0; rejection commands require exit code 1, no timeout, the expected error markers, and absence of the listed environment/resource failure diagnostics. A killed or failed compiler cannot produce ordinary PASS through the reviewed control flow.

**Source and helper identity.** Full copied and original source snapshots include controls, exporter, dependency pins, module lists, and ancillary inputs. Endpoint comparisons reject persistent changes and extra files. The exporter is explicitly matched to the reviewed helper hash. Assembler and verifier load `common.py` directly from source, avoiding unreviewed timestamp-valid `.pyc` execution. The postflight requires the independently accepted helper manifest and its own reviewed hash.

**Runtime identity.** The replay hashes the portable toolchain's `bin` and `lib` trees and every external cache directory actually used in `LEAN_PATH`, before and after execution. File symlinks bind both their target spelling and resolved contents; directory and broken symlinks fail. The preload adapter is separately bound. Dependency Git revisions and tracked cleanliness are checked at both replay endpoints. The postflight independently reconstructs the runtime scopes and hashes their current contents against the recorded snapshot. This checks persistent byte changes; it does not authenticate the cache objects as builds of the pinned sources.

**Postflight stability.** After its potentially long runtime scan, postflight rechecks command logs, the axiom report, declaration catalogues, runtime snapshot record, compiler, adapter, original assembly, source/build trees, helper revisions, validator, inventory, review manifest, and run receipt. Therefore a persistent edit during that scan cannot be silently accepted merely because an earlier check passed.

## Findings resolved before acceptance

| Finding | Accepted correction |
|---|---|
| Initial runtime coverage bound only the Lean executable and preload adapter; dependency source checks ran only before compilation. | Added complete selected toolchain/cache endpoint inventories and terminal Git revision/cleanliness commands. |
| The initial postflight recorded its current hash without requiring the reviewed validator revision. | Added `postflight_sha256` to the review contract and enforced it at entry and exit. |
| Normal Python imports could execute timestamp-valid cached helper bytecode outside the reviewed source inventory. | Assembler and verifier now compile and execute the bytes of `common.py` directly. |
| Copied exporter identity depended only on the reviewed assembler's behavior. | Verifier and postflight explicitly compare the snapshot exporter to its reviewed helper hash. |
| Initial postflight did not repeat all small evidence checks after the long runtime scan. | Added terminal log, audit, catalogue, runtime-record, adapter/compiler, and original-assembly checks. |

## Checks performed and control meaning

All four Python files parsed successfully. A temporary filesystem check exercised both runtime inventory implementations: they agreed on ordinary files and file symlinks, detected changed file bytes and changed symlink targets, and rejected broken and directory symlinks. The temporary graph check confirmed the actual cumulative 151/148 scope. These focused checks do not constitute exhaustive Python verification.

The exact exporter compatibility smoke at `integration/development/exporter_smoke_01` completed with exit code 0, seven declarations from one inherited module, permitted axioms only, and nonempty untruncated types for every row, including generated simplification declarations. I read the raw log/report and matched the exporter, log, and audit hashes. This is a compatibility smoke over existing objects, not the clean integrated replay.

I read all six new rejection logs in `development/controls/attempt_002`. Every source snapshot matches its frozen fixture, every log matches its receipt hash, and all six exit codes are 1 with the intended final `False` goal. The four positive files have exit code 0 and empty logs. This local receipt has SHA-256 `3f4872bf925baa172e42b59bb75c646966be01d494d52a4c305e6a57137b6978`; it uses development objects and is not substituted for the forthcoming clean replay.

| New rejection fixture | Intended rejected claim or application |
|---|---|
| `DropBudgetPenalty` | Removing the support penalty would assert 1 ≤ 0 for the scalar identity at datum and budget 1. |
| `DropCandidateBudget` | The exact correction 1 is not feasible at budget 0. |
| `DropDataUncertainty` | Deleting the datum allowance would assert an absolute difference of 1 is at most 0. |
| `DropDualNormRestriction` | The proposed dual witness 2 violates the unit-ball obligation. |
| `DropOperatorUncertainty` | Deleting the operator allowance would assert an absolute difference of 1 is at most 0. |
| `NegativeBudgetAttainment` | The minimizer theorem cannot accept a negative budget. |

The inherited fixtures remain bound to the accepted predecessor. They cover placeholder and custom-axiom rejection, false arithmetic, protected constraints, normalization, invalid finite-prefix use, regularization hypotheses, and WR01–WR02 budget misuse. Generic diagnostic matching is deliberately not treated as a semantic theorem: the final integrated rejection logs should still be inspected against these exact bodies. No missing import, unknown identifier, timeout, or crash is an acceptable substitute for the intended error.

## Reviewed identities

| File | SHA-256 |
|---|---|
| `scripts/ExportAudit.lean` | `cbb6a94adce34d0a55082f4964c604efc06037c261f5098e9bbd37b15788cb53` |
| `scripts/assemble.py` | `b6174e83931d1004354a8fcff2787049f9df7e8fe6c82f85ecdd3b466dfd4053` |
| `scripts/common.py` | `3bbd5ef1c468266d171f4dffda51774cde53ffd6c22eb547acb69c5e5ff37a3d` |
| `scripts/verify.py` | `dce701d05fbe8e0d3d0cada7e5525c1e587f5ce2e25d9182c39c6d0caf25294b` |
| `postflight/validate.py` | `c6c01c72a4e95e085c75e50e278293b68032912162e1ae55d97e566a0b02adfa` |

## Limits and required terminal follow-up

The compiler/kernel, permitted axioms, host Python/Git/OS, and the initial external compiled-cache contents remain trusted. Caches are not rebuilt from source. Git cleanliness ignores untracked files; the actual imported cache trees are separately content-bound. Hash records are integrity evidence, not signatures proving that an arbitrary hand-authored receipt came from a genuine execution.

Endpoint hashing is not an atomic filesystem snapshot and cannot detect transient changes restored before recheck. The import scanner supports the one-line import form used by the reviewed sources; it is not a complete Lean parser. Type export completeness concerns the imported declarations from the selected modules, and does not establish correspondence to prose by itself. Finite boundary controls do not prove universal mathematical claims.

Acceptance of the completed mathematical checkpoint still requires the clean integrated receipt to reach terminal PASS, the independent postflight to reach PASS using this review manifest, and inspection of the final integrated rejection diagnostics. A timeout, resource exhaustion, or environment error means that execution was inconclusive or failed; it is not a mathematical counterexample. No final integrated declaration count or completed-run PASS is asserted in this preflight helper review.

## Terminal acceptance addendum — 2026-10-12

**PASS for the completed `clean_budget_01` replay and its independent postflight, within the trust boundary above.** The preceding sections preserve the preflight review. Their pending execution obligations are discharged by this addendum.

The run used frozen assembly `wr03_wr05_01` and the original accepted helpers. It completed at `2026-10-12T21:46:58.872496+00:00`, after 1,096.327 seconds. The prescribed independent postflight completed at `2026-10-12T21:48:49.541108+00:00`. Both receipts have terminal PASS and no failure field. The original helper review manifest was retained unchanged so that the postflight's review binding remains valid.

| Completed gate | Observed result |
|---|---|
| Command inventory | Exactly 219 unique commands, all with their prescribed outcomes and no timeouts. |
| Clean compilation | All 151 targets compiled; 148 production modules and 3 entrypoints. |
| Preserved source and objects | 190 source/control/ancillary files and exactly 151 project objects match their recorded hashes. |
| Cumulative declaration audit | 4,935 declarations; no unsafe declaration or unapproved axiom. |
| New declaration types | All 63 new declarations have nonempty, untruncated full types. |
| Controls | 8 positive files, 20 compiler rejection files, and 2 policy rejection files completed. |
| Runtime preservation | Postflight confirmed the recorded 130,284-file toolchain/cache inventory and endpoint identity. |

I independently compared the terminal receipt, assembly inventory, unchanged helper manifest, validator hash, complete source/object inventories, and every command-log hash to the postflight bindings. I also checked the actual declaration reports against the predecessor: all 4,872 inherited names retain their module, kind, safety flag, and axiom set; the set difference is exactly the 63 declarations from the four new modules. The permitted cumulative axiom union remains `Classical.choice`, `Quot.sound`, and `propext`.

| New module | Exported declarations |
|---|---:|
| `KomorebiSpace.BudgetProfile` | 29 |
| `KomorebiSpace.BudgetProfileGeometry` | 8 |
| `KomorebiSpace.BudgetDuality` | 17 |
| `KomorebiSpace.BudgetRobustness` | 9 |

These 63 rows comprise 60 theorem constants, including generated proof/simplification constants, and 3 definitions. They are not 63 separately stated public theorems. Their exported types contain 1,608,171 characters in total, and every row satisfies the nonempty/untruncated check.

I read all 22 final rejection logs individually. The six budget controls produced the intended `False` obligations described in the earlier table. The inherited logs likewise reject the actual frozen misuse rather than an unrelated parser, import, identifier, or resource failure:

| Diagnostic class | Files | Observed meaning |
|---|---:|---|
| Unsolved `False` obligation | 15 | The stated scalar bound, protected constraint, normalization, parameter condition, or budget strengthening is false at the fixture's values. |
| False arithmetic | 1 | `decide` identifies `0 = 1` as false. |
| Type mismatch | 2 | A finite partial point is not a global point; the WR02 implication still requires its uniform-budget premise. |
| Placeholder rejection | 2 | Warnings-as-errors rejects a declaration using `sorry`. |
| Axiom-policy rejection | 2 | The specified policy message rejects the injected unapproved axiom. |

All eight positive files exited successfully. All 22 rejection files exited with code 1, and their retained logs match the terminal receipt and postflight. This closes the fixture-specific diagnostic-review obligation for this run; it does not turn the generic marker matcher into a proof of arbitrary future control semantics.

### Withdrawn performance proposal

A prospective change to reduce full pretty-printing of inherited types was discussed while the exporter appeared to be active. Before any helper or production/control source was changed, inspection of the actual command receipt showed that the exporter had already completed normally: exit code 0, 385.582 seconds, and no timeout. The proposed optimization was therefore withdrawn and the original reviewed replay continued through all controls and terminal checks. No interrupted replay or mathematical failure should be inferred from that proposal. The accepted evidence is the unchanged original `clean_budget_01` execution, with full printing retained for its originally selected inherited types as well as all new declarations.

### Terminal evidence identities

| Artifact | SHA-256 |
|---|---|
| `runs/clean_budget_01/receipt.json` | `42ded58f00f816a1f7895039e6521b9e510f652baf9b6e86acd1eaa47d49f376` |
| `runs/clean_budget_01/postflight.json` | `b1d47aeab1cbe838109a751edd9bba55a57593d9e9ce0e852dc0f8988983f2f2` |
| `assemblies/wr03_wr05_01/inventory.json` | `b04f4ee60be32182d1bb74024c75ab64aad29c0ac5f563c7fcb45e5e5ee3606a` |
| `reviews/reviewed_helpers.json` | `f9dd68dbadabed2a1ba92d5cd0d4ebbd5801ff3a6b2777ccdf16efaa7566c1e1` |
| `runs/clean_budget_01/axioms.json` | `5bd29f14954a05a1d59135dbec241f180da8c98532715cd9d94b0570e3942cfd` |
| `runs/clean_budget_01/runtime_snapshot.json` | `9092d8caa0e9525e373b41568bf6836f38a5e4baf9a7668656614741af9596cd` |

The implementation and its completed finite verification assertion are accepted for these bound inputs. The separate theorem-to-prose review, compiler/cache trust, endpoint-hashing limitations, and nonclaims stated above remain in force.
