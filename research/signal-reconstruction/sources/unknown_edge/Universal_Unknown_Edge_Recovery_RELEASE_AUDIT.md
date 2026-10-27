# Release audit

## Mathematical scope

The release proves an exact unknown-edge recovery theorem for periodic signals formed from a bandlimited background and finitely many off-grid piecewise-constant jumps. It also proves a dimension-independent finite dictionary theorem and several exact extensions under stated rank conditions.

## Generated content

- 67-page PDF
- complete LaTeX source
- KaTeX-friendly derivation
- one closed Python implementation
- 35 vector-PDF figures
- 35 matching PNG figures
- 5 CSV tables
- 1 JSON result ledger
- full contact sheet

## Tests

The Python implementation returned 19 passes from 19 named checks.

## Numerical highlights

- maximum representative location error: `4.6629367034256575e-14`
- maximum representative jump error: `2.9309921493206785e-13`
- representative complete reconstruction error: `3.8191672047105385e-14`
- maximum complete reconstruction error across four exact cases: `3.9601655288379334e-13`
- finite dictionary support recovered: `[1, 5]`
- finite dictionary restricted separation: `0.5116895108313039`
- two-dimensional rectangle recovered: `[6, 8, 5, 6]`
- symbolic annihilator: `z**4 - 1`
- symbolic Hankel determinant: `6144`

## PDF audit

- page count: 67
- encrypted: no
- scanned-only: no
- preflight warnings: 0
- overfull boxes: 0
- underfull boxes: 0
- undefined references: 0
- multiply defined labels: 0
- visible semicolons: 0
- pages with fewer than 20 extracted words: 0
- embedded fonts: yes
- pages rendered at 180 DPI: 67 of 67

The full contact sheet and several dense pages were inspected at full resolution. No clipped text, overlapping legends, misplaced colorbars, missing panels, or broken glyphs were found.

## Rebuild audit

The Python source compiles and regenerates all figures, tables, and result files. The LaTeX source compiles in two passes with no reported layout warning.

## Claim boundary

The release does not promote finite experiments to a universal noisy theorem. Exact recovery requires the declared finite-rate class and distinct nonzero jumps. Local stability requires quantitative separation and conditioning. Arbitrary continuous two-dimensional geometry remains outside the result.

## Archive validation

The complete release archive passed 90 internal checksum entries. The source archive passed 87 internal checksum entries. A clean source extraction regenerated all figures and tables, returned 19 of 19 checks, and rebuilt the same 67-page manuscript without LaTeX layout warnings.
