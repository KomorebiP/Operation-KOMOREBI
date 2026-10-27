# Failures and limitations

1. The first principal-matrix Lean draft used subtraction directly on a nested
   product. Bundled Std did not synthesize that subtraction instance. The failed
   source and compiler diagnostic are retained. The corrected statement writes
   the three coordinates explicitly; the mathematical identity is unchanged.
2. The first transfer proof used the unqualified name `pow_succ`, unavailable in
   this Std scope, and a dependent local induction inherited unnecessary
   hypotheses. It was changed to `Int.pow_succ` and a separate universal zero-sum
   lemma. The failed draft/log are retained. No hypothesis was weakened.
3. A model proof had an unused `simp` argument. Warnings-as-errors rejected it;
   removing that argument corrected the linter issue.
4. The naive mathematical identity product_k F(z+k delta7)=F(beta z) is FALSE.
   Its exact divisor obstruction is proved in section 2 and the correct
   three-factor identity is retained. This failure is not a numerical error.
5. The principal-norm relation does not imply flattening for an arbitrary C^2
   logarithm. Section 6 gives an exact counterexample; the positive theorem
   retains its smoothness/global-holomorphic assumptions.

The new accepted exact, numerical, and Lean checks pass. No full inherited Lean
replay, no gamma/model scalar construction, and no original gamma-arithmetic
identity is claimed. The portable archive was reconstructed locally and its
complete SHA-256 matches the pinned hash. Only its toolchain was extracted.
