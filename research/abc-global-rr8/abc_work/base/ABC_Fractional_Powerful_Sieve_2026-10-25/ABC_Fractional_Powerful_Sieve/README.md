# ABC fractional powerful-part sieve — reproducible handoff

## Contents
- `PROOF_NOTE.md` — explicit definitions, positive powerful-divisor identity, proof of bounded fractional moments, and a simultaneous density-one ABC non-hit theorem for fixed S-smooth input alphabets
- `verify.py` — standard-library-only integer factorization, exact divisor-expansion checks, several finite exponent/multiplier windows and a genuine exceptional ABC hit
- `results.json` — produced by `python verify.py`
- `CLAIM_LEDGER.md` — status of verified, externally dependent and unresolved claims
- `SHA256SUMS.txt` — checksums for the files above

## Reproduce
Run `python verify.py` from this directory. The checks use finite arithmetic and do not replace the analytic proof; the classical Brun–Titchmarsh theorem remains an external dependency.

## Scope
The unrestricted abc conjecture is **not** proved. The theorem bounds exceptional prime multipliers when the other input factor is an S-unit whose size is at most H^(1-eta). It does not give a pointwise result for every multiplier or cover S-units as large as h or larger. New Lean verification is not included.
