# ABC two-axis first-shell sieve — reproducible checkpoint

* `PROOF_NOTE.md`: definitions, unconditional theorems and proofs, exact counterexample, limitations.
* `CLAIM_LEDGER.md`: explicit classification of proved, computed, and open statements.
* `verify.py`: standard-library Python 3 verifier. Run `python verify.py`.
* `results.json`: exact-assertion verification output from the verifier. Rounded display metrics only, all congruence assertions are integer-exact.
* `SHA256SUMS.txt`: hashes of the four files above.

The output is a research checkpoint, not an ABC solution or a Lean-certified release. The routine computes no huge exponential integers for the moving-window tests; it uses modular exponentiation and separately validates arithmetic-progression counts.

The strengthened prime-multiplier section invokes Brun–Titchmarsh, a published standard sieve theorem. The verifier checks the progression counts and primality exactly in finite ranges; it does **not** verify Brun–Titchmarsh itself.
