# Block 10 validation record

## Exact theorem verifier

Command:

```powershell
python .\verify_block10_algebraic.py
```

Recorded result:

```text
checks: 73088
failures: 0
cumulative: 1911944
```

Category totals:

| Category | Checks |
|---|---:|
| General residue-packet compiler | 3,690 |
| Catalan sharp parity theorem | 7,426 |
| Quadratic-radical collision phase | 43,900 |
| Finite branch selectors | 16,632 |
| Collision-ledger combinatorics | 1,440 |
| **Total** | **73,088** |

The verifier uses exact `Fraction` and SymPy polynomial arithmetic. Floating point is not used to certify any algebraic identity.

## Frozen regression records

The normal replay verifies the machine-readable records for Blocks 03 through 09:

```text
PRIOR_REGRESSION_RECORDS=PASS
BLOCK03_TO_BLOCK09_RECORDED_CHECKS=1838856
```

The `-FullRegression` build option recomputes those earlier verifiers rather than only authenticating their frozen records.

## LaTeX validation

- final PDF pages: 167
- page size: US letter
- outline entries: 140
- unresolved references: 0
- undefined control sequences: 0
- multiply defined labels: 0
- overfull boxes: 0
- underfull boxes: 0
- embedded fonts: yes
- encryption: none
- interactive forms or JavaScript: none

## Visual replay

The final PDF and a cleanly extracted source replay were rendered at 96 dpi. All 167 corresponding pages were pixel-identical.

## Claim boundary

The exact computation supports the residue compiler and the named Catalan, Motzkin, and quadratic-radical model cases. It is not evidence that every algebraic packet eliminant is minimal or that one finite invariant classifies arbitrary multivariate polynomial grammars.
