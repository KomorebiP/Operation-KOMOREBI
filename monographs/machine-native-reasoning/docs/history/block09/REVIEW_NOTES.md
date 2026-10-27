# Lean Block 09 — internal review and execution boundary

**Machine-Native Reasoning · Reviewed Core 0.2 · Companion 0.9.0 · Komorebi P. · 10 October 2026**

## Scope

Core 6.1 (finite counterexample-guided synthesis) and Core 6.2 (ordered semantic compression preserving the teacher trace) are the new source targets. The 35 predecessor substantive source modules and source book are unchanged. Six new substantive modules contain 78 additional authored theorem declarations, within 120 new authored declarations. Cumulative authored totals are 669 theorems and 1,014 declarations. These are supporting proof-code counts for 17 source results, not new-discovery counts.

The actual completion record is `evidence/RELEASE_RESULTS_BLOCK09.md`, produced only after the current-source final and extracted-source gates and their comparison terminate. `evidence/final09/report.json`, `evidence/fresh09/report.json` and `evidence/FRESH_REBUILD_BLOCK09.json` bind the actual executed inputs and outputs. Earlier and development receipts retain their own scope. The authoring-stage individual compilations and negative rehearsal are not substituted for the cumulative gates.

## Mathematical review

The implementation's one-pass scan is proved to follow the source's restart-earliest protocol on the full original grammar. An additional relation admits any truthful, potentially history-dependent counterexample; all finite prefixes have distinct submitted programs and at most the grammar length in calls. Final acceptance selects the earliest correct AST and final exhaustion excludes exactly the given grammar. An active teacher with arbitrary valid replies cannot make unboundedly many calls. No bound on physical time, evaluation cost or unproductive waiting follows from that statement.

The quotient proof maintains a refutation witness for every seen key. It preserves the literal submitted programs, replies, final retained evidence and returned answer. Key equality implies semantic equality, but semantic completeness is not required. The representative is the original first AST, not a newly normalized program. Existing example order and teacher context order are fixed on both sides.

The comparison counter is the literal short-circuit count of checks against retained examples. Teacher comparison counts are separately equal because the trace is the same. Preparing the illustrative index consumes ten key comparisons and is not free. Program evaluation, key computation, storage and dispatch are not converted into one unqualified speedup number.

Budgeted execution uses distinct complete and suspended constructors. Resumption is proved equal to a full scan including its counters. Fuel bounds candidate inspections, not teacher calls or processor work. The checked suspension model does not supply an independently verified host serialization or crash-recovery implementation.

The eight-expression arithmetic example has a three-context complete finite target and a separately proved universally sound key on natural-number triples. It is intentionally smaller than the older manuscript experiments. The formula fitting those contexts does not thereby acquire authority to prune every future diagnostic problem. Core 6.4 remains outside this block.

## Recorded authoring and environment issues

1. No Lean runtime was initially extracted. The five already-mounted compact parts were used without rematerializing or overwriting them. The inspected supplied assembler checked all chunk hashes and the concatenated archive, then extracted it. The archive hash is `f7548038f94ea30789ce28fc2ff769c40e9c37d8879ea133e9bea821056342c7`. This is consistency with the saved runtime inventory, not independent source authentication.
2. The first synthesis draft used deprecated tactic/lemma names (`push_neg`, `cons₂`), the wrong tuple order for a finite-list lemma, and an unnecessary-simplification diagnostic. Those warning-as-error and elaboration failures were corrected against the pinned interfaces.
3. Quotient helpers initially carried unused decidability assumptions. Explicit `omit` binders removed only the unused section variables. A retained-evidence proof also needed the surviving variable name after substitution. No mathematical premise was weakened.
4. The bounded-scan draft had multiline structure-update parsing errors and an incorrect induction-hypothesis application. Explicit update syntax and the correct remaining-grammar arguments repaired it. Failed elaboration logs may contain Lean recovery diagnostics; no such object is accepted as proof evidence.
5. An unnecessary `Fintype` derivation for the program syntax failed in the minimal import environment, and the first concrete-context proof lacked its finite-index instance. The derivation was removed because programs need not form a global finite type; the actual `Fin` instance imports were added. The grammar and contexts were not reduced.
6. Converting the general protocol's final status initially produced a dependent-match mismatch. Splitting the concrete outcome constructors resolved that elaboration issue without changing the contract.

Raw authoring source-hash and command receipts are under `evidence/development09`. Twelve new negative fixtures were rehearsed and all rejected for their intended proof diagnostics on the first rehearsal. Deliberate rejection is not a failed production theorem. Any later cumulative execution issue belongs to its own receipt and is not erased by this review.

## Verification contract

The cumulative gate compiles 42 production modules into a fresh empty local object directory, checks the original APIs and a new independently restated synthesis API, inspects actual declarations, audits every theorem constant and authored declaration for transitive axioms, and replays all 41 substantive modules through `leanchecker`. There are 91 negative-control contracts: 90 specified proof/placeholder rejections and one deliberately compiled custom axiom that must fail the axiom policy. Only `propext`, `Classical.choice` and `Quot.sound` are admitted.

`PREDECESSOR.json` binds 160 unchanged prior files to the exact Block08 ZIP. The source book's original hashes remain checked. Every current production `.olean` must be byte-identical in the final/fresh comparison. Audit-helper binary differences, if any, are reported separately, without waiving identical generated source or actual axiom output. No prior helper mismatch automatically excuses a current production mismatch.

The pinned compiler is Lean 4.34.0-rc2, commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`; mathlib is `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. Per-command limits remain one thread, warnings as errors, 3,072 MiB Lean-internal allowance and 45 seconds wall time. The whole-gate supervisor allows 900 seconds. No OS-level memory or CPU-affinity cap is claimed.

## Assurance limits

Same-kernel replay is not an independent kernel implementation or upstream source rebuild. Imported dependency objects and runtime artifacts are reused and hash-checked against the saved inventory. The project-authored JSON/source/ZIP tools do not replace Lean's checking of the proof terms. The legacy computation manifest records local execution evidence, not independent attestation.

No source-book PDF rewrite, neural training, empirical performance claim, hardware run, broad learner implementation, external-account action or Windows run is included. No runtime, standalone font, private transcript or third-party full paper is distributed. Proof validity is conditional on the mathematical statement; physical-model fidelity, efficient synthesis, host execution and historical novelty are separate claims.
