# Failure ledger — Strong Artin Lean v0.19

No failed attempt below is counted as proof evidence.

## Runtime extraction

The seven-part portable runtime assembled successfully with the expected combined SHA-256. The initial extraction command exceeded its outer execution wrapper after writing a partial tree. Extraction was rerun and completed; the final runtime contains the complete 11 GB tree. A subsequent full runtime verification also exceeded an outer wrapper after several successful checks, so theorem verification used the narrower project verifier against the pinned toolchain and mathlib revision.

## API probe timeout

An initial scratch file importing all of `Mathlib` exceeded a 300-second wrapper. The development was reduced to narrow imports. This was an operational timeout, not a mathematical result.

## `NilpotentRightInverse`

The first draft failed because simplification did not identify

```text
(J.comp R₀ - id) + id = J.comp R₀
```

at the `IsUnit` level, and because the broad `abel` tactic was not imported. The final proof uses explicit `change`, `sub_add_cancel`, and `add_sub_cancel_left` steps.

## `PowerDivisibility`

The first induction proof of monotonicity left an exponent-normalization goal. It was replaced by a direct exponent decomposition

```text
n = m + d
```

and an explicit witness `pi^d • x`.

## `VariableJacobianHensel`

Two development errors were corrected:

1. Lean could not infer the module in `sameResidual_self`; the final proof unfolds the definition and simplifies directly.
2. `x₀` was referenced before its explicit binder, creating a distinct implicit metavariable. The binder order was corrected.

## Fresh verifier timeout

The first fresh seven-module replay completed six modules and then exceeded the outer wrapper while loading the final quadratic module. The cause was an unnecessarily broad `Mathlib.Tactic` import. It was narrowed to `Mathlib.Tactic.Abel`, the final module was recompiled in the same fresh output tree, and the resumable verifier returned `PASS`. The interrupted wrapper was not counted as a complete verification.
