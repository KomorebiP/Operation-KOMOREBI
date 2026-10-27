
# v0.10.0 development and execution record

The following are implementation/execution failures, not mathematical counterexamples.
All failed source attempts were excluded from the final active proofs.

* `003_InternalOrderGraphs.log`: a missing closing tuple delimiter in a graph-construction proof. Repaired syntactically.
* `005_InternalRankingConditions.log`: nested first-order formula parentheses caused a parser error. The formula was split into explicit functional, downward and recurrence subformulas, each with a checked interpretation.
* `008_InternalBoundedRanking.log`: tuple substitution removed a local variable name used later in the proof. Replaced the stale reference by the inferred remaining term.
* Direct `container.exec` returned ClientError. Filesystem work and actual compiler execution proceeded via Python subprocesses.
* The first verification launch used the virtual-environment Python and triggered an unrelated spreadsheet-runtime startup hook. Its daemon consumed about 1.39 GB RSS. The enclosing next-batch call timed out after 35 seconds with only two compiler version commands recorded. That incomplete directory is retained at `verification_history/v0.10.0_interrupted_startup`.
* A subsequent system-Python batch recorded five more successful commands before its enclosing 35-second call timed out. The exact recorded boundary was retained; no incomplete command was counted. An unused startup helper was terminated, and the unchanged verifier resumed from the hash-pinned boundary. The remaining batch was observed through its actual exit using a subprocess handle. This is a staged verification session, not one uninterrupted compiler subprocess.

The final active verdict is issued only by `verify_staged.py finish`, after full command coverage, exact log hashes, source stability and axiom checks. Read that verdict rather than this development log to determine completion.


---

# Historical records through v0.9.0

# Development failures v0.7.0

## Environment and execution

1. The toolchain was not mounted in the fresh container, but all seven retained offline parts were present. The inherited restoration script completed, with every part and the reconstructed stream matching the recorded SHA-256. See provenance/runtime_restore_v0.7.0.json.
2. A requested streaming execution session failed with StreamingExecNotEnabledContainerError. No successful process was inferred from that request. Restoration was then executed synchronously and completed.
3. An initial multi-target predecessor build produced an exit-zero GuardedTheory result, then the enclosing tool interrupted the longer call before a result for the next target was recorded. The available GuardedTheory log is in development/restore_build_GuardedTheory.log. The incomplete call is not verification evidence for its later targets.
4. An unused artifact renderer occupied about 1.4 GiB. It was stopped before continuing the proof work. This reduced memory pressure, but no single cause for the enclosing-tool interruption is claimed. The final run uses short synchronous batches with actual exits recorded.

## Resolved implementation errors

* general_01.log: bind was ambiguous with the generic Bind class operation. The binder helper was fully qualified as MembershipFormula.bind. No formula changed.
* zfc_semantics_01.log: .mp/.mpr were applied to theorem names still awaiting the explicit schema formula argument. Supplying that argument fixed elaboration.
* zfset_model_01.log: elaboration did not infer the separator predicate through the generic membership wrapper. Explicit source, element and predicate arguments plus the proved membership conversion fixed it.
* zfc_closure_01.log: the deterministic universal-closure implementation initially left a Fin 0 assignment equality and an unused simp argument. The existing realize_relabel_sumInr theorem supplies exactly the needed semantic identity. The result is a deterministic bound-variable construction, not a weakened schema.

No mathematical hypotheses were added to resolve these errors. No mathematical counterexample was found in the new ZFC encoding block. The predecessor's genuine finite-prefix and successor-cardinal counterexamples remain unchanged.

## Verification boundary

Only the active completed staged-session verdict under verification is a fresh proof audit. Successful development compilation is useful intermediate evidence but does not replace the full clean build, per-file elaboration, complete named-theorem axiom audit, negative controls and unchanged-source checks.

## Historical v0.6.0 record

# Development failures and corrections v0.6.0

## Environment and execution

The fresh container contained the seven offline archive parts but no extracted compiler. The runtime was reconstructed synchronously, with its SHA-256 exactly matching 66dfa8ce4627489bc61e44a77782931d36c1b626a177790a5d4599034b70ec34. A streaming-session request failed because that capability was unavailable. The restore itself succeeded with zstd and tar exit codes zero.

An initial root rebuild was interrupted by the enclosing tool before a complete verdict. An individually retried membership module then built. Two later monolithic serial clean verification attempts were also interrupted. The calls requested a 200-second allowance, but their partial logs do not establish that 200 seconds actually elapsed; the effective host interruption limit is not known. None of these attempts is presented as a successful full verification. Their partial logs are retained in separate historical directories.

Inspection found an unused artifact_tool rendering worker consuming about 1.4 GiB in the 4 GiB cgroup. There was substantial memory-limit pressure and no recorded OOM kill. The unused worker was stopped before a further clean verification attempt. That monolithic attempt was still interrupted. Memory pressure is an observed environment issue, not a proven explanation of the host interruptions. Mathematical assumptions and statements were not weakened to fix runtime behavior.

