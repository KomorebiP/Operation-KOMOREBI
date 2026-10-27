# Failure ledger — Strong Artin Lean v0.21

No failed attempt below is counted as proof evidence.

## Runtime and verification wrappers

The full portable-runtime self-check exceeded its external execution wrapper before returning. It was not used as proof evidence. Verification instead used narrow compilation against the pinned Lean and mathlib environment.

An attempted interactive streaming replay failed because streaming execution was unavailable. The release verifier was run synchronously in bounded, resumable batches.

The first release replay passed arguments to its inner shell at the wrong positional indices. Lean consequently received incorrect root and output paths and failed before compiling a theorem. The verifier was corrected to pass all four search paths and the source root, output and source file at their proper positions. The corrected replay produced zero compiler exit codes for all 19 modules.

Two outer transport wrappers ended before returning their terminal output. The underlying verifier completed and wrote `RESULT.json`, all 19 per-module logs, all 19 `.olean` files, and recorded zero exit codes. Source hashes, object files, logs, and the result manifest were independently cross-checked before packaging.

## Lean search path

The first compiler probe replaced rather than extended the portable environment's `LEAN_PATH`, shadowing the offline mathlib cache. This was an environment configuration failure, not a theorem failure. Subsequent commands ran through `lake env` and prepended only the release source and object roots.

## Polynomial compiler

An initial compiler attempted to obtain finite products from syntactic commutative-monoid instances that the custom expression type did not possess. It was replaced by explicit recursive list products and sums.

One draft used a nonexistent or mismatched list-product theorem. The proof was rewritten with `Finset.prod_map_toList` and compiled.

## Formal-power-series API

Several exploratory drafts used incorrect Mathlib names or shapes, including proposed forms of:

```text
MvPowerSeries.coeff_coe
MvPolynomial.eval₂_at_apply
IsNilpotent.of_pow_eq_zero
```

The final source uses the available substitution, truncation, coefficient, and nilpotence APIs directly.

The first canonical-evaluation-at-zero proof did not simplify the zero substitution automatically. It was repaired by proving the substitution functions equal explicitly and then applying `subst_zero_eq_C_constantCoeff`.

## Derivative compiler

Early `MvPolynomialExprDerivative` drafts left unresolved goals and therefore produced `sorryAx`. Those drafts were rejected. The final proof first establishes equality of the compiled expression's actual polynomial semantics and then derives the partial-derivative identity. The final module contains no `sorryAx` and compiles with warnings as errors.

## Formal presentation quotient

Initial quotient-algebra proofs had coercion and simplifier/linter failures around `AlgHom`, `RingHom.ker`, and quotient constructors. The evaluation map and relation-ideal inclusion were rewritten with explicit coercions and kernel membership proofs. The final quotient-point capstone compiled successfully.

## Warnings as errors

Several intermediate proofs contained unused section variables or unnecessary simplifier arguments. They were removed rather than suppressing warnings. The authoritative replay used `-DwarningAsError=true` for every module.
