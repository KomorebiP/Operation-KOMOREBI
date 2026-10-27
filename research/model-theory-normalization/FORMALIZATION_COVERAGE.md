# Formalization coverage — v0.10

PASS: 9 new local Lean modules, 105 theorem declarations (78 generic and 27 concrete
kernel examples), 50 definitions, 2 abbreviations, 1 structure and 1 inductive type:
159 explicit named declarations audited. Generated constructors/fields compile but
are not counted again as named research declarations. 17 expected-outcome tasks
passed: 9 cold builds, one full axiom audit, one positive control and six rejections.
Only `propext`, `Classical.choice`, and `Quot.sound` appear. No custom project axiom,
`sorryAx` or `Lean.ofReduceBool` is accepted. Library warnings are errors.

| Module | Exact checked scope |
|---|---|
| BinaryWords | Word semantics, padding, full-adder/subtractor truth tables, ripple operations and length/value theorems |
| BinaryMulDiv | Actual shift-and-add multiplication and restoring long division, positive-divisor invariants and cost recurrences |
| BinarySigned | Sign/magnitude arithmetic, zero detection, Euclidean adjustment and safe divisor rejection |
| BinaryEncoding | Integer/word boundary conversion correctness and semantic scalar adapters; conversion costs excluded |
| BinaryCosted | Actual metered evaluators, erasure theorems, exact counts, modular multiplication and quadratic width budgets |
| BinaryPricing | Explicit unsigned request interpreter, trace semantics and conditional length/width cost bound |
| BinarySignedCost | Metered sign handling, zero scans, signed addition/multiplication/division and their cost bounds |
| BinaryBackend | Signed subtraction, modular addition, final scalar semantics and budgets |
| BinaryExamples | 27 finite direct kernel computations, including negative division, padding, carry, borrow and widened modular products |

The current Lean modules import pinned Mathlib directly. The predecessor archive
is preserved but its historical local Lean library is NOT recompiled by this block.
The selected Python baseline payloads are exact original bytes; their 203 source
profiles are re-executed independently and under the new port.

## Boundaries

No universal theorem lowers the full discovery loop into these binary routines.
The 203 complete bit-backed discovery executions are PYTHON tests, not 203
kernel-checked whole-loop instances. Their scalar algorithms have generic Lean
counterparts; their parser/port/transcription is not verified extraction.

The cost theorem concerns a declared gate/cell model. It excludes input conversion,
allocation/indexing/queue work, compiled runtime, proof checking and bit-machine
implementation overhead. Primitive arithmetic correctness and priced scalar
recurrences do not alone close that missing implementation refinement.

The conditional unsigned trace theorem requires an explicit trace and explicit
operand-width/length bounds. The signed primitive theorems are separate; no
unproved universal trace-composition premise is silently discharged.

Lean 4.34.0-rc2, commit 6a10ac8c22beadecabdbb0919c2b50214762f91d.
Mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06. Existing upstream cache reused,
not rebuilt. Interpretation and implementation review are self-review.
