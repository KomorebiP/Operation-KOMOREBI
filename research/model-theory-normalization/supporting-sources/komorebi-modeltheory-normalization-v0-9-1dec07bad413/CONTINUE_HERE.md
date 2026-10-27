# Continuation from v0.9

1. Treat this v0.9 archive as the immediate checkpoint. Check the delivered SHA256
   and run distribution integrity before regenerating evidence.
2. Read NORMALIZED_CORE.md, COST_MODEL.md, FORMALIZATION_COVERAGE.md, RESULTS.md,
   PROOF_AUDIT.md and DEVELOPMENT_FAILURES.md. Read all four Costed*.lean generic
   modules before modifying their semantics.
3. Preserve the value/refinement theorem, the exact operation-charge contract,
   every failed attempt, and all negative controls. Do not relabel an arithmetic
   unit count as compiled execution time or a bit-operation theorem.
4. The next precise goal is an operand-sensitive priced-arithmetic evaluator plus
   a proved cost refinement. It must account for source-row work and both gcd and
   extended gcd, and explicitly handle arrays/sharing, access and queue overhead.
   Verified binary arithmetic or an appropriate trusted backend theorem is a
   separate input, not something established by testing 203 cases.
5. A useful intermediate step is a generic pricing theorem for the actual trace,
   bounding separate integer/residue events with the correct magnitude budgets.
   Keep constant-time semantic ring operations distinct from their bit costs.
6. Keep the synthetic/regression character of the 203 profiles explicit. Neither
   trained discovery nor a held-out mathematical result has been established.
