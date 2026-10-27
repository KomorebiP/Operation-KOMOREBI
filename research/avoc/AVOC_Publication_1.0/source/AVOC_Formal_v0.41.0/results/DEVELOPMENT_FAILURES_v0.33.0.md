# AVOC v0.33.0 — development failures and repairs

These failures were not counted as successful evidence.

## 1. Missing inherited local object files

The new modules initially could not elaborate because the extracted cumulative
source tree did not contain inherited local `.olean` outputs.  This was an
environment/setup issue, not a theorem counterexample.

**Repair:** reconstruct the exact pinned Lean environment and rebuild the
entire inherited local dependency graph.  The final release then repeated a
clean 182-target local rebuild from an empty local build directory.

## 2. Generic-controller executability

An early design attempted to store matrix rank directly in the generic control
model.  Matrix rank is not the right executable field for the generic runtime
interface and would have entangled probabilistic planning with algebraic proof
objects.

**Repair:** separate the layers.  The generic model stores only deterministic
reports, certificate levels, fees and payoffs.  `RankSound` is an external
algebraic invariant proved for the affine specialization and preserved by every
transition.

## 3. Rational expectation proof repairs

First-pass proofs of uniform-catalogue expectations and success/failure
probability identities encountered type-coercion and finite-sum normalization
errors.

**Repair:** make rational card coercions explicit, use the nonempty-world proof
to establish a nonzero denominator, and prove the partition/cardinality law
before the rational identity.

## 4. Dependent success/failure states

The first rank-invariant proof attempted to rewrite directly through the
`if h : filteredWorlds.Nonempty` state construction.  Lean could not infer the
required dependent branch equalities automatically.

**Repair:** split explicitly on the nonempty predicate, recover membership in
the selected branch, and transport the previous rank invariant manually.

## 5. Missing plan-horizon binder

The first statement of `rankSound_optimal_plan_exists` quantified over an
untyped competing plan.  Lean could not infer the plan horizon.

**Repair:** give the competing plan the explicit type
`Guarded.Plan (MultiLevel.Action P) Bool steps` and recompile the module.

## 6. Codec construction and indentation

The first executable codec used awkward nested indentation around monadic
bindings.  It elaborated during development but was difficult to audit.

**Repair:** normalize the block structure and recompile the codec and entrypoint
before the final clean build.

## 7. Concrete-choice proof experiments

Two attempted convenience examples tried to reduce the exact chosen action by
`rfl` or `native_decide`.  The choice did not reduce definitionally through the
full evaluator, and `native_decide` is outside the positive-source policy.

**Repair:** omit those convenience proofs.  The universal action-optimality
proof remains kernel-checked, while exact example choices are executed by the
proved evaluator and independently checked by the exact Python oracle.

## 8. Negative-test batch interruption

A 25-file negative batch hit the host's execution limit after 14 completed
files.

**Repair:** resume at the first unfinished test in ten-file groups.  Only final
non-timeout, substantive Lean rejections are included in the release summary.

## 9. Runtime source-record strictness

The development wrapper temporarily permitted fallback to direct development
records or inherited v0.32 records when v0.33 clean records were absent.

**Repair:** remove all fallbacks before final regression.  The delivered wrapper
requires current v0.33 clean source/import/output records for every local Lean
module it executes.
