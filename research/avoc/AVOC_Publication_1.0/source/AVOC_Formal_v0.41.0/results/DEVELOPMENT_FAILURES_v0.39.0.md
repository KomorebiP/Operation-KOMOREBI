# Development failures and corrections — v0.39.0

No failure below was counted as a completed proof, substantive negative test, or
successful execution. Raw development logs remain in results/v0.39.0.

## Inherited evidence defects

1. Five negative files failed on absent local Fact (Nat.Prime 5) instances rather
   than false mathematical claims. Their original v0.38 logs show the same defect.
   Minimal local instances make the propositions elaborate; the intended false
   claims are then rejected.
2. FalseZeroCostWitness failed because decide refused a goal with an unused free
   variable. Explicitly changing the goal to (1 : Nat)=0 exposes the intended
   contradiction. Six originals, hashes, and original failures are retained in
   provenance/v0.38_negative_setup. Earlier 111/111 substantive wording was too strong.
3. Old selected-artifact fixtures contained absolute paths into a prior workspace.
   Their initial reruns failed before operation execution. Relocated fixture copies
   preserve the absent unselected path and make the workflows reproducible.
4. Two explicit private v0.38 theorem helpers were omitted from the public-name
   inventory. The new source inventory includes their exact compiled names.
5. The old dominance checker compared an action against itself. This is sound but
   forces its radius to zero. A new competitor-only checker is proved sound without
   changing inherited implementation or theorem files.

## New mathematical development

The binomial normalization proof initially needed a corrected sum-rewrite
orientation; deprecated tactic syntax triggered warnings-as-errors; envelope
multiplication required an explicit nonnegative endpoint; rational cancellation
needed normalization. These were local elaboration issues, not counterexamples.
Direct decide reduction of proof-bearing Finset extrema did not complete the
concrete examples. Explicit retained-set equalities and small exact norm_num
lemmas proved the same examples without compiler-trust evaluation.

The false empirical-singleton proposal is preserved as a kernel counterexample:
with n=1,p=1/2, its miss probability is one. The corrected interval is the proved
cell-envelope hull. The false single-error-budget adaptive-selection proposal
is also preserved: two individually 1/2-error events can be selected with error
one. The corrected theorem uses the finite scheduled sum.

Outcome-dependent censoring remains a genuine model obstruction. If failures
are reported as infrastructure faults and successes as checked records, deleting
faults leaves only successes. The corrected contract requires binomial marginals
for the accepted stream; this premise is not inferred from fault exclusion.

## New implementation development

- A first log-membership proof required explicit substitution after Option.some
  equality. The corrected proof compiles with warnings as errors.
- Early codec/main checks ran before the new dependency object existed. Missing
  objects were setup failures only; subsequent checks used compiled dependencies.
- The codec initially used unavailable Option.toExcept and mixed a Prop equality
  into Bool conjunction. Pattern matching and Bool equality fixed elaboration.
- Independent review found raw Lean JSON parsing normalized exponent-form tokens,
  allowing 1e0 despite a strict integer-token contract. A lexical numeric-token
  check before Json.parse now rejects decimals/exponents while preserving escaped
  identity strings. Fourteen direct raw-CLI probes passed after the fix.
- Initial private-name inspection used unsupported #print prefix syntax. Direct
  environment inspection recovered exact private names; the final audit uses them.
- Early schedule proofs needed local finite-sum/elaboration repairs. Separate logs
  retain the unsuccessful attempts and final warnings-as-errors pass.
- The inherited-regression portability helper initially failed during dynamic
  dataclass import and then on reused workflow directories. Module registration
  and per-run isolated directories corrected those runtime setup faults.

## Environment

Four runtime-file materialization attempts returned HTTP 502. A separately
located preserved runtime was instead checked for its exact Lean commit and all
nine dependency revisions. No failed download is claimed as a restoration.
The source ZIP and all 13,389 original payload hashes were independently verified.

## Build orchestration

Two bounded final-build slices briefly overlapped because the second session was
still finishing its active targets when the next slice was started. No source
changed. The final sequential dependency validator checks every current source,
import object, output object, and log hash, and reruns any inconsistent target.
Only the resulting complete current graph is release evidence.

The first final axiom-audit attempt could not parse the numeric component of two
private declaration names in textual #print commands. The audit now resolves
those exact names from the imported environment and uses Lean.collectAxioms,
with an exact two-name count check. The second complete audit passed all 2,122
reports. The failed first report remains preserved.
