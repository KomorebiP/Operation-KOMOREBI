# Reproduce the sharp quadratic and uniform mixed-family theorems

Extract assets/sequence-formula-source.zip and work from the extracted root.
Python 3.10+ with its standard library is sufficient:

```text
python -B tools/verify_sequence_sharp_quadratic.py --output sharp-quadratic.json
```

The program uses exact sparse Laurent polynomials in n,z,w. It checks
termwise divisibility, all nine degree-six coefficient groups, all coefficients
of the four initial-boundary identities, the value 1/2 at zero, the branch
differential equation and both quartic root factorizations. These are complete
symbolic identities, not parameter sampling.

Separate finite regressions compare Rodrigues and Chebyshev constructions
through degree 20, verify their formal orthogonality and norms, and compare
16 transformed determinant values with direct monomial determinants. Nine
integer parameter cases produce 810 direct monomial block determinants and
225 recurrence residues at indices 1 through 25. Their index-zero residues
match the stated exceptional value. These finite checks alone do not establish
the theorem; read SHARP_QUADRATIC.md for the universal formal-moment,
determinant, exponential-polynomial and specialization argument.

The retained output is
verification/sequence-library/hankel-compression/sharp-replay.json.
Runtime varies; compare mathematical fields rather than elapsed_seconds.
The replay imports no exploratory SymPy code or preceding transfer code.
SHARP_QUADRATIC_REVIEW.md records the project self-review and its limits.

Replay the mixed-family extension from the same extracted root:

```text
python -B tools/verify_sequence_uniform_mixed.py --sample-certificate verification/sequence-library/hankel-compression/mixed-certificate.json --output uniform-mixed.json
```

This program checks the complete quartic boundary identities using a separate
sparse polynomial ring, the sixteen resultant/Newton traces, the sample
degree-16 factor, reconstruction of the sample numerator and its modular
Bezout coprimality witness. It also checks 330 functional moments, 170 direct
monomial determinants and 200 recurrence residues across ten parameter cases.
Its finite regressions use the retained exact Schur solver and direct Bareiss
determinants. Read UNIFORM_MIXED_RECURRENCE.md for the universal quartic proof,
the linear-weight/first-order application, and the nonempty-open-set
generic-minimality argument. UNIFORM_MIXED_REVIEW.md records the self-review.
The retained output is verification/sequence-library/hankel-compression/uniform-mixed-replay.json.

The preceding five replay commands and their exact certificate inputs remain
unchanged in HANKEL_COMPRESSION_REPRODUCE.md. The old order-126 proof is
retained; its bound is sharpened by the new order-63 theorem. The previous
74-member source ZIP is retained byte-for-byte as
research/sequence-closed-forms/retained-sources/sequence-formula-source-595aa4a6.zip,
with SHA-256 daf022ed9211342577192b9a43ed208edfba1ba42dac9e02636f3d8e98090b66.
