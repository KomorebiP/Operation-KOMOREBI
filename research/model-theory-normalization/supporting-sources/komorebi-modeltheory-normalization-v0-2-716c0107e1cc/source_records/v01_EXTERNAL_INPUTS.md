# External and prior-input boundary

## Mathematical dependencies

The new compiled modules use Lean/Std plus exactly two copied project modules:
RepresentationCore.lean and FiniteCertificates.lean from Representation Calculus
v0.4. The source map and their SHA-256 hashes are in
`source_records/PREDECESSOR.json`. Their mathematical bodies and module headers
are unchanged. The original complete archive is preserved in history/.

The retained compiler is Lean 4.34.0-rc2 with commit
6a10ac8c22beadecabdbb0919c2b50214762f91d. Reconstructed compressed runtime hash:
f7548038f94ea30789ce28fc2ff769c40e9c37d8879ea133e9bea821056342c7.
No new Mathlib theorem is imported. No theorem in this block is conditional on
an unverified external algebraic/model-theoretic result.

## Bounded public terminology check

Checked 2026-09-21 using official Mathlib documentation:

- https://leanprover-community.github.io/mathlib4_docs/Mathlib/ModelTheory/Syntax.html
  Inspected ordinary first-order terms, formulas, equality and variable binding.
- https://leanprover-community.github.io/mathlib4_docs/Mathlib/ModelTheory/Types.html
  Used as a terminology boundary: fragment truth agreement is not automatically
  a standard complete type declaration.
- https://leanprover-community.github.io/mathlib4_docs/Mathlib/ModelTheory/Definability.html
  Used as a terminology boundary between finite formulas/definable sets and an
  unspecified quotient or infinite collection of tests.

Online documentation may not match the saved compiler's Mathlib pin. It is a
terminology/source-orientation check only; the new proofs depend on the local
Lean/Std sources and the two archived semantic modules. We did not analyze any
external PDF, cache licensed material, or perform a priority/literature survey.
Initial broad search returned largely irrelevant results. Those were not used
as mathematical evidence; direct official pages supplied the relevant checks.

A full satisfaction-preserving map into Mathlib FirstOrder syntax is specifically
not claimed completed. The written many-sorted interpretation is a clear design
contract for that next formalization.
