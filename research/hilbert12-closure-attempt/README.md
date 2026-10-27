# Pure cubic Hilbert 12 closing audit

This research checkpoint contains a weighted transport obstruction, an exact arithmetic certificate for the target, and a rational interval comparison.

**Status:** the elliptic gamma to class field equality is not proved. The interval certificate proves a ratio distance below `10^-60`, which resolves the branch condition but not exact equality.

## Reproduce the interval and finite transport checks

Python 3.11 or later, standard library only:

```sh
python h12_closure_verify.py --json certificate.json
python h12_closure_verify.py --terms 3400 --json certificate_replay.json
```

## Reproduce the arithmetic polynomial checks

Python with SymPy installed:

```sh
python h12_arithmetic_certificate.py
```

Read `H12_Closure_Attempt_Research_Note.md` for the proofs, exact remaining obligation, and verification scope. The JSON certificates contain integer interval endpoints and explicit truncation parameters. No numerical recognition is used as a proof of equality.
