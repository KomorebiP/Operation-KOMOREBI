# Komorebi Space release evidence review

The accepted mathematical and formal scope is complete. The current publication package's remaining explicit release blocker is the absence of a public license grant in REUSE.md. This review found no mismatched source, review, book, or declaration identities in the accepted package.

## Fresh checks in this review

- The exact 9,899,433-byte publication archive has SHA-256 `7f68336e652bc6af817ba0fc8c96476f7cc39318ff333f404e202f4388dfe63f`.
- ZIP CRC passes. All 491 SHA256SUMS entries match, and the file set is exactly those entries plus SHA256SUMS. The extracted tree is byte-identical to the archive.
- All edition source hashes, current review hashes, book hashes, and all 229 proof-run input hashes match current files.
- The integrated receipt and declaration inventory match the edition record's hashes. The receipt's declaration and control-manifest hashes also match.
- A fresh `--plan-only` invocation completed as `STATIC_VALIDATION_ONLY`, with Lean execution explicitly false. The source graph contains 166 targets: 162 production modules and four roots. The exact control set and all control source hashes validate.
- All 114 selected theorem-map names, defining modules, declaration kinds and source-file hashes reconcile with the preserved compiled inventory.
- That inventory has 5,339 unique exported declarations from 162 production modules, with no unsafe or direct-axiom declarations and no rejected entries. Its recursive axiom union is `Classical.choice`, `Quot.sound`, `propext`.

These are fresh integrity and source-binding checks, not a fresh Lean replay or a new whole-book proof audit. The two machine-readable records beside this report preserve their exact scope.

## Preserved accepted formal evidence

The accepted integrated replay ran on 15 October 2026 from 02:30:48 to 02:44:59 UTC. Its PASS receipt records 262 commands, 166 freshly compiled targets and 5,339 audited exported declarations. All 56 diagnostic controls had the expected outcomes: 18 acceptances, 35 elaboration rejections and three axiom-policy rejections. It is incorrect to describe all 56 as negative controls. No command timed out. The source, fresh project object and external-runtime endpoint identities were unchanged.

The source contains 1,859 explicit theorem or lemma declarations. The compiled inventory contains 3,863 theorem constants, including generated declarations, plus 1,341 definitions, 45 inductives, 45 constructors and 45 recursors. These are different counting conventions, not independent discoveries.

The edition records formal counterparts for all sixteen principal analytic theorem groups. This includes actual infinite diagonal behavior, certified tails, the sharp all-real-budget limit, rounded noisy rates, the measured-residual inexact rate, and an actual nonclosed diagonal range with a closure datum lacking a preimage. The independent reviews of the last two connections both report “proved as written” with no remaining gap. That is preserved statement-review evidence, not a new review performed here.

The printed weak-subsequence proof route and separate protected product-space illustration are not separately formalized. Coverage of sixteen principal groups does not mean every explanation, example or alternate proof route has a separate Lean theorem. Finite Python examples are not certified Lean extraction. The compiler and dependency caches remain trusted inputs. Their endpoint hashes do not authenticate their origin or rule out transient changes restored before the final check.

## Source and book preservation

The monograph has 160 pages, the Lean guide 24 and the Visual Guide 19 in this accepted base. Their bytes match the edition record. All 192 previous formal environments and 512 bracketed displays in 29 mathematical chapter files were preserved in the accepted edition. All 160 inherited production modules were byte-preserved from its parent; two new modules and the diagonal-root import update were accepted.

No source or publication file was edited during this review. No AGENTS.md exists in the inspected publication tree.

## Reproduction and delivery

The integrated runner uses Lean 4.34.0-rc2 commit `6a10ac8c22beadecabdbb0919c2b50214762f91d` and mathlib `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`, matching the stored portable runtime already restored for the MNR task. All nine dependency Git revisions are checked, and tracked dependency changes are rejected. The runner recompiles all project sources into a new empty output directory and uses project objects ahead of external caches in LEAN_PATH.

For an offline working copy, provision its `lean/.lake/packages` from the matching portable runtime's `workspace/.lake/packages`, put the portable `toolchain/bin` on PATH, and supply the runtime's existing executable-path adapter through LD_PRELOAD if required by this host. Do not change the accepted source inputs to install an adapter. The runner records the supplied adapter bytes. Run from the publication root:

```sh
python3 -B verification/runner/runner.py --output /absolute/new/outside-directory
```

The default per-command timeout is 300 seconds and the declaration-audit timeout is 1800 seconds. Compilation is sequential with `-j1`, warnings as errors and autoImplicit disabled. There is no fixed internal memory cap in this runner. The source-bound inputs are Lean sources, three Lean configuration files, and all verification/runner files. Root and lean README files are outside that 229-file proof-input set, so their licensing prose can be updated without changing accepted formal inputs.

The compact publication contains the accepted receipt and complete declaration inventory, but not its raw 262 command logs or 166 project objects. The separately published `Komorebi_Space_Technical_Record_v1.15.0.zip` (Library ID `libfile_983f36b8fa6c8191bd5e2a685743657b`, 139,563,911 bytes) was recovered and checked directly. It includes the 262 raw logs, all 229 source-snapshot files, inventories, attempts, and the intact predecessor technical archive. Its README explicitly says the 166 fresh project object byte sequences were omitted; only their hashes are retained. Those historical object bytes were not recovered or rechecked. A new run can produce current objects without relabeling them as historical bytes. No missing historical payload was reconstructed here.

## Recommended current release wording

“Komorebi Space's accepted formal scope is complete: sixteen principal theorem groups have formal counterparts. The source has 162 production modules and four import roots, with 1,859 explicit theorem or lemma declarations and 5,339 exported declarations. The preserved integrated verification checked all 166 targets and all 56 specified diagnostic outcomes. The current release adds explicit public reuse terms and canonical packaging while preserving the accepted mathematics.”

If root performs a new full replay, replace only the preserved/current execution phrasing using its actual completed receipt. Do not infer a fresh kernel result from this review's static plan.

## Recovered Technical Record check

The exact technical archive has SHA-256 `2cc2a0291669781e3c5bb6608cc4f3c86cce513ec686c2b17031d35278d353db`. Direct ZIP CRC and all 1,202 manifest hashes pass, with exactly 1,203 archive members including the manifest. Its accepted receipt is byte-identical to the publication copy. All 262 command logs, all 229 source snapshots, the declaration inventory, generated auditor and runtime inventory match their accepted receipt hashes. Log and snapshot file sets match exactly. Its embedded publication archive matches the canonical publication SHA-256.

The first inspection attempted to read an omitted historical `.olean` file and raised `KeyError`. Reading the archive README established that object omission was intentional. The corrected check is a pass for the included archive contents and preserved evidence, with no historical object-byte comparison claimed. See `TECHNICAL_RECORD_INTEGRITY_AND_BINDING.json`.
