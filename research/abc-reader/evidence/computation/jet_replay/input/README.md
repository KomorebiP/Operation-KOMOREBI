# Komorebi ABC — Jet Determinant Block 01

Date: 2026-09-19
Status: written mathematical proofs + executed exact Python verification.
Lean status: uncompiled source; compiler unavailable in this runtime.
ABC status: not proved.

## Main result

The continuation constructs the shifted Hankel determinant

\[
\mathcal H_r(t)=\det(\operatorname{Li}_{i+j+1}(t))_{0\le i,j<r}.
\]

It has exact Taylor contact r(r+1)/2 and is strictly positive for 0<t<1.
An all-rank formula gives the exact valuation of its p-depleted version. The
undepleted universal expression has the same exact contact at primes p>3r-1 and
a fixed, explicit small-prime denominator budget elsewhere.

These are local/formal/analytic results, not the missing global arithmetic realization.

## Important correction

The preceding target Q=R^{o(1)} with Q=abc/R is false. The correct defect is
Q/(ab)=c/R. The counterexample family and an unavoidable leading-cost theorem are
proved in proofs/01_Target_Correction.md.

## An attempted global scalar

The obvious finite rational truncation fails: clearing denominators destroys the
output-prime contact for every prime greater than the truncation level. This is
proved exactly, not inferred from finite optimization failure.

## Contents

- proofs/: six complete mathematical notes, including the corrected open bridge.
- verification/verify.py: standard-library-only exact verifier.
- verification/results.json and run.log: accepted execution record.
- verification/failed_shifted_run.log: an implementation failure retained transparently.
- formalization/lean/: seven uncompiled elementary algebraic Lean proof scripts.
- formalization/LEAN_STATUS.md: explicit compiler and formalization boundary.
- source_context/: the preserved 361-row predecessor triangle corpus.
- DEVELOPMENT_FAILURES.md, SOURCE_MAP.md, CONTINUE_HERE.md, SHA256SUMS.txt.

## Reproduce exact verification

```text
python verification/verify.py
```

The accepted run recorded 149,306 finite assertions, including 504 exact modular
determinant valuations and 361 stored triangle rows. These counts are finite
verification support, not substitutes for the general proofs or evidence of an ABC solution.

The verifier requires Python 3.10 or later and no third-party package. It was run
with Python 3.13.5. Hashes are provided for every packaged file except SHA256SUMS.txt itself.
