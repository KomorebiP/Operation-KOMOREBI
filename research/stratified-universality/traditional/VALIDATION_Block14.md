# Validation record - consolidated foundations edition

## Publication-source audit

- audit assertions: 41
- failures: 0
- abstract length: 240 words
- recursively loaded TeX sources: 51
- labels: 477
- cross references: 124
- cited bibliography keys: 14
- included graphics: 57

The audit checks the source graph, generated inputs, required theorem labels, duplicate and unresolved labels, citation keys, graphics, publication proof order, environment balance, and explicit relative-universality and independent-validation boundaries.

## Mathematical and computational replay

The normal replay executed the current verifier chain:

- authenticated frozen exact records through the algebraic atlas: 1,911,944 assertions
- nonlinear tree verifier: 115,721 assertions
- finite Galois and Tannakian verifier: 11,195 assertions
- global bridge-synthesis suite: 154,209 assertions
- global weighted-Fuss and tagged-invariant suite: 119,453 assertions
- failures: 0

The global suites include 39,846 replay or authentication assertions already represented in the preceding cumulative record. The nonduplicated cumulative exact record remains 2,272,676 assertions. The raw executed total including the global replay is 2,312,522. These are implementation assertions, not counts of independent theorems.

## LaTeX and PDF preflight

- final PDF pages: 209
- PDF outline entries: 182
- page size: US letter
- LaTeX overfull boxes: 0
- LaTeX underfull boxes: 0
- unresolved references or citations: 0
- undefined control sequences: 0
- fonts embedded: yes
- encrypted: no
- XFA: no
- JavaScript: no
- likely scanned: no
- pages rendered and visually inspected: 209

The one-command normal replay completed every verifier, data assembly, figure-generation, table-generation, and publication-audit stage. It exceeded the command window during the final third TeX pass. A subsequent standalone `latexmk` invocation completed the cross-reference pass with a clean log.

## Clean extraction replay

- source manifest verification: PASS
- clean auxiliary-file reset: PASS
- clean TeX passes: PASS
- clean replay PDF pages: 209
- clean replay warning scan: 0 unresolved references, citations, controls, overfull boxes, or underfull boxes
- rendered-page comparison at 96 dpi: 209 of 209 pages pixel-identical

The first combined clean-replay command was interrupted during its initial TeX stage by the execution window, leaving incomplete auxiliary files. Those files were removed, and three clean standalone `pdflatex` passes completed successfully. The resulting PDF has the same rendered content as the final publication PDF on every page.
