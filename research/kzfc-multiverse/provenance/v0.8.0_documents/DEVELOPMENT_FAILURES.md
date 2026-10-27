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
