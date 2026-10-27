# Block 16 validation record

Date: 2026-08-31  
Release: v1.16.0

## Exact implementation regression

| Validation family | Exact assertions |
|---|---:|
| Group actions and object-orbit descent | 7,780 |
| Pair-orbit partitions and intertwiner bases | 3,537 |
| Orbital path composition and structure constants | 1,212,963 |
| Compatible selectors and negative controls | 994 |
| Equivariant refinement and orbit-projector sums | 10,162 |
| Rational cyclotomic orbit projectors | 109,374 |
| Theorem-source contract | 13 |
| **Total** | **1,344,823** |
| **Failures** | **0** |

The verifier uses exact integer arithmetic, including cleared common
denominators for the rational cyclotomic identities. The frozen seed is
`20260831`.

## Publication-source audit

- Status: PASS
- Checks: 85
- Failures: 0
- TeX input graph: 60 files
- Abstract: 346 words
- Labels: 542
- Cross-references: 138
- Citation keys: 14
- Graphics: 57
- Integrated PDF: 239 pages

## Baseline preservation

The Block 15 verifier was rerun unchanged:

- Status: PASS
- Assertions: 197,099
- Failures: 0

## Interpretation

The exact suites are finite regression records for selected implementation
clauses and release contracts. The symbolic proofs do not depend on sampling,
and the computations do not constitute independent proof review or historical
novelty verification.
