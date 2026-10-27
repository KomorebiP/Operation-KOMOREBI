# Computation and figure report

The exact Collatz computations verify the accelerated orbit examples and bounded cylinder checks. The xi and Hermite computations pass numerical consistency controls. Two RH panels are schematic.

## Contract

* Collatz: six odd starting values, a 512-step cap, exact integer/Fraction arithmetic.
* Cylinder check: all 120 words of length 1–4 over exponents 1–3, tested against every odd n from 1 to 4,095.
* Xi: 701 points from t=0 to 35 at 50 decimal digits, with nine 75-digit and Hardy-Z controls.
* Hermite: orders 0–3, finite trapezoid Gram check on 8,001 points in [-10,10].
* Saved coverage input: 1,804 covered and 244 unresolved among 2,048 odd classes modulo 4,096. This count was not replayed.

## Results

* 148 exact iterate and descent-inequality checks passed.
* 245760 exact word/cylinder membership checks passed.
* n=27: first source descent at odd step 37, x=23, S=59; intermediate 31 follows 41 but exceeds 27.
* The r2>=4 tail of the r1=1 branch was checked on every representative n<=4095.
* 701 critical-line xi evaluations passed the realness tolerance 1e-45 at 50 decimal digits.
* Nine Hardy-Z cross-checks and nine 75-digit recomputations passed absolute tolerance 1e-45.
* Three functional-equation controls passed absolute tolerance 1e-65 at 75 decimal digits.
* First four Hermite functions passed a finite trapezoid Gram check to 1e-12 on 8,001 points.

The first descent of 27 occurs at accelerated step 37, with x=23, S=59, and C=1100931843921811423. At step 2, 31 is below the preceding 41 but above the source 27.

## Reproduction

Install the exact versions in figures/requirements.txt, then run:

```bash
python shared/figures.py
```

Tested interpreter: Python 3.12.14. Matplotlib 3.10.8, NumPy 2.3.5, mpmath 1.3.0.

Execution environment note: Default and primary Python imports of mpmath initially failed with ModuleNotFoundError. Execution used recovered local mpmath 1.3.0 through PYTHONPATH; public source uses an ordinary import and pins dependencies. Initial figure rendering failed on Matplotlib fraction shorthand; brace syntax corrected the label and rerun succeeded.

Numerical xi values are not interval certificates. The finite Collatz checks do not establish universal descent. The barrier-rate curves use a common unit normalization. The heat-front curves model isolated amplitude envelopes exp(delta*u), omitting the fixed heat multiplier, and do not represent observed off-line zeros. The Hermite functions illustrate a basis only.

Generated eight vector PDF figures and eight 220-dpi PNG counterparts in 6.91 seconds. Exact rational orbit data, numerical xi samples, and control outputs are in figures/data.json.
