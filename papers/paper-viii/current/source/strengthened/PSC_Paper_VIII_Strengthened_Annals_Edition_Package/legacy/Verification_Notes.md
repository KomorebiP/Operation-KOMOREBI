# Verification Notes

## Projector-Resolved Seed Calculus VIII
### Packet Algorithms and GPU Realization: Dense Operators, Block Transfer, and CUDA

**Author:** Komorebi P.

## Build

- Final PDF: `Projector_Resolved_Seed_Calculus_VIII.pdf`
- Final page count: 26
- LaTeX engine: `latexmk` with `pdflatex`
- Undefined references: none
- Overfull boxes: none
- Underfull boxes: none reported
- Paper-local citations: none
- Paper-local bibliography: none
- Figures: 18 PNG and 18 vector-PDF files
- PNG ancillary metadata: removed
- Vector-PDF metadata: title and **Komorebi P.** only

## Automated tests

```text
23 passed
```

The suite verifies:

- packet decomposition and materialization;
- block-diagonal application and solve;
- BDLR application, Woodbury solve, and compressed product;
- block-sparse application;
- arithmetic and storage formulas;
- exact amortization thresholds;
- mixed-precision error bounds and KKT allocation conditions;
- packet-preconditioned conjugate gradient;
- full-step Lanczos eigenvalue recovery in a finite model;
- benchmark schema, counts, fairness rules, and negative controls;
- sanitization of local paths and user identifiers;
- generation of every figure pair.

## Finite numerical certificates

| Certificate | Result |
|---|---:|
| BDLR apply residual | `2.7395048403e-14` |
| Woodbury solve residual | `1.6187860978e-15` |
| compressed BDLR product residual | `4.1037498536e-13` |
| block-sparse apply residual | `2.5216318512e-14` |
| mixed-precision actual error | `1.2613779813e-02` |
| mixed-precision certified bound | `2.4605490950e-02` |
| plain CG iterations | `31` |
| packet-preconditioned CG iterations | `6` |
| normalized coupling eta | `2.9428948474e-02` |
| preconditioned condition bound | `1.0606425432` |

## Measured corpus audit

- Rows: 154
- CPU rows: 74
- GPU rows: 80
- Failed or skipped rows: 0
- Suites: 16
- Maximum recorded relative error: `2.8789524512e-03`
- Fairness-group violations: 0
- Recorded GPU: NVIDIA GeForce RTX 3070 Ti Laptop GPU
- Compute capability: 8.6
- Recorded GPU measurements were not rerun during this PDF build.

## Sanitization

The packaged benchmark JSON was scanned to ensure that it contains no:

- prior personal identifiers;
- local user-directory paths;
- `filepath` fields;
- raw `timestamp_utc` fields;
- process-list output.

The paper source, Python source, JSON, CSV, Markdown, and PowerShell files were also scanned for prior personal identifiers and conversational drafting remnants.

## Wheel

- Wheel: `projector_packet_algorithms-1.0.0-py3-none-any.whl`
- Build method: PEP 517 wheel build without dependency isolation
- Clean target installation: passed
- Import test: passed
- Model check after installation: `ideal_bdlr_speedup(8192,64,8) == 102.4`

## Render audit

All 26 pages were rendered at 160 DPI. `Verification_Render.png` contains a complete page contact sheet. `Figure_Contact_Sheet.png` contains all 18 figures.

## Archive verification

- Complete release archive extraction: passed
- Complete release tests after extraction: `23 passed`
- Source-focused archive extraction: passed
- Source-focused tests after extraction: `23 passed`
- Source-focused LaTeX recompilation: 26 pages, with no undefined references or box warnings
- Deterministic archive timestamps: normalized

## Claim control

The paper separates:

- theorems and exact finite identities;
- modeled arithmetic and storage counts;
- hardware-specific measured rows;
- negative controls;
- hardware and compiler conjectures.

No claim of a new generic matrix-multiplication exponent is made.
