# Block 12 validation record

## Exact theorem verifier

Command:

```powershell
python .\verify_block12_galois_tannakian.py
```

Recorded result:

```json
{"checks": 11195, "failures": 0, "groups": 10, "passed": true}
```

Category totals:

| Category | Checks |
|---|---:|
| Finite subgroup and Reynolds-projector identities | 1,020 |
| Normality, core, and normal-closure identities | 192 |
| Double-coset and Mackey packet identities | 1,590 |
| Nested ramification-style projector filtrations | 39 |
| Exact Hilbert 90 cocycles over Gaussian rationals | 884 |
| Projective and Brauer obstruction examples | 44 |
| Finite faithful tensor-model checks | 7,426 |
| **Total** | **11,195** |

The verifier uses exact rational group-algebra arithmetic, exact permutation and subgroup combinatorics, and exact Gaussian-rational matrices. Floating point is not used to certify the subgroup, double-coset, Hilbert 90, Brauer, ramification, or finite tensor identities.

## Frozen regression records

The normal replay authenticates the machine-readable records for Blocks 03 through 10 and recomputes Blocks 11 and 12:

```text
PRIOR_REGRESSION_RECORDS=PASS
BLOCK03_TO_BLOCK10_RECORDED_CHECKS=1911944
BLOCK11_CHECKS=115721
BLOCK11_FAILURES=0
BLOCK12_CHECKS=11195
BLOCK12_FAILURES=0
BLOCK03_TO_BLOCK12_CUMULATIVE=2038860
```

The `-FullRegression` option recomputes the earlier verifier suites rather than only authenticating their frozen records.

## LaTeX and PDF validation

- final PDF pages: 194
- page size: US letter
- outline entries: 160
- unresolved references: 0
- undefined control sequences: 0
- multiply defined labels: 0
- overfull boxes: 0
- underfull boxes: 0
- embedded fonts: yes
- encryption: none
- interactive forms or JavaScript: none
- rendered pages inspected: 194
- source manifest: 231 entries passed
- normal build replay: PASS
- rendered clean-replay comparison: 194 of 194 pages identical at 96 dpi

The initial one-shot clean replay exceeded the execution window during the first LaTeX pass. All verifier and figure-generation stages had completed. The interrupted auxiliary files were removed, a fresh clean `latexmk` pass completed successfully, and the rebuilt PDF matched the final PDF on every rendered page.

## Claim boundary

The exact computation supports the finite subgroup and Reynolds identities, normality and envelope calculations, Mackey packet counts, declared ramification filtrations, explicit Hilbert 90 coboundaries, the split and quaternionic projective examples, and finite faithful tensor actions. It is not evidence for modular semisimplicity, wild integral descent, nonneutral Tannakian effectivity, or a general heterogeneous stack theorem.
