# Release audit

## Artifact summary

- Title: Projector-Generated Special Functions IV
- Author: Komorebi P.
- PDF pages: 55
- Vector figure files: 28
- Matching PNG figure files: 28
- Built-in checks: 18 of 18
- Independent tests: 18 of 18

## Mathematical audit

The release distinguishes the unconditional positive-kernel results from the conditional signed finite reduction and the open principal-coherence problem. The `n = 1` packet is separated from the number-basis scale operator because `-log(1 - n^-beta)` is singular there. It contributes only at depth zero.

## Document audit

- PDF opens successfully
- PDF is not encrypted
- PDF preflight warnings: 0
- no overfull LaTeX boxes
- no underfull LaTeX boxes
- no undefined references
- no duplicate page anchors
- no extracted word boxes outside the page
- all 55 pages rendered at 180 DPI
- complete contact sheet inspected
- dense figure, table, verification, and code pages inspected at full resolution
- no blank-like content pages
- no prose semicolons in the manuscript

## Reproducibility audit

The source includes the Python generator, table generator, independent tests, requirements, all generated figures and tables, and the complete LaTeX source. `build_all.py` regenerates the computational outputs, runs the tests, and compiles the paper.
