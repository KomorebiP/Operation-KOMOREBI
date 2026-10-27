# AVOC v0.32.0 — development failures and repairs

1. **Concrete evaluator examples initially used `by decide`.** The larger
   evaluator reductions did not close reliably under the pinned kernel, and
   using `native_decide` would have violated the project audit boundary. The
   universal evaluator theorem remained in Lean; only small rational facts were
   kept as kernel examples, while exact catalogue choices/values were checked
   through the executed Lean entrypoint and an independent Python oracle.
2. **Immediate-reward rewrites initially unfolded model structures too early.**
   The proofs were repaired by exposing the exact `successProb` term, applying
   the proved probability equality, and then normalizing the rational arithmetic.
3. **Several bounded build calls hit the host execution limit.** Their unfinished
   targets were not counted. The dependency-aware builder was rerun until all
   176 current targets had successful current-source records.
4. **The first large negative-test batches hit the outer execution limit.** The
   remaining files were rerun in smaller sequential slices. Final evidence
   contains 91 current substantive rejections.
5. **The first evidence collector treated the final malformed-request batch as a
   normal valid-request batch.** Invocation-hash validation was corrected to
   check the four valid batches and the malformed batch separately, then rerun.
6. **Direct `lean --run` initially omitted package search paths.** Development
   executions were corrected to use the pinned package paths; the delivered
   wrapper constructs them and validates current source/object records.

No failed route was counted as a proof or runtime success. No placeholder or
custom axiom was introduced to bypass these issues.
