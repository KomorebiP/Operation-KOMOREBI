# Block22 development and verification notes

Base: Block21 final archive SHA256 fbe69e04d5e693f6f91b7af7090b04ec43a3467feea1c17cd53fbc9cd9cffbf2. All 138 predecessor production sources are retained.

The first local restriction proof compiled mathematically but its proof-local letI triggered the style linter; changing it to let preserved the same instance and proof. A subsequent root-choice invariance proof needed an explicitly typed map_neg equality because the absolute-Galois abbreviation hid the algebra-automorphism interface from simplification.

The p-adic square-root proofs initially needed an explicit prime-five instance, precise derivative evaluation and coercion lemmas. An incorrect guessed lemma name was replaced by the actual pinned API. The valuation proof initially used neg_mem with the wrong argument count and a scalar-action power rewrite in the wrong form. An explicit ring-automorphism power identity resolved it. None of these corrections changed the mathematical hypotheses.

The local packet builder corrected an underspecified map_one after extensionality by naming the homomorphism. The inertia integration renamed an unused proof binder; compilation of its dependent arithmetic wrapper before that object existed failed and was rerun afterward.

The first final arithmetic wrapper had two rejected proof scripts. One left a definitionally equal ZMod4 versus ZMod(2^2) goal, resolved by rfl. The other ran decide after a rewrite had already closed the goal, so that redundant tactic was removed. The independent audit observed the same errors. These failures were not counted as successful evidence, and no statement was weakened.

The independent audit initially attempted separate PaperX object directories in LEAN_PATH, but Lean resolves the first namespace directory instead of merging the two trees. Its harness was corrected to combine the hash-verified archived predecessor objects with fresh audit objects in one isolated directory. The audit preserves the rejected attempt logs. Exact finite computation and replay succeeded; unavailable Git metadata is reported rather than invented.

All accepted evidence is tied to the frozen final sources. The final cumulative verifier, transitive axiom audit and fresh-archive replay are separate from development compiles. The full ledger remains 15 checked / 5 partial. Inertia means the actual residue-action kernel inside a valuation decomposition group; this release does not identify that decomposition group with the whole local absolute Galois group or prove ramification at the prime 2.
