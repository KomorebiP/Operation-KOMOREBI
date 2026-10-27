# Failure ledger — v0.35

## Runtime and execution

- No Lean runtime was initially mounted. The seven archived offline parts were materialized, CRC/read checks and each part SHA-256 were checked, and the assembled archive matched SHA-256 66dfa8ce4627489bc61e44a77782931d36c1b626a177790a5d4599034b70ec34. Extraction completed with exit code zero.
- Streaming execution was unavailable (`StreamingExecNotEnabledContainerError`). The work used synchronous bounded calls instead.
- The first LEAN_PATH probe ran outside the portable workspace and returned only the toolchain path. It was rerun from the documented workspace before any accepted proof compilation.
- An initial broader dependency replay was interrupted before PrimaryBlockNorm completed. That broad dependency is not needed by the accepted route. The final closure uses the narrower inherited NilpotentPolynomialImage theorem and freshly recompiles all required dependencies.
- One first-release replay wrapper was interrupted after 23 successful source modules. No complete success was inferred from that wrapper. The unchanged source hashes and prior object/log hashes were checked by the resumable verifier; all remaining modules and the axiom audit subsequently completed with zero exit codes.

## Rejected proof drafts

The development directory preserves diagnostics from rejected attempts. The main corrections were:

- An induction over the norm degree accidentally generalized hypotheses that depend on the degree. The proof cleared unrelated data before that induction.
- An application of a product of endomorphisms needed `Module.End.mul_apply` before the coordinate theorem could rewrite it.
- A section parameter used only in a proof needed an explicit `include`; unused section typeclasses were explicitly omitted instead of disabling warnings.
- Recursive modulus and compatibility wrappers required reducible definitions to avoid mismatched implicit-transparency typechecking.
- Matrix-unit values and inverses needed explicitly typed compatibility lemmas rather than relying on hidden coercion conversions.
- ZMod integer-cast divisibility has a specific subtraction orientation. The coordinate compatibility proof was corrected to that orientation. An unrestricted cast simp set looped; it was replaced by explicit identities.
- The first concrete unipotent-adjoint matrix expansion did not normalize to entries. The final finite identity was kernel checked by `decide` on its actual finite coefficient matrices, then promoted to a linear-map equality. No native_decide was used.

No rejected draft, timed-out module or incomplete replay is counted as a theorem certificate. The final source snapshots and axiom logs are the evidence.
