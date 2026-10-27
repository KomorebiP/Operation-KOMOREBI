# Failures and corrections

The first Lean compilation failed because `prefix` is a reserved Lean token.
The draft source and raw diagnostic log are retained as
`failed_reserved_identifier.lean` and `failed_reserved_identifier.log`.
The definition was renamed `partialSum`; no mathematical statement was weakened.
An unused nonzero hypothesis in the separate modular-multiple identity was
removed, yielding the stronger theorem valid also at modulus zero in Lean.
After these syntax/proof-cleanup changes all 28 theorems and the complete axiom
audit passed, and the false arithmetic control was rejected.

The first broad public search returned mostly irrelevant pages. Exact arXiv
identifiers gave the primary sources recorded in SOURCE_CHECK.md. No inference
was based on the irrelevant results.

No numerical target matching was attempted. No run claimed to construct the
actual gamma comparison multiplier. The main proof route remains open at that
construction and its Fourier cancellation identities, not at Lean syntax.
