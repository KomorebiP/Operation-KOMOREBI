# Block 11 validation record

## Exact theorem verifier

Command:

```powershell
python .\verify_block11_nonlinear_tree.py
```

Recorded result:

```text
BLOCK11_CHECKS=115721
BLOCK11_FAILURES=0
BLOCK03_TO_BLOCK11_CUMULATIVE=2027665
BLOCK11_NONLINEAR_TREE=PASS
```

Category totals:

| Category | Checks |
|---|---:|
| Colored profile counts | 100 |
| Orbit-size identity | 48 |
| Exact compressed Faà di Bruno values | 126 |
| Polynomial fixed-point prefixes | 300 |
| Finite tree-address signatures | 70,458 |
| Fuss-Catalan formulas | 2,892 |
| Exact q-ary packet systems | 37,567 |
| Dominant-orbit combinatorics | 176 |
| Dependency-core reductions | 4,054 |
| **Total** | **115,721** |

The verifier uses exact integer and rational combinatorics. Floating point is not used to certify the Faà di Bruno, fixed-point coefficient, packet-support, Fuss-Catalan, packet-equation, or graph-reduction identities.

## Frozen regression records

The normal replay authenticates the machine-readable records for Blocks 03 through 10:

```text
PRIOR_REGRESSION_RECORDS=PASS
BLOCK03_TO_BLOCK10_RECORDED_CHECKS=1911944
```

The `-FullRegression` build option recomputes those earlier verifiers rather than only authenticating their frozen records.

## LaTeX validation

- final PDF pages: 180
- page size: US letter
- outline entries: 149
- unresolved references: 0
- undefined control sequences: 0
- multiply defined labels: 0
- overfull boxes: 0
- underfull boxes: 0
- embedded fonts: yes
- encryption: none
- interactive forms or JavaScript: none
- rendered pages inspected: 180
- normal build replay: PASS
- source manifest: PASS
- rendered clean-replay comparison: 180 of 180 pages identical at 96 dpi

## Claim boundary

The exact computation supports the repeated-direction compression theorem, marked polynomial fixed-point prefixes, arity-gcd support theorem, full q-ary packet equations, singularity-orbit combinatorics, and bounded dependency-core reductions. It is not evidence for a universal nonlinear normal form, arbitrary mixed-direction compression, coordinate-free minimal system dimension, or global noncontractive dynamics.
