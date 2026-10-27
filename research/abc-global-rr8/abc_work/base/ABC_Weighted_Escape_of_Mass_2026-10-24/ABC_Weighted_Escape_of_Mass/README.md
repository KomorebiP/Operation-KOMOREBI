# ABC weighted escape of mass research handoff

This archive contains a continuation of the Komorebi ABC work. General ABC is **not proved**.

Contents:
- `ABC_Weighted_Escape_of_Mass.md`: complete note with theorems and proof boundaries
- `verify.py`: reproducible finite arithmetic tests (pure Python stdlib)
- `results.json`: output of `python verify.py`
- `RUN_LOG.txt`: actual verification command and outcome
- `CLAIM_LEDGER.md`: concise theorem/assumption status
- `SHA256SUMS.txt`: SHA-256 digests of the other files

Verification: run `python verify.py`. Expected `PASS all checks`.

External imports: classical Chebyshev prime bounds and Yu's p-adic logarithmic-form theorem. No Lean compilation was performed. Infinite assertions are mathematical proofs or stated applications of published theorems, not inferred from finite samples.