## Verified execution repair

The final run uses `scripts/verify_staged.py`. A fresh start removed project build products, cleared stale verdicts, pinned all inputs, and fixed the complete command plan. Ten synchronous batches executed all 47 compiler commands with unchanged inputs. Finalization checked the recorded plan, every actual exit code and log hash, all 210 named theorem declarations, source restrictions, and preservation of all 17 predecessor mathematical modules. Only then was PASS written. The completion record explicitly identifies a staged session rather than one uninterrupted subprocess. This changes execution scheduling and evidence recording, not mathematical assumptions.

## Lean elaboration repairs

The first guard attempt used wrong namespace qualifications for ord_card_le and lt_add_one. Cardinal.lt_ord also required an explicit target before applying it to aleph0. These were API/elaboration errors.

The cofinality converse originally selected an ordinal-carrier element through enum. Simplification and instance matching prevented the intended typein_enum rewrite. The final proof instead uses the directly supplied typein_surj theorem, preserving the same mathematical argument. Raw unsuccessful attempts are retained in verification/development/guard_attempt_*.log.

The first sentence regressions tried to project a conjunction directly from a formula realization. Formula conjunction is encoded in primitive logical syntax, not definitionally a Lean pair. Applying Formula.realize_inf before projection resolved the error. No theorem was admitted.

## Boundaries not closed

The object-language ZFC derivation, arbitrary-model internal set-theoretic comparison, uncountable existence, independence and relative consistency remain unproved. Their absence is not a failed compiler test and is not relabeled as completed by the concrete semantic result.


## v0.8.0

See BLOCK_08_REPORT.md and development/v0.8.0 for the restore interruption, baseline build interruption and completed retry, local elaboration repairs and syntax delimiter repair. No mathematical assumption was weakened or inserted to fix these errors.


# v0.9.0 development and execution record

The fresh container had no mounted Lean executable. The seven stored offline parts were present. The retained restore script reconstructed the runtime and produced the expected archive SHA-256. `development/v0.9.0/runtime_restore.json` records the successful restore. No new compiler download or dependency update was used.

The first baseline build exceeded the enclosing tool limit after nearly all prerequisite modules compiled. `baseline_build.log` is incomplete evidence, not PASS. Repeating the baseline target completed successfully in `baseline_retry.log`.

`supports_01.log` records a failed elaboration caused by an equality being passed where an equivalence was required in the singleton-size lemma. It was repaired explicitly. `supports_02.log` records the successful module build.

`concrete_01.log` and `concrete_02.log` record failed elaborations in the concrete cardinal-product bridge. The issues were definitional unfolding of Carrier/ZFSet.card and rewrite ordering, not additional mathematical premises. Rewriting the range equality before simplifying the exact cardinal expression fixed the proof. `concrete_03.log` records exit-success output.

The cone filter, necessity theorem, uniform-bound reduction, support equivalence and closed-sentence formula modules compiled on their first recorded checks. Their individual logs are development evidence only. A complete final run is recorded separately in verification/RESULTS.json.

The attempt to close Extension -> Fine unconditionally in every ZFC model remains incomplete. The unproved piece was reduced to the exact productArithmeticSentence. It was not assumed as an axiom, inserted into the base theory, hidden in Guard or discharged by external cardinal arithmetic for arbitrary models. The concrete ZFSet case is complete. This is a formalization boundary, not a mathematical counterexample.

## v0.11.0 multiverse branch

### Direct Lake invocation invalidated the shared Mathlib cache target

An initial attempt to call `lake env lean` inside a copied project caused Lake to report a changed
Mathlib URL and delete the symlink target it regarded as stale.  This damaged only the restored
runtime cache, not project source.  The cache was restored from the seven retained offline parts.
The first Python restore attempts exceeded the enclosing command limit after part 6; a shell
streaming reconstruction (`unzip -p | zstd -dc | tar -xf`) completed successfully.  The v0.11
verification therefore invokes the pinned Lean executable directly with an explicit `LEAN_PATH`
and does not call Lake.

### Triangle example elaboration repairs

The first abstract network used the field name `extends`, which is reserved syntax in this Lean
version.  It was renamed to `reach`.  A first finite example based on a subtype of finite sets was
also dropped because the minimal imports did not provide the desired computable `Fintype`
instances.  The replacement six-constructor triangle network is mathematically equivalent for the
intended obstruction and compiles without native decision procedures.

### Minimal-nonface auxiliary theorem deferred

An attempted convenience theorem identifying the triangle as a `MinimalNonface` exposed awkward
definitional-equality friction between the network's projected world type and the concrete
`TriangleWorld` type.  The theorem was not needed for the central higher-obstruction claim and was
removed rather than weakening warning settings or adding casts solely for presentation.  The
kernel-checked pairwise/non-joint statements remain the exact substantive content.
