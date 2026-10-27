# AVOC v0.7.0 development failures and repairs

The following failed attempts are retained as engineering/proof-development history and are not counted as verified results.

1. The first `pushforward_dirac` proof left an equality with the same proposition written in opposite orientations (`φ x = z` versus `z = φ x`). Rewritten using `eq_comm`; final theorem passes.
2. A subsequent over-aggressive `simp` attempt on the same theorem hit maximum recursion depth. It was discarded and replaced by a smaller probability-level simplification.
3. The first Bayes/compression proof used a nonexistent `Finset.sum_div` lemma. The proof was rewritten using `div_eq_mul_inv` and two applications of `Finset.sum_mul`.
4. The first predictive-probability commutation proof attempted to rewrite the fine likelihood sum before applying the factorization hypothesis. It was replaced by an explicit three-step `calc` chain.
5. The first concrete 0.9/0.1 posterior examples attempted definitional `change` through structures carrying proof fields. Lean correctly rejected that dependent reduction. The final proof uses the previously certified conditioning identity and evidence-mass theorem instead.
6. Clean build wrapper calls can outlive the interactive host call. The release used one Lake graph, waited for each bounded child to exit, and resumed without overlapping builders until all 1050 jobs completed.
