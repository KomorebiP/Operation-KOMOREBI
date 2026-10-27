# Lehmer residual audit

**Lehmer's conjecture is not proved.** This bundle contains an attempted proof, exact tests, a counterexample to a specific integral dyadic interpolation model, and the remaining gap.

Start with `RESEARCH_NOTE.md` and `SOURCES.md`.

## Reproduce

Requirements: Python 3.10 or later, SymPy for the optional symbolic check, and a C++17 compiler such as g++. The core integer checks use the Python standard library.

On Linux or WSL:

```bash
bash run_all.sh
python3 check_differential_projector.py
```

On Windows, run the Python scripts separately. Compile `verify_eta_ntt.cpp` using an available C++17 compiler, run the executable, and redirect its output to `eta_ntt_results.txt` before running `validate_results.py`.

The computations are bounded. The full run checks all primes through 20000, twelve selected larger primes, and the stated Hurwitz rows. It is not an exhaustive search through the largest displayed prime.

## Files

- `explore.py`: integer Jacobi recurrence, direct product cross-check, and prime convolution identities.
- `dyadic_check.py`: twelve large prime values from the divisor convolution.
- `verify_eta_ntt.cpp`: independent exact q-series evaluation modulo 2^19. Two NTT primes and a verified CRT reconstruction bound are used.
- `validate_results.py`: cross-comparison and trial-division primality checks.
- `check_trace_inverse.py`: triangular inverse and independent reduced-form Hurwitz calculation.
- `check_differential_projector.py`: exact symbolic certificate in Q[E2,E4,E6].
- JSON files and logs: retained outputs from completed runs.
- `PROVENANCE.json`: environment, commands, scope, and file hashes.

## Failure record

The first combined rerun was mistakenly assigned a one-second tool timeout and was interrupted. The same run was repeated with a 45-second cap and completed. The timeout is an execution configuration failure, not a mathematical counterexample.

The mathematical failures are separate: the proposed integral dyadic interpolation is refuted by two exact values, and the attempted convolution/differential/triangular reductions do not establish nonvanishing.

No Lean compilation was performed. No proof of the earlier Euler claims or earlier archive contents is asserted by this standalone bundle.
