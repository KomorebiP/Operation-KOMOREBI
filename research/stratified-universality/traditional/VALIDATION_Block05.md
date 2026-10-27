# Block 05 validation record

## Mathematical verifier

Command:

```powershell
python .\verify_block05_regular_atlas.py
```

Recorded result:

- raw automata: 25,986
- admissible leading-zero-consistent raw automata: 9,990
- unique minimized automata: 417
- minimized automata with strict state-to-rank compression: 83
- automatic-to-linear checks: 86,207
- exact named-family checks: 2,438
- total checks: 89,055
- failures: 0
- status: PASS

The bounded enumeration verifies reachability, behavioral minimization, canonical linear quotient construction, transition and output equivariance, word-Hankel rank, regular rank, exact finite-orbit recovery, state-to-rank bounds, and coefficient agreement. Exact symbolic calculations separately verify polynomial-rank and digit-sum formulas.

## Regression suites

- Block 03 periodic atlas: 39,805 checks, 0 failures
- Block 04 rational-mask atlas: 11,391 checks, 0 failures
- Block 05 regular atlas: 89,055 checks, 0 failures
- combined: 140,251 checks, 0 failures

## LaTeX and PDF validation

- final length: 103 letter-size pages
- PDF outline entries: 92
- embedded fonts: yes
- encrypted: no
- forms or JavaScript: none
- unresolved references: 0
- undefined control sequences: 0
- multiply defined labels: 0
- overfull boxes: 0
- underfull boxes: 0
- PDF preflight: openable, non-scanned, no XFA
- all 103 pages rendered at 96 dpi and inspected in 12 contact sheets

## Source-package replay

- internal SHA-256 manifest: 102 files verified before replay
- clean extraction: PASS
- Block 03 verifier replay: PASS
- Block 04 verifier replay: PASS
- Block 05 verifier replay: PASS
- figure regeneration: PASS
- LaTeX component regeneration: PASS
- clean `latexmk` rebuild: PASS
- rebuilt page count: 103
- rendered comparison: 103 of 103 pages pixel-identical at 96 dpi

## Boundary

These results certify the declared finite computations, PDF build, and package replay. They do not constitute external peer review and do not prove integral, semiring, all-moduli, or all-radix extensions.
