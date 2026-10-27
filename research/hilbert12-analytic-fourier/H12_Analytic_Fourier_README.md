# Hilbert 12 Ambient Cubic Fourier Attempt

Author: Komorebi P.

This package contains a new exact algebraic continuation of the pure cubic Hilbert 12 program together with an explicit meromorphic gamma candidate and numerical diagnostics.

## Included files

- `H12_Analytic_Fourier_Resolvent_Research_Note.md` — mathematical setup, proofs, conditional analytic targets, and scope.
- `H12_Analytic_Resolvent_Verifier.py` — exact SymPy polynomial audits and independent mpmath fifth-smoothed gamma series.
- `H12_Analytic_Resolvent_Verification_Log.txt` — accepted exact checks, gamma data, and negative control.

## Reproduce

Requires Python 3 and `sympy` and `mpmath`.

```bash
python H12_Analytic_Resolvent_Verifier.py --exact-only
python H12_Analytic_Resolvent_Verifier.py --dps 64 --nbase 4000 --n10 19000 --n23 34000 --negative-control
```

All work is offline.

## Established

- Exact order three Möbius action extending the Galois action on the cubic roots.
- An invariant quotient coordinate and a one parameter cyclic cubic pencil.
- Exact perfect square discriminant and the three deformed Fourier identities.
- A canonical rational analytic gamma candidate and an explicit scalar obstruction.
- An algebraic reduction to gamma chart orbit identities plus trace normalization.
- Numerical agreement at conductor three, with a separate negative control at one quarter.

## Not established

- The analytic gamma chart orbit relations.
- The exact trace normalization of those analytic values.
- The vanishing of the gamma scalar obstruction at one third.
- The elliptic gamma/class field equality or Hilbert's twelfth problem.

The numerical log does not constitute an interval proof. The analytic series tail has a mathematical bound, but the floating point operations themselves are not directed interval computations. The first attempted numerical run had prematurely rounded `1/3`. The accepted log was generated after correcting this precision issue.
