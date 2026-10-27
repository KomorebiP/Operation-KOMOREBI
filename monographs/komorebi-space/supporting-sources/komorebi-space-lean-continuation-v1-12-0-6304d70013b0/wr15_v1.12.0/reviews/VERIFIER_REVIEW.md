# Independent WR15 verification-harness and terminal-evidence review

Reviewer: `/root/wr15_replay_audit`. Date: 2026-10-13. **PASS for the completed `clean_wr15_01` cumulative replay, independently reviewed terminal postflight, independent terminal evidence reconstruction, and all actual final control diagnostics.** Primary verdict: **computationally verified only in the stated range**, namely the exact source graph, helpers, controls and trusted runtime bound below. The preflight sections are preserved as history; their execution and diagnostic gates are superseded by the terminal acceptance addendum. The separate theorem-to-prose verdict is outside this review. The helper manifest remained frozen throughout.

## Claim, scope and dependency graph

The finite verification claim is that the complete inherited Lean source graph plus `KomorebiSpace.CoordinateBasisChange` and `KomorebiSpace.CoordinateCovector` compiles from an empty project object directory under Lean 4.34.0-rc2, commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`, with one worker, warnings as errors and `autoImplicit=false`; the imported cumulative environment has no unsafe declaration and no axiom dependency outside `propext`, `Classical.choice`, `Quot.sound`; every declaration originating in either new module receives a complete elaborated type export; every frozen inherited and new control has its intended outcome; and the recorded endpoints preserve the bound inputs and outputs.

This is exact symbolic verification of these formal declarations. It does not prove that their hypotheses and conclusions match every WR15 source clause. That source-specific correspondence belongs to the separately owned mathematical audit. It also does not turn finite misuse controls into universal counterexample proofs.

The accepted parent is recovered at `recovery/v1.11.0/Komorebi_Space_Lean_Continuation_v1.11.0/limits_v1.11.0/integration/runs/clean_limits_01`. Its fixed receipt, postflight, report and source inventory feed the additive assembler. The source-only assembly and exact helper map feed the clean verifier. That verifier feeds the independently implemented terminal validator. This reviewer will reconstruct the actual terminal evidence independently, and the mathematical reviewer consumes the same new full-type catalogue. No terminal PASS label alone discharges a downstream review obligation.

## Implementation obligations

| Obligation | Preflight finding |
| --- | --- |
| Accepted parent and additive ancestry | Passed: three exact parent evidence hashes; complete 203-file source map; 154 targets, 151 production modules, 39 controls and 4,982 distinct inherited declarations |
| Complete local import graph | Passed implementation: all local imports exist, cycles rejected, every production source reachable from combined root, dependency-before-dependent compile order |
| Empty build and strict compilation | Passed implementation; actual WR15 execution pending |
| All declarations audited | Passed implementation: imported environment enumeration, originating-module selection, `collectAxioms` for every included constant before type-presentation selection |
| Every new complete type | Passed implementation: all new-module rows use full printing, require nonempty strings and reject the ellipsis marker |
| Inherited declaration preservation | Passed implementation: exact name/module/kind/unsafe/sorted-axiom identities reconstructed from fixed parent report |
| Exact commands and controls | Passed implementation: command arguments, order, cwd, flags, markers, outcomes, log names and hashes reconstructed; all frozen `.lean` control paths covered |
| Endpoint source/helper/object/runtime bindings | Passed implementation and focused bounded runtime-inventory tests |
| Prior independent helper review | Passed implementation: reviewed hash manifest and validator pinned before Lean, review timestamp precedes run start, same identities checked at endpoints/postflight |
| Actual final rejection diagnostics | Pending actual clean run and case-by-case reading |
| WR15 theorem-to-prose correspondence | Outside this review; separate mathematical audit required |

## Raw implementation findings

I read the inherited raw assembler, common helper, verifier, exporter and postflight, then inspected every candidate diff. I did not edit production modules, controls or integration helpers. Candidate `common.py` only removes an unused archive constant. The exporter is byte-identical to the accepted parent's reviewed exporter.

The assembler checks parent receipt and postflight hashes and acceptance fields, hashes all inherited source/control bytes, derives the graph, checks all 39 inherited control specifications and reconstructs 4,982 declaration identities. The two new module names are fixed. No inherited module can be overwritten. Allowed ancillary updates are enumerated: combined root, exporter, control manifest, new/type/wanted module lists, and `parent_declarations.json`. This last catalogue exists in v1.11 and is deliberately refreshed from the accepted v1.11 report; the postflight independently reconstructs it rather than treating the permitted overwrite as evidence. All other inherited source/control bytes remain equal. The exact combined-root extension is reconstructed independently. The assembler rechecks parent and overlay inputs before completion.

Recovered absolute locations are recorded in the new assembly inventory. The original accepted receipt and postflight remain hash-bound, with their original historical paths preserved. The validator reads the recovered parent through the new inventory's path, verifies the old hashes, and compares historical path fields to the untouched old receipt. No old receipt is edited to make a relocated path appear current.

The verifier creates a new numbered immutable attempt, copies and checks the frozen assembly, requires an empty build directory, and places that directory first in `LEAN_PATH`, followed only by available pinned external dependency caches. Every target compiles with `-j1 -DwarningAsError=true -DautoImplicit=false`. Exactly one expected `.olean` per target is required; the final build map must equal the postcompile map. Both shared-helper users compile `common.py` directly from reviewed source bytes, preventing a timestamp-valid cached `.pyc` from substituting helper code.

The exporter enumerates `env.constants` and selects declarations by originating module, including private/generated constants and all constant kinds. It collects transitive axioms for every selected declaration before choosing full/readable/omitted type presentation. Thus omission of inherited type strings does not narrow the cumulative safety or axiom audit. Both Lean and Python reject unsafe declarations or any axiom outside the permitted set. Every declaration from a new module uses `pp.all`, full names, universes, explicit arguments and proofs. New-only and sorted report catalogues are checked against actual report rows. No full inherited-type or proof-expression equality is claimed: inherited equality covers exactly name, module, kind, safety and sorted axiom set, with unchanged source and fresh strict recompilation supporting continuity.

The verifier and independent postflight reconstruct the complete command sequence: version; initial revision and tracked-cleanliness commands for each dependency; all graph compiles; exporter; every control; terminal revisions and tracked cleanliness. They reject absent, extra, duplicate or reordered labels and logs. The postflight also checks exact argument vectors, cwd, flags, log hashes, expected-rejection flags and intended markers. A rejection must exit 1 without timeout, contain an error and all intended markers, and avoid import, missing-symbol, object-load, synthesis, crash and resource diagnostics. These marker checks still require final human-readable fixture-specific diagnostic inspection.

Source/control/ancillary bytes, assembly, helpers, copied exporter, object files, compiler, path adapter, runtime/cache trees and source pins are bound at endpoints. Runtime scopes cover toolchain `bin`/`lib` and every external cache included in `LEAN_PATH`. File symlinks bind both link target spelling and resolved contents; broken and directory links fail. After its runtime scan the postflight rechecks logs, audit/catalogues, runtime record, compiler/adapter, both source snapshots, parent evidence/source tree, build, helper map, inventory, review manifest, validator and receipt.

The import and source-token scanners are appropriate for the inspected ordinary one-line-import project sources; they are not full Lean parsers. Lean elaboration/kernel checking and the all-constant axiom/safety audit are separate gates. Tracked Git cleanliness does not cover untracked files; used cache contents have a separate inventory.

## Bounded evidence and frozen identities

`python wr15_v1.12.0/reviews/replay_audit/helper_checks.py` completed with exit 0 and retained `helper_checks.json`. This check parses all Python implementations, independently checks the three fixed parent hashes and all 203 inherited source files, counts 4,982 distinct declarations, checks the accepted complete dependency-ordered graph, and exercises both runtime-inventory implementations on normal files and file symlinks. They agree; changed contents/target spelling change the result; broken/directory symlinks raise errors. These focused finite checks do not prove arbitrary Python correctness and do not execute Lean.

| Artifact | SHA-256 |
| --- | --- |
| `scripts/ExportAudit.lean` | `3a43043a86636d9bcba2ebd4f0c45984a277a879fa0438015a985554af62c748` |
| `scripts/assemble.py` | `4aec63eb10900e7a1d1993badc7ae24ea14c60b77e8fbf1ef59dbe8cf0923e25` |
| `scripts/common.py` | `a43f1ac66e2d0a2f132b36cc005c6dd355cffa1e8034b1ea91609b50e37b0973` |
| `scripts/verify.py` | `fd41630d9f5b8ba43d8cfb4dd9db13b024a551141d9b12ebaf982f45092ed40f` |
| `postflight/validate.py` | `6ca37b2fd44af38ffd1488ea2618fcf18896d7384a990d9a269b102c058d90a4` |
| Accepted parent receipt | `1fbbed1df05f74aa0c6b967cd3828b3985c7b3c4bb533027636719640978bdd0` |
| Accepted parent postflight | `37e7f09b13c7db2a9cb979f64402199d1a377a19f58ec698a605d7b78765bb9d` |
| Accepted parent report | `b6806e522fa0a562e91adfa3fcc3347401de7ffd7d21d7e0e5a90888d955b1f8` |

## Trust boundary and exact remaining implication

The Lean compiler/kernel, permitted axioms, host Python/Git/OS, and initial external compiled caches remain trusted. Cache bytes are pinned but are not authenticated as the products of their pinned Git sources. Endpoint hashing is non-atomic and cannot detect changes restored before a recheck. Receipts are integrity records, not cryptographic attestations that fabricated records originated in execution. Shared-model errors remain possible despite task separation.

At this preflight stage, the strongest verdict was that the exact helper implementation passed independent review and its stated bounded checks; the new clean replay claim was **incomplete pending actual execution**. The next required gates were final source/control identity review, actual 156-target/153-production cumulative replay, independent terminal postflight, reconstruction of terminal command/report inventories and reading every actual rejection diagnostic. A helper change requires renewed review and a new frozen manifest. The separate mathematical audit must establish WR15 correspondence over those same final source and report identities.

## Source/control preflight addendum — 2026-10-13

The source/control identity gate is now discharged for `replay_audit/preflight_checks.json`, SHA-256 `c51126954300ea0db406dba3f8c5f7c03690730b7d09547856255006aad6cf17`, recorded before the WR15 clean run. All eight files of the overlay match the root's frozen overlay map. The reviewer independently constructed the additive import graph and root reachability from raw source: 156 compile targets, 153 production modules, three entrypoints. There are 44 cumulative controls: 14 positive, 28 ordinary rejection and two axiom-policy fixtures. Nine pinned dependencies checked at both endpoints yield exactly 238 commands. The helper manifest remains unchanged.

The frozen production identities are `CoordinateBasisChange.lean` SHA-256 `964ed871bf33db57c854b653125b9bf92416eefb5bc5df40877cd909ef366c07` and `CoordinateCovector.lean` SHA-256 `151661fac5f9ef5e2212ef41d76bf179299b5da4c5df10bf07844f18e04decfe`. Their theorem-to-prose review is separate. I read all five new fixture bodies and all 27 inherited rejection/policy bodies. Every new fixture was matched to its actual retained development source and hashed diagnostics. New fixture outcomes were not inferred from a status label.

| New fixture | Reviewed development evidence and intended final diagnostic |
| --- | --- |
| `positive/NonorthogonalTransport` | Attempt 009 exits zero with empty diagnostics. The concrete invertible shear/scale computes covector `(2,1)`, raw squared Euclidean size 5, and inverse-Gram scalar 1. |
| `positive/HilbertBoundaryCases` | Boundary attempt 001 exits zero with empty diagnostics. The full scalar basis vector 2 has Gram 4; at parameter −2 the actual Hilbert gradient is −1, equation covector −2, inverse-Gram scalar 1 and reconstructed gradient −1. An actual empty full Euclidean basis gives zero norm and scalar for arbitrary parameter. |
| `negative/RawCovectorNorm` | Attempt 006 exits 1 at an unsolved `False`: the raw covector square 5 cannot equal original squared norm 1. |
| `negative/ProperSubspaceCertificate` | Attempt 007 exits 1 at an unsolved `False`: the missed full residual has squared norm 1, which a zero coordinate certificate cannot bound by 0. |
| `negative/SingularGram` | Attempt 008 exits 1 at an unsolved `False`: redundant columns give Gram determinant zero, not a unit. |

The development logs contain no unrelated errors. Earlier rejected development attempts remain historical and were not promoted to acceptance. These three negative fixtures are explicit elementary countermodels to the proposed invalid simplifications; they do not claim to exhaust every possible weakened theorem. The final clean run must still execute and reproduce their intended diagnostics. Complete development source/log bindings are in `replay_audit/control_development_checks.json`.

A separate read-only review of the reviewer-owned terminal reconstruction script identified missing comparisons for frozen control specifications, log symlinks, some exact record fields and catalogue byte hashes. Those checks were added before execution. This changed only reviewer-owned code; integration helper hashes and their manifest are untouched. The terminal script remains non-executed at this preflight checkpoint.

## Terminal acceptance addendum — 2026-10-13

**PASS for the actual completed `clean_wr15_01` replay and its bound terminal evidence.** No terminal restart or source/helper substitution occurred. The clean run started at `2026-10-13T00:40:30.142116+00:00` and finished at `2026-10-13T00:53:09.678162+00:00`, after 759.536 seconds. The reviewed postflight finished at `2026-10-13T00:53:49.160866+00:00`. Both records are terminal PASS without a failure field. The original helper manifest and separate source/control preflight remain unchanged.

I executed the reviewer-owned reconstruction command after both terminal records existed:

```text
python wr15_v1.12.0/reviews/replay_audit/terminal_check.py --run wr15_v1.12.0/integration/runs/clean_wr15_01
```

It exited zero at `2026-10-13T00:55:09.087788+00:00`. It does not execute Lean and does not import verifier or postflight code. It independently reconstructed the source/import/object inventory, exact command sequence and arguments, frozen new control specifications, log names/outcomes/hashes, inherited identities from the fixed parent report, all new full-type rows, catalogues and record bindings. It additionally repeated the complete runtime/cache content and symlink scan and rechecked the other endpoints afterward. The retained console is `replay_audit/terminal_check.console.log`; its structured record is `replay_audit/terminal_checks.json`. I read every actual final rejection diagnostic in the context of the already reviewed fixture body.

| Completed gate | Observed result |
| --- | --- |
| Empty project build and strict compilation | All 156 targets compiled: 153 production modules and three entrypoints; exact strict flags and expected Lean version/commit |
| Complete command evidence | Exactly 238 unique commands, with reconstructed arguments/cwd/order/expectations; all accepted, no timeout |
| Frozen source/control/ancillary inventory | All 210 files match actual run, assembly, receipt, postflight and inventory; new files match frozen preflight |
| Inherited source ancestry | All 203 accepted parent source files remain bound; permitted ancillary updates reconstructed; combined root is precisely parent bytes plus the two imports |
| Project object inventory | Exactly 156 `.olean` files; postcompile, final receipt, actual build and postflight maps agree |
| Cumulative declaration policy | 5,048 distinct declarations; no unsafe row or unapproved axiom; allowed union exactly `Classical.choice`, `Quot.sound`, `propext` |
| Inherited declaration identity | All 4,982 parent identities preserved in name/module/kind/safety/axiom-set fields; none omitted or added |
| Complete new types | All 66 new declarations have nonempty, untruncated `full` types and agree with the new-only/sorted catalogues |
| Positive controls | All 14 exit zero with empty diagnostic logs |
| Rejection/policy controls | All 28 ordinary and two policy controls exit 1 with exactly their intended diagnostic class |
| Runtime/cache endpoints | Reviewer independently reconstructed the same 130,284-file byte/symlink inventory as receipt and reviewed postflight; its serialized snapshot is byte-identical to the accepted parent snapshot |
| Reviewed helper freeze | Four-script map, exporter, validator and prior manifest unchanged; the prior review timestamp precedes execution |
| Historical record preservation | Accepted v1.11 receipt, postflight, report and source bytes retain their exact hashes; historical absolute paths were not rewritten |

The two new originating modules contribute 24 declarations from `CoordinateBasisChange` and 42 from `CoordinateCovector`: 58 theorem constants and eight definitions in total, including generated/private constants. This is not a claim of 66 separately named public theorems. Their full type strings contain 13,588,234 characters. The actual exporter exited zero in 101.401 seconds. Existing types remain readable or omitted according to the reviewed presentation policy; no full inherited-type re-export or proof-expression identity is claimed.

### Individual final rejection inspection

Each path is beneath the final run's `source/tests/` tree. Every source hash, final log hash and complete diagnostic is retained individually in `terminal_checks.json` and agrees with the receipt/postflight. These are the actual final messages, not reused development outcomes.

| Fixture | Actual intended rejection |
| --- | --- |
| `budget/negative/DropBudgetPenalty` | Omitting the scalar penalty demands `1 ≤ 0`; unsolved `False` |
| `budget/negative/DropCandidateBudget` | Exact correction 1 violates zero candidate budget; unsolved `False` |
| `budget/negative/DropDataUncertainty` | Omitting datum allowance demands absolute difference 1 be at most 0; unsolved `False` |
| `budget/negative/DropDualNormRestriction` | Dual witness 2 fails the unit-norm obligation; unsolved `False` |
| `budget/negative/DropOperatorUncertainty` | Profiles 1 and 0 cannot satisfy omitted-allowance bound zero; unsolved `False` |
| `budget/negative/NegativeBudgetAttainment` | Negative radius cannot satisfy minimizer feasibility; unsolved `False` |
| `extension/negative/OmitParameterGain` | Normal residual without inverse-parameter gain is too small; unsolved `False` |
| `extension/negative/Placeholder` | Warnings-as-errors rejects `declaration uses sorry` |
| `extension/negative/ReverseDualInequality` | Reversed scalar dual inequality is false; unsolved `False` |
| `extension/negative/ZeroParameter` | Zero parameter fails strict positivity for unique minimizer; unsolved `False` |
| `extension/policy/CustomAxiom` | Explicit `custom axiom rejected by the extension policy` |
| `formal/negative/AllProtectedProblemsFeasible` | Protected identity cannot remove the nonzero identity defect; unsolved `False` |
| `formal/negative/FalseArithmetic` | `decide` reports that `0 = 1` is false |
| `formal/negative/FinitePrefixesImplyPoint` | A finite-prefix `Partial` inhabitant does not inhabit global `Point`; type mismatch |
| `formal/negative/Placeholder` | Warnings-as-errors rejects `declaration uses sorry` |
| `formal/negative/UnnormalizedCertificate` | Zero covectors fail normalization; unsolved `False` |
| `formal/negative/WrongPreservedValue` | Scalar coordinate preservation equation is false; unsolved `False` |
| `formal/policy/CustomAxiom` | `AXIOM_POLICY_REJECTION` identifies dependency `injectedUnprovedExistence` |
| `limits/negative/ClosureIsNotAttainment` | Closure membership supplied where actual range membership is required |
| `limits/negative/NoiseDecayWithoutScaling` | Decay of `δ` supplied where decay of `δ / √α` is required |
| `limits/negative/NonpositiveParameter` | `0 ≤ α` supplied where `0 < α` is required |
| `limits/negative/SolverDecayWithoutScaling` | Decay of `ε` supplied where decay of `ε / α` is required |
| `limits/negative/TwoSidedParameterLimit` | Source filter `𝓝[>] 0` supplied as source filter `𝓝 0` |
| `new/negative/WR01DropBudgetBound` | Constant realization 2 violates budget one; unsolved `False` |
| `new/negative/WR01ShrinkPreservedBudget` | Norm-two certificate cannot be reduced to norm one; unsolved `False` |
| `new/negative/WR02ConvexEquality` | Convex half-line energy equality is false; unsolved `False` |
| `new/negative/WR02MissingBudget` | An implication still requiring a finite uniform budget is supplied as its conclusion |
| `wr15/negative/ProperSubspaceCertificate` | Missed full residual square 1 cannot be bounded by coordinate certificate 0; unsolved `False` |
| `wr15/negative/RawCovectorNorm` | Raw covector square 5 cannot equal original squared norm 1; unsolved `False` |
| `wr15/negative/SingularGram` | Determinant zero is not a unit; unsolved `False` |

The diagnostic classes total 18 unsolved `False` obligations, one false arithmetic proposition, seven intended type/application mismatches, two placeholder rejections and two axiom-policy rejections. None is an import/name/object failure, unrelated synthesis error, crash, timeout, memory failure or heartbeat/recursion exhaustion. This closes the exact fixture-specific diagnostic gate; it does not certify arbitrary future fixtures by substring matching alone.

### Final evidence identities and closure

| Artifact | SHA-256 |
| --- | --- |
| `runs/clean_wr15_01/receipt.json` | `2de09e2bdae21cd53e0b3ff294d706dbf1582446ef5a0e1b8bc875023a4737cb` |
| `runs/clean_wr15_01/postflight.json` | `262fd925eb8ad139bebfcfc7627545da04ad7b3de6f0b0d3e32e0de67b3e90af` |
| `assemblies/wr15_01/inventory.json` | `881dd5ae80947bc0d717dd07ed5f07278af52067e5f6f5b72bc7254dd4110a4e` |
| `reviews/reviewed_helpers.json` | `993460d78c983f4a87d5e95c682d220151f1de73ec45c6e29235728a3135facf` |
| `runs/clean_wr15_01/axioms.json` | `9ad15c9fb3139088dc1e1afab28e137a8ae8d70b4a1eb6ba8bc40fb21271256b` |
| `runs/clean_wr15_01/new_declarations.json` | `6222bd6e4b8b4e9a5e754201c14895128e0581a9ec2bd6f850c00b92d55cb2fd` |
| `runs/clean_wr15_01/declarations_sorted.json` | `2154d10de1afa16c0bf95635a9f65b386360d7be2d72b2568e89ea3ba3097d95` |
| `runs/clean_wr15_01/runtime_snapshot.json` | `9092d8caa0e9525e373b41568bf6836f38a5e4baf9a7668656614741af9596cd` |
| `reviews/replay_audit/preflight_checks.json` | `c51126954300ea0db406dba3f8c5f7c03690730b7d09547856255006aad6cf17` |
| `reviews/replay_audit/terminal_checks.json` | `58099914efda553c27602fdbfc762ca7ae183aebca8e3e4dd7233c3f1bf62eeb` |
| `reviews/replay_audit/terminal_check.console.log` | `8f5349c850c41d6cfb6b873388ccb7454c3e44b783fde7c71c4b4e192bd20b75` |

No remaining verifier or final-control gap was found for these exact inputs. The compiler/kernel, permitted axioms, external cache authenticity, host execution environment and non-atomic endpoint limitations remain trusted exactly as stated above. Mathematical checkpoint promotion must additionally consume the separately owned WR15 theorem-to-prose verdict over these same source and exported-type identities. This report makes no assertion about closure of other work registers or the entire monograph.
