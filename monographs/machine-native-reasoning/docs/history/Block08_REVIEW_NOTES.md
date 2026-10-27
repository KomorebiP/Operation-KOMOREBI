# Lean Block 08 — internal mathematical review and execution scope

**Machine-Native Reasoning · Cumulative companion 0.8.0 · Reviewed Core 0.2 · Komorebi P. · 10 October 2026**

## Admission

Core 5.3 is the single added manuscript result, bringing coverage to 15/27. Five new modules derive the general binary bounds, literal unary count, actual worst-case execution, certificate admission and boundary examples. All thirty predecessor substantive modules and the source book are byte-identical to Block07.

The source inventory is 591 authored theorem declarations within 894 authored declarations, adding 63 and 90 respectively. Those include supporting lemmas and examples for one source result. The final axiom/environment totals must be read from the actual current completed receipts, not inferred from these source counts.

## Mathematical review

The proof uses the actual `Tree`, `Valid`, post-action `update`, `profile`, `execute`, `solve` and `compute` definitions. It derives case/leaf equality from immutability and singleton terminal success. It does not use a assumed leaf lower bound. Binary depth is the actual query depth, distinct from the horizon parameter. Unary queries are allowed and counted exactly. The final repair contributes one online unit. The possible worst cost is witnessed by an actual modeled execution.

The lower-bound scope is slightly weaker than the source: total permissions and globally available repairs are unnecessary for a bound on an already valid successful controller. Uniform permissions and all live children still come from `Valid`. Empty support is never a successful state. The singleton case costs one unit and stores one record.

The candidate must be valid and attain BOTH the online and storage bounds. `checkCandidate` alone has a scope premise; `admissionCheck` also executes the finite scope guard. That guard inspects actual table fields, including every finite support-dependent terminal cost. Its potentially exponential preparation is not made free or claimed efficient. A failed certificate does not imply no solution. The constant-report model separately proves no successful tree at any finite horizon.

The eight-case example's general all-larger-horizon result follows by the proved lower bound and padding, not extrapolation from bounded enumeration. The three-case redundant-query example demonstrates that an optimal depth can coexist with excessive storage. Reset and universal-repair models have valid shorter controllers but fail different scope premises. The four-valued report example is outside the binary type, not a refutation of the theorem.

## Development failures and corrections

1. The runtime was not extracted initially. The mounted five compact parts were used directly, without rematerializing or overwriting them. The supplied inspected assembler checked all part contents and the combined SHA-256 before extraction. The combined archive was `f7548038f94ea30789ce28fc2ff769c40e9c37d8879ea133e9bea821056342c7`.
2. An interactive container execution request failed with `StreamingExecNotEnabledContainerError`. A normal subprocess invocation replaced that unsupported launch mode. The restore log records actual completion. No unavailable session was represented as a running verifier.
3. The first structural module requested a nonexistent pinned import `Mathlib.Tactic.Omega`. The import was removed; the needed core tactic was already available. Boolean sums needed the actual `Mathlib.Data.Fintype.BigOperators` import.
4. Proof authoring encountered unspecified maximum arguments, dependent finite-filter rewrite motives, exact lemma-arity differences, an equality-versus-iff Boolean lemma, and warning-fatal unused binders/simplifications. Explicit terms and the pinned library interfaces repaired them. No source theorem was weakened.
5. Zero-horizon `Tree` numerals required explicit `Fin 3` annotations, and zero-horizon examples needed the terminal predicate exposed for decidability. An early draft's recovery placeholders occurred only in failed elaboration logs; no such proof was accepted.
6. Documentation comments had to follow, rather than precede, scoped `omit` and `set_option` commands. A maximizing-execution proof needed an explicit intermediate natural number instead of an unresolved implicit bound.

All authoring logs and the twelve-control rehearsal are retained under `evidence/development08`. The rehearsal met every expected rejection diagnostic. Current full-gate results, any additional failure and the nonproduction audit-helper comparison belong to their own terminated run receipts. No historical passing receipt is a substitute.

## Verification contract

The cumulative driver starts with an empty local object directory, compiles all 36 production modules with warnings as errors, checks independently restated source APIs, inspects actual constants, audits transitive axioms, replays all 35 substantive modules with `leanchecker`, and checks 79 expected negative outcomes. Seventy-eight fixtures must fail with their specified mathematical or placeholder diagnostics. One inherited custom-axiom fixture must compile and then fail the axiom policy.

The fresh gate starts from the frozen source-only ZIP without local proof objects. Every production object must match byte-for-byte. Generated nonproduction helper differences are recorded separately; source and complete axiom outputs must still agree. Earlier helper mismatches do not imply a current mismatch.

Current records are `evidence/final08/report.json`, `evidence/fresh08/report.json`, `evidence/FRESH_REBUILD_BLOCK08.json`, `evidence/COMPUTATION_MANIFEST_BLOCK08.json` and the post-execution `evidence/RELEASE_RESULTS_BLOCK08.md`. Their actual results are authoritative for execution claims.

## Assurance boundary

Lean 4.34.0-rc2 and mathlib `aeb72f1e9981b6d35b426b16dca7759be3e7ba06` remain pinned. Each command has one thread, warnings-as-errors, a 3072 MiB Lean-internal allowance and a 45-second wall timeout. The whole-gate supervisor allows 900 seconds. These are not separately enforced OS memory or CPU-affinity caps.

Same-kernel replay and reused pinned imports are not an independent kernel or upstream rebuild. The complete imported cache and selected runtime artifact hashes are checked against the saved inventory. Source and JSON tools are project-authored and do not replace kernel checking. No physical-model validation, efficient runtime bound, neural training, benchmark campaign, arbitrary-host software verification, Windows execution, hosted repository change or independent peer review is claimed. No runtime or standalone font file is distributed.
