# AVOC v0.12.0 — development failures and repairs

These are development-time failures, not hidden successful proofs.

1. **Zero-distortion simplifier shape mismatch.** The first proof of exact Q-optimality relied on `simpa` after `abs_nonpos_iff`; Lean had already simplified the absolute-value inequality to a subtraction equality. Repaired with an explicit chain `|x| ≤ 0 -> x = 0 -> lhs = rhs`.

2. **Whole-signature finite sets require finite action equality.** The first finite Q-center-cover module attempted to form `Finset (A -> ℚ)` without enough typeclass information to decide function equality. Repaired by making `[Fintype A] [DecidableEq A]` explicit in the exact finite action-signature layer. This is also the correct modeling boundary for finite action-vector coding.

3. **New dependent module lacked its `.olean`.** Direct compilation of `QRateDistortionFinite.lean` initially failed because the newly created `QRateDistortion.olean` did not yet exist. Repaired by first building the dependency through Lake; all later direct warnings-as-errors checks passed.

4. **Warnings-as-errors caught an unnecessary `simpa`.** The first crossed-signature disequality and max-existence scripts used `simpa` where `simp` was sufficient. The linter rejected the convenience form; scripts were tightened rather than disabling the linter.

5. **Concrete two-signature cardinality did not reduce automatically.** `norm_num` reduced the Bool image to a two-element function set but did not itself prove the two functions unequal. Repaired by supplying the already proved function disequality and then simplifying the finite-set cardinality.

6. **Clean-build UI wrapper outlived the first bounded slice.** The first clean-build tool call timed out while its explicit `timeout 105s lake build AVOC` child was still running. No concurrent build was started. The child was allowed to stop, and all subsequent bounded slices resumed the same clean build graph.

7. **Combined negative-suite calls exceeded the host command window.** Both pre-clean and post-clean batched negative checks hit the execution cap after eight expected failures. The remaining six tests were run separately. All fourteen false files were rejected; no truncated batch was counted as complete evidence.
