# Independent clean replay harness review

Reviewer: `/root/limits_replay_audit`. Review date: 2026-10-12. Final verifier status: **PASS for the completed `clean_limits_01` cumulative replay and its independently reviewed terminal postflight**, using the exact helper revisions in `reviewed_helpers.json`. The preflight sections below are preserved as historical records; their pending execution and diagnostic gates are superseded by the terminal acceptance addendum. The separately owned theorem-to-prose verdict is outside this verifier review's scope.

## Normalized claim and scope

The finite verification claim is that the complete cumulative source graph, extended by the three regularization-limit modules, compiles from an empty project build under Lean 4.34.0-rc2, commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`, using one worker, warnings as errors, and `autoImplicit=false`; that the resulting imported project environment has no unsafe declaration and no axiom dependency outside `propext`, `Classical.choice`, and `Quot.sound`; that every new declaration has its complete elaborated type exported; and that every frozen control returns its prescribed success or intended rejection.

The accepted parent is `budget_v1.10.0/integration/runs/clean_budget_01`. I independently hashed its receipt, postflight, declaration report, and complete source tree. The observed parent has 151 compile targets, 148 production modules, 3 entrypoints, 4,935 distinct declarations, and 30 controls. The additive graph formed from the actual three new modules has 154 targets and 151 production modules. With the nine new controls and nine dependency pins checked at each endpoint, the expected command count is 231. The cumulative controls comprise 12 positive, 25 ordinary rejection, and 2 axiom-policy files.

This is exact symbolic Lean verification over the supplied formal declarations. It is not a numerical experiment, and no finite collection of controls proves the universal Hilbert-space theorems. The mathematical correspondence of the final declarations to every WR08, WR09, and WR16 clause belongs to the separate mathematical audit.

I used the `mathbox:proof-audit` workflow, read the raw implementations, and did not edit the assembler, verifier, shared helper, exporter, validator, production modules, or controls. Reviewer-owned bounded checks and their record are in `reviews/replay_audit/`.

## Dependency graph and acceptance obligations

The accepted parent receipt/postflight bind the inherited source and declaration inventory. The reviewed assembler produces a source-only additive snapshot and inventory. The reviewed verifier checks this inventory, compiles the complete source graph into fresh objects, runs the environment exporter and controls, and checks endpoint stability. The independently implemented postflight reconstructs command arguments and outcomes and validates the retained evidence against the frozen helper manifest. The final theorem-to-prose audit consumes the exact new declaration exports and frozen definitions.

| Obligation | Preflight result | Decisive implementation evidence |
| --- | --- | --- |
| Accepted parent and additive source ancestry | Passed | Fixed receipt/postflight/report hashes; complete inherited source inventory; no inherited module overwrite; exact additive combined root |
| Complete dependency-ordered graph | Passed | Local import existence/cycle checks and full root reachability; every project source is in the graph |
| Empty project build and strict compilation | Implementation passed; execution pending | New immutable attempt; empty build checked before Lean; one fresh `.olean` required per target |
| Complete cumulative axiom/safety policy | Implementation passed; execution pending | Actual imported environment enumeration and `collectAxioms` for every selected project constant |
| Every new elaborated type exported | Implementation passed; execution pending | New-module branch enables full names, universes, explicit arguments and proofs; nonempty/untruncated checks |
| 4,935 inherited declaration identities preserved | Implementation passed; execution pending | Exact sorted name/module/kind/safety/axiom-set comparison to accepted report |
| All command arguments, outcomes, and logs | Implementation passed; execution pending | Closed reconstructed command sequence, exact flags/cwd/targets, log hashes and expected markers |
| Source/helper/exporter/object endpoint bindings | Passed implementation review | Complete tree maps and final rechecks; copied exporter explicitly matches reviewed helper |
| Runtime/cache endpoint bindings | Passed implementation review and bounded checks | Toolchain `bin`/`lib` and all used dependency cache scopes, file contents and symlink target spellings |
| Independent postflight and reviewed helper freeze | Passed implementation review; execution pending | No imports of verifier code; review manifest and validator hashes required at entry and exit |
| Complete final theorem-to-prose correspondence | Out of this review's scope | Separate `WR08_WR09_WR16_MATH_AUDIT.md` review is required |

## Detailed implementation findings

**Source and build.** The assembler first verifies the accepted parent's fixed receipt and postflight hashes and their PASS/Lean-executed fields. Its parent source tree must match both accepted records, and its declaration report must match the accepted report hash. All new modules must be absent from the inherited tree. The only permitted inherited file changes are the combined root, exporter, control manifest, and module/type selection lists. The combined root is extended by imports of the new modules; the postflight separately reconstructs this exact extension from accepted parent bytes. Every other inherited source/control file must retain its original hash. Both assembler inputs are checked again at assembly completion.

The verifier copies the frozen assembly into a new immutable run, checks the copy and full graph, creates an empty build directory, and puts that directory first in `LEAN_PATH`. Only the selected external dependency caches follow it. It compiles every target in dependency order with `-j1 -DwarningAsError=true -DautoImplicit=false`. The full object set must be exactly the expected `.olean` files and must remain unchanged through exporter and control execution. The import scanner supports the ordinary one-line imports used by these reviewed sources; it is not a general Lean parser.

**Exporter scope and the printing change.** The exporter iterates `env.constants`, obtains each declaration's originating module, and selects the complete cumulative module list. This includes generated/private constants and all constant kinds rather than a handwritten public-theorem list. `collectAxioms name` executes before the type-printing branch. Every included declaration therefore receives the same transitive axiom and safety audit regardless of whether its type is printed in full, printed readably, or omitted. Lean and Python both reject unsafe declarations and every unapproved axiom.

New declarations always use the full printer (`pp.all`, full names, universes, explicit arguments, proofs). Existing selected declarations use readable types; other inherited type strings are omitted. This changes report presentation and size, not the cumulative axiom audit scope. The verifier and postflight require `type_mode=full`, a nonempty type, and absence of the `⋯` truncation marker for every new row. They check duplicate names, counts, production-module coverage and absence of outside-module rows. The sorted and new-only catalogues are compared to the actual report.

**Inherited identity means exactly the recorded fields.** The parent catalogue comparison covers name, originating module, kind, safety flag, and sorted axiom set. It does not compare elaborated type strings or kernel proof expressions. Readable inherited type strings must not be described as full inherited type re-exports. Continuity of inherited formal proofs is supported by unchanged inherited source bytes, the accepted source ancestry, and fresh strict recompilation with the stated runtime; no proof-expression byte identity is claimed. Postflight independently reconstructs the 4,935 parent identities from the fixed-hash accepted declaration report rather than trusting the newly assembled catalogue alone.

**Commands and controls.** Both implementations derive the complete command sequence: compiler version; initial dependency revisions and tracked cleanliness; every graph compile; exporter; every control; terminal dependency revisions and tracked cleanliness. Postflight also checks exact arguments, working directory, Lean flags, expected rejection flag, required markers, expected log names, and every log hash. Missing, extra, duplicated, or reordered commands/logs fail. Positive commands require exit 0. Rejections require exit 1, an error diagnostic, every case-sensitive intended marker, no timeout, and none of the prohibited import/name/resource/crash diagnostics. A killed or timed-out compiler cannot satisfy this control flow's ordinary PASS condition.

**Endpoint binding.** Source/control/ancillary files and exporter bytes are bound in both the frozen assembly and run source. The executable path adapter is bound separately. All compiler/toolchain libraries and every dependency cache actually present in `LEAN_PATH` are hashed before and after replay. File symlinks bind both target spelling and resolved file content; broken and directory symlinks are rejected. Git revision and tracked-cleanliness commands run at both endpoints. The postflight reconstructs the current runtime/cache inventory independently.

After its long runtime scan, postflight repeats checks on logs, axiom report, declaration catalogues, runtime snapshot record, compiler, adapter, original assembly, copied source, build, helper files, inventory, review manifest, validator, and run receipt. It also repeats the accepted parent's receipt/postflight/report and complete source-tree checks. My initial concern about that last parent recheck arose from an earlier source read; inspection of the frozen validator confirmed that the required terminal checks were already present. No helper correction was needed for that observation.

Assembler and verifier load `common.py` by compiling its source bytes directly. Timestamp-valid cached `.pyc` files therefore do not substitute unreviewed shared-helper code. Postflight requires its own exact independently reviewed hash and the complete reviewed script map, both before and after checking the run.

## Bounded checks and exporter compatibility evidence

`python limits_v1.11.0/reviews/replay_audit/preflight_check.py` passed. It parsed all four Python implementations, verified the three accepted parent evidence hashes and all 190 inherited source files, checked 4,935 distinct inherited names, formed the actual additive 154/151 graph in a temporary reviewer-owned tree, independently checked dependency-before-dependent order, and checked complete control manifest coverage. It also exercised the two runtime inventory implementations on ordinary files and file symlinks: their inventories agreed; changed file content and target spelling changed the inventory; broken and directory symlinks raised errors. These are focused finite checks, not a universal proof of Python correctness. Their exact helper/source/control identities are retained in `preflight_checks.json`.

I independently inspected the exact revised exporter probe `development/verifier/exporter_probe_02`, verified its source/log/report hashes, and compared its rows to the accepted parent report. It exited 0 after 92.633 seconds and returned all 4,935 parent identities and axiom sets unchanged, with 9 full, 384 readable, and 4,542 omitted type strings. All 9 exercised full types exactly match the accepted full-printer strings, are nonempty and untruncated. There were no unexpected axioms. The probe uses accepted cached project objects and is explicitly **not** the clean cumulative replay. Probe 01's unsupported option-scoping syntax was rejected during development and its retained failure was not promoted to acceptance.

## Control semantics checked before final integration

I read all nine final new fixture bodies and matched each to a source-identical development attempt and its actual hashed log. Final positive attempts 005, 008, 014, and 015 exited 0. Final rejection attempts 003, 007, 009, 012, and 013 exited 1 with precisely the intended mismatch. Earlier fixture attempts remain development history.

| New rejection | Observed intended mismatch |
| --- | --- |
| `NonpositiveParameter` | `0 ≤ α` supplied where objective comparison requires `0 < α` |
| `TwoSidedParameterLimit` | A theorem over `𝓝[>] 0` supplied as a theorem over `𝓝 0` |
| `ClosureIsNotAttainment` | Membership in `closure (Set.range T)` supplied where actual `Set.range T` membership is required |
| `NoiseDecayWithoutScaling` | Decay of `δ` supplied where decay of `δ/√α` is required |
| `SolverDecayWithoutScaling` | Decay of `ε` supplied where decay of `ε/α` is required |

These are API misuse controls. In particular, a failed type application alone is not an independently verified counterexample to every theorem omitting that hypothesis. The final positive noise/inexact fixture assumes the actual minimum-preimage equations and parameter convergence and invokes the complete parameter-choice theorems; it no longer assumes the exact bias convergence. The other positive fixtures cover full-filter composition, zero operator with positive residual floor, unique minimum preimage, eventual escape beyond every finite budget, the three-term pointwise certificate, and the sharp scalar coefficient. The 30 inherited fixtures remain source-bound to the accepted parent. Final integrated logs still need case-by-case inspection.

## Reviewed identities and trust boundary

| File or parent evidence | SHA-256 |
| --- | --- |
| `scripts/ExportAudit.lean` | `3a43043a86636d9bcba2ebd4f0c45984a277a879fa0438015a985554af62c748` |
| `scripts/assemble.py` | `a5837c6abb084c57cd950a4b390f39c5d8f9a6bc32ca105d0000b8cd839950b0` |
| `scripts/common.py` | `3bbd5ef1c468266d171f4dffda51774cde53ffd6c22eb547acb69c5e5ff37a3d` |
| `scripts/verify.py` | `45b3c91ffad26cacd1f5d29a8d71c391bc9897ce5866cad469560a2015fcb860` |
| `postflight/validate.py` | `e45d922f2d2a59e31a6388ac1f882d14e6b90804c1a2c093690db5ba7b590529` |
| Accepted parent receipt | `42ded58f00f816a1f7895039e6521b9e510f652baf9b6e86acd1eaa47d49f376` |
| Accepted parent postflight | `b1d47aeab1cbe838109a751edd9bba55a57593d9e9ce0e852dc0f8988983f2f2` |
| Accepted parent axiom report | `5bd29f14954a05a1d59135dbec241f180da8c98532715cd9d94b0570e3942cfd` |

The compiler/kernel, permitted axioms, host Python/Git/OS, and initial external compiled caches remain trusted. Cache content hashes do not authenticate the caches as products of their pinned source revisions. Tracked Git cleanliness does not cover untracked files; actual imported cache trees are separately hashed. Endpoint hashing is not an atomic snapshot and cannot detect transient changes restored before recheck. Receipts are integrity records, not cryptographic attestations that arbitrary fabricated records originated from genuine execution.

## Exact remaining gate

The helper implementation is accepted for the recorded revisions. The smallest outstanding execution implication is a terminal PASS from the fresh cumulative replay followed by the reviewed independent postflight, plus inspection of actual final rejection logs. The final imported declaration set and all complete new types must then feed the separate mathematical statement audit. No final new-declaration count or completed integrated-run PASS is asserted here. Any helper change requires renewed helper review and a new manifest; any production/control source change requires rechecking the affected source-dependent review before final acceptance.

## Terminal acceptance addendum — 2026-10-12

**PASS for the completed `clean_limits_01` cumulative replay and its independently reviewed postflight.** Primary verdict for this review's finite verification claim: **computationally verified for the exact bound source, helpers, controls, and trusted runtime described below**. The preceding preflight sections are preserved as history; their outstanding execution and diagnostic gates are discharged here. The separate theorem-to-prose review remains outside this verifier review's scope.

The accepted run used frozen assembly `wr08_wr09_wr16_01` and the exact originally reviewed helpers. It started at `2026-10-12T22:30:15.831097+00:00` and finished at `2026-10-12T22:43:12.937005+00:00`, after 777.106 seconds. The reviewed postflight finished at `2026-10-12T22:44:05.905685+00:00`. Both retained receipts are terminal PASS without a failure field. No final replay restart or helper/source substitution was needed. The preflight manifest is unchanged.

I ran the separate reviewer-owned command:

```text
python limits_v1.11.0/reviews/replay_audit/terminal_check.py --run limits_v1.11.0/integration/runs/clean_limits_01
```

It completed with exit 0 at `2026-10-12T22:44:49.932828+00:00` and wrote `reviews/replay_audit/terminal_checks.json`. This check does not execute Lean. It independently reconstructs the actual source/import/object inventories and the exact command sequence, compares every retained command and log, reconstructs inherited declaration identities directly from the fixed-hash accepted parent report, and checks all new type exports and evidence bindings. I then read each rejection diagnostic against the already reviewed source body. Neither an author's PASS label nor agreement between reviewers substitutes for those checks.

| Completed gate | Observed result |
| --- | --- |
| Empty project build and strict compilation | All 154 targets compiled: 151 production modules and 3 entrypoints; strict flags and intended compiler version/commit recorded |
| Complete command sequence | Exactly 231 unique commands with exact arguments, working directories, expected outcomes and no timeouts |
| Frozen source/control/ancillary inventory | All 203 files match run, assembly, inventory and postflight hashes; final new modules and controls also match preflight-reviewed identities |
| Inherited source ancestry | Accepted parent evidence hashes and all 190 source files unchanged; combined root is exactly the accepted root plus the three new imports |
| Project objects | Exactly 154 `.olean` files; postcompile, terminal receipt, actual build and postflight maps agree |
| Cumulative declaration policy | 4,982 distinct declarations; no unsafe row, no unexpected axiom, permitted union exactly `Classical.choice`, `Quot.sound`, `propext` |
| Inherited declaration identity | All 4,935 parent names retain originating module, kind, safety flag and sorted axiom set; no inherited row omitted or added |
| Complete new types | All 47 new declarations have nonempty, untruncated `full` types; new-only and sorted catalogues equal their rows in the actual report |
| Positive controls | All 12 exit 0 with empty diagnostic logs |
| Rejection controls | All 25 ordinary and 2 axiom-policy controls exit 1 with the prescribed markers and intended diagnostics |
| Runtime/cache endpoints | Reviewed postflight confirms the same 130,284-file runtime/cache inventory and all endpoint gates |
| Reviewed helper freeze | Original script map, exporter, validator and manifest hashes remain unchanged |

The reviewer reconstruction checked the runtime snapshot hash, file count, selected evidence bindings and successful reviewed postflight. It did not independently repeat the postflight's complete 130,284-file runtime byte scan. That scan was performed by the separately implemented validator whose source and exact hash were accepted in preflight. Its runtime snapshot hash also equals the accepted parent's snapshot hash. Compiler/cache authenticity and transient-change limitations remain exactly as stated above.

### New declaration scope and source identities

| New module | Exported declarations | Frozen source SHA-256 |
| --- | ---: | --- |
| `KomorebiSpace.RegularizationLimits` | 12 | `9a9bc073f605faa13dae5d42fa3a66f390cdf95c71241e2b25d6b3d07cc09cfd` |
| `KomorebiSpace.RegularizationNoiseLimits` | 27 | `8e5045c83611637d9212b9f2f3563b9bd2073c3f11fa3da67b1b7b053f5dab03` |
| `KomorebiSpace.RegularizationStrongLimit` | 8 | `f2960594f8112fb3f5f443b4059313c63642794c07fd3ad2ad3b2e9ccdb795cc` |

The 47 rows comprise 45 theorem constants and 2 definitions, including generated proof/equation constants. This is not a count of 47 separately stated public theorems. The complete new type strings contain 358,645 characters in total. The exporter exited 0 in 84.696 seconds. The current inherited types are readable or omitted according to the reviewed presentation policy; the complete inherited name/kind/safety/axiom comparison and unchanged source ancestry passed. No inherited proof-expression equality or full inherited-type re-export claim is made.

### Individual final rejection inspection

All paths below are beneath the run's frozen `source/tests/` tree. Every listed final log and source hash appears individually in `terminal_checks.json`; each log also matches the terminal receipt and postflight. The mismatch columns report the actual compiler diagnostic in the context of the fixture body.

| Fixture | Actual intended rejection |
| --- | --- |
| `budget/negative/DropBudgetPenalty` | Scalar penalty-free bound simplifies to `False` |
| `budget/negative/DropCandidateBudget` | Exact correction 1 violates the zero-budget obligation; `False` |
| `budget/negative/DropDataUncertainty` | Removing datum allowance demands an absolute difference 1 be at most 0; `False` |
| `budget/negative/DropDualNormRestriction` | Proposed scalar dual witness 2 fails the unit-norm obligation; `False` |
| `budget/negative/DropOperatorUncertainty` | Profiles are 1 and 0 while the claimed omitted-allowance bound is zero; `False` |
| `budget/negative/NegativeBudgetAttainment` | Negative-radius feasibility/minimizer application leaves `False` |
| `extension/negative/OmitParameterGain` | Normal residual without inverse-parameter gain is too small; `False` |
| `extension/negative/Placeholder` | Warnings-as-errors rejects `declaration uses sorry` |
| `extension/negative/ReverseDualInequality` | Scalar reversed dual inequality simplifies to `False` |
| `extension/negative/ZeroParameter` | Strict positivity needed for unique minimizer leaves `False` at zero |
| `extension/policy/CustomAxiom` | `custom axiom rejected by the extension policy` |
| `formal/negative/AllProtectedProblemsFeasible` | Protected identity example cannot remove the nonzero defect; `False` |
| `formal/negative/FalseArithmetic` | `decide` reports that `0 = 1` is false |
| `formal/negative/FinitePrefixesImplyPoint` | A finite `Partial` inhabitation is not an inhabitation of the global `Point` |
| `formal/negative/Placeholder` | Warnings-as-errors rejects `declaration uses sorry` |
| `formal/negative/UnnormalizedCertificate` | Zero covectors fail normalization; `False` |
| `formal/negative/WrongPreservedValue` | The scalar matrix-coordinate preservation claim simplifies to `False` |
| `formal/policy/CustomAxiom` | `AXIOM_POLICY_REJECTION` identifies dependency `injectedUnprovedExistence` |
| `limits/negative/ClosureIsNotAttainment` | `hclosure` has closure membership; theorem requires actual range membership |
| `limits/negative/NoiseDecayWithoutScaling` | `hnoise` gives `Tendsto δ`; theorem requires `Tendsto (fun i => δ i / √(α i))` |
| `limits/negative/NonpositiveParameter` | `hα` has `0 ≤ α`; theorem requires `0 < α` |
| `limits/negative/SolverDecayWithoutScaling` | `hsolve` gives `Tendsto ε`; theorem requires `Tendsto (fun i => ε i / α i)` |
| `limits/negative/TwoSidedParameterLimit` | Supplied theorem has source filter `𝓝[>] 0`; target asks for `𝓝 0` |
| `new/negative/WR01DropBudgetBound` | Constant realization 2 fails the budget-one assumption; `False` |
| `new/negative/WR01ShrinkPreservedBudget` | Norm-two certificate cannot be reduced to norm one; `False` |
| `new/negative/WR02ConvexEquality` | Convex half-line scalar equality is false; `False` |
| `new/negative/WR02MissingBudget` | Supplied implication still requires its finite-uniform-budget premise |

The diagnostic classes total 15 unsolved `False` obligations, 1 false arithmetic proposition, 7 intended type/application mismatches, 2 placeholder rejections and 2 axiom-policy rejections. None is a missing import, unknown identifier, crash, timeout, resource exhaustion or unrelated synthesis error. This closes the fixture-specific diagnostic review for these exact files; it does not assert that substring matching alone will certify arbitrary future fixtures.

### Terminal evidence identities

| Artifact | SHA-256 |
| --- | --- |
| `runs/clean_limits_01/receipt.json` | `1fbbed1df05f74aa0c6b967cd3828b3985c7b3c4bb533027636719640978bdd0` |
| `runs/clean_limits_01/postflight.json` | `37e7f09b13c7db2a9cb979f64402199d1a377a19f58ec698a605d7b78765bb9d` |
| `assemblies/wr08_wr09_wr16_01/inventory.json` | `a72c09207881b5cc11d55ea80b2274954c3f5c30d07dda063b74cd91a2ca22ca` |
| `reviews/reviewed_helpers.json` | `e6d587d06e07217af93b1d4aab773027468d7411399a460e77c05da6489464ea` |
| `runs/clean_limits_01/axioms.json` | `b6806e522fa0a562e91adfa3fcc3347401de7ffd7d21d7e0e5a90888d955b1f8` |
| `runs/clean_limits_01/new_declarations.json` | `2e4d1172858215855b559348a7885bdc95ad39a6c7589a959787013f63247abb` |
| `runs/clean_limits_01/declarations_sorted.json` | `094d3dbbac07bafa63b99b76056941b4e44b05659d7e221e903ca6efd6a429e4` |
| `runs/clean_limits_01/runtime_snapshot.json` | `9092d8caa0e9525e373b41568bf6836f38a5e4baf9a7668656614741af9596cd` |
| `reviews/replay_audit/terminal_checks.json` | `c3074b6f0010c813c34e5d1caef102f1ec5c6b13af9e95ba138e98c275d930eb` |

No remaining verifier or final-control gap was found for these bound inputs. Promotion of the mathematical checkpoint still requires the separately owned final theorem-to-prose verdict over the same source and report identities. The trust boundary, precise inherited-identity meaning, cache assumptions, and endpoint-hashing limitations remain in force.
