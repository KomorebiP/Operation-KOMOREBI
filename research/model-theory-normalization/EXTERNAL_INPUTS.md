# External mathematical and execution inputs

The only proof-library dependency is the pinned Mathlib/Lean installation:

* Lean 4.34.0-rc2, commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`.
* Mathlib `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.
* Observed Lean executable SHA-256:
  `e8baaa71855a616dc351028f3ad2200051b0671f423a1696a100e809302d5550`.

Natural/integer arithmetic, list induction, Euclidean quotient/remainder identities
and their uniqueness, and the ring/omega/nlinarith tactics are existing inputs.
Examples include `Nat.div_mod_unique`, `Int.ediv_eq_iff_of_pos`, and
`Int.emod_add_ediv_mul`. The compiled theorems derive the actual binary algorithm's
invariants before applying those semantic uniqueness results. No theorem claiming
the correctness of this new algorithm is assumed.

The official Lean integer reference distinguishes logical integers from the native
arbitrary-precision implementation and its optimized primitive operations:
https://lean-lang.org/doc/reference/latest/Basic-Types/Integers/
This source is explanatory context, not a new external proof dependency. Native
primitive cost is not inferred from the mathematical integer operations.

The frozen predecessor supplies the discovery source and 203 test profiles. They
are reused byte-for-byte in baseline/, without claiming that Python source is
verified Lean extraction. The parent archive's existing proof evidence is historical;
this block does not retrospectively re-verify the entire parent library.

Schoolbook bit arithmetic, restoring division and fixed-width circuit accounting
are standard methods. No historical priority or literature-novelty conclusion is
asserted. Review of the statement/implementation correspondence is self-review.
