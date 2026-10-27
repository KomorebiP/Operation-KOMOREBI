# Failure ledger — Strong Artin Lean v0.23

## 1. Interactive runtime launch unavailable

An attempted interactive execution failed with
`StreamingExecNotEnabledContainerError`.  No Lean theorem was run in that
attempt.  Work continued through synchronous container execution.

## 2. Initial Lean search path was wrong

The first compilation command launched `lake env` outside the portable
workspace, so Mathlib was absent from the module search path.  The failure
occurred before theorem elaboration.  The command was corrected to run inside
the pinned workspace with the generated `LEAN_PATH` plus the staged source and
object directories.

## 3. Direct nested quotient equivalence was not retained

I attempted to package an explicit linear equivalence

```text
presentationObstructionDual P / relationSyzygies P
  ≃ P.toExtension.H1Cotangent.
```

The pinned environment produced quotient-instance failures in one formulation
and repeated elaboration timeouts in another.  No timed-out declaration was
counted.

The release instead uses the more stable and operationally sufficient data:

- a canonical surjection;
- an exact kernel;
- exactness;
- surjectivity of selected evaluation;
- equivalence when the syzygy kernel vanishes.

This does not weaken the checked auxiliary-selection conclusion.

## 4. Development inference failures

Early drafts contained ordinary Lean engineering errors:

- a namespace/field-notation mismatch for comparison data;
- underdetermined implicit arguments to `evaluationMap` and `selectedKernel`;
- a binder-order error in which a presentation was referenced before binding;
- a failed direct rewrite through `LinearMap.ker_eq_bot`;
- a final `simp` call that did not reduce a composite of two constructed linear
  equivalences.

The last issue was replaced by an explicit
`LinearEquiv.apply_symm_apply` proof.  All final modules compile with warnings as
errors.

## 5. One-shot verification exceeded the outer wrapper

The first complete fourteen-module replay reached eleven successful modules and
then exceeded the external execution limit.  It emitted no theorem error, but
the interrupted wrapper was **not** counted as a completed verification.

The verifier was changed to persist each observed module result and support
bounded resumable replay.  A clean replay was then run in two batches:

- batch 1: 8/14 modules, all zero exit codes;
- batch 2: remaining 6 modules, all zero exit codes.

The final `RESULT.json` records all fourteen observed compiler results.
