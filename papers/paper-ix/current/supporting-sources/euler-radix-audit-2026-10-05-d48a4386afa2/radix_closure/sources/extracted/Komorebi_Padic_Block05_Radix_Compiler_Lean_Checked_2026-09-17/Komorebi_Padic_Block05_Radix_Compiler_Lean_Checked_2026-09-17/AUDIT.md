# Block 05 audit summary

## Universal proof evidence

The warning-as-error Lake build and direct root elaboration passed. Every one of
51 theorem declarations was queried with `#print axioms`; only standard Lean
axioms used by mathlib appeared.

## Concrete compiler evidence

`LeanCompilerVector.lean` contains 72 independently generated concrete checks.
Every check passed `native_decide`.

## Independent exact computation

`verify_radix_compiler.py` passed 1,562,433 exact checks with zero failures.
It compares factorial valuation, direct integer-binomial valuation, and Kummer
carry implementations, then compares full and representative minima.

## Lineage evidence

Eleven predecessor verifier/integrity scripts were rerun individually and
passed. The long Block 03 interval audit was not recomputed in the final replay;
its retained output and source hashes were checked successfully.

## Negative controls

Lean rejected both a false theorem and a theorem containing `sorry` under
warning-as-error.

## Residual risks

- RC2 rather than stable toolchain
- suffix scan not yet formalized
- finite computation ranges do not prove universal statements
- no external novelty review
