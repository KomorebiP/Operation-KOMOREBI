# Verification Notes

## Projector-Resolved Seed Calculus IX
### Arithmetic Packet Calculus: Euler Families, Supercongruences, and Weighted p-adic Reconstruction

**Author:** Komorebi P.

## Build

- Final PDF: `Projector_Resolved_Seed_Calculus_IX.pdf`
- Final page count: 29
- LaTeX engine: `latexmk` with `pdflatex`
- Undefined references: none
- Overfull boxes: none
- Underfull boxes: none reported
- Paper-local citations: none
- Paper-local bibliography: none
- Figures: 16 PNG and 16 vector-PDF files
- PNG ancillary metadata: removed
- Vector-PDF metadata: title and **Komorebi P.** only
- Main PDF metadata: title, subject, and **Komorebi P.** only
- Hyperlinks retained after metadata normalization: 54

## Automated tests

```text
29 passed
```

The test suite verifies:

- residue packet reconstruction and nested refinement;
- congruential Euler triangular coefficients;
- exact odd-prime Euler reconstruction;
- odd-prime tail valuations;
- exact weighted dyadic Euler reconstruction;
- dyadic tail valuations and rational 2-adic integrality;
- Mahler coefficients and finite-difference reconstruction;
- Lucas standard-window reduction;
- reduced inverse independence in the tested standard windows;
- odd-prime and dyadic unit decompositions;
- CRT packet addresses and reconstruction;
- companion and Fibonacci packet recurrences;
- generation of all figures and machine-readable results.

## Finite certificates

| Certificate | Result |
|---|---:|
| packet reconstruction residual | `0` |
| odd-prime supercongruence checks | `180`, all passed |
| minimum odd-prime valuation margin | `0` |
| weighted dyadic checks | `111`, all passed |
| minimum dyadic valuation margin | `1` |
| standard-window parameter cases | `30` |
| Mahler reconstruction residual | `0` |
| CRT checks | `192`, all passed |
| Fibonacci packet recurrence residual | `0` |

The zero odd-prime margin means that some examples attain the proved lower bound exactly. The positive dyadic margin means every nonzero tested dyadic tail exceeded the uniform bound by at least one additional 2-adic unit.

## Wheel

- Wheel: `projector_seed_arithmetic-1.0.0-py3-none-any.whl`
- Build method: PEP 517 wheel build without dependency isolation
- Clean target installation: passed
- Import test: passed
- Installed model checks: `E_8 = 1385` and CRT address `(17 mod 8, 17 mod 3) = (1,2)`

## Render audit

All 29 pages were rendered at 160 DPI. `Verification_Render.png` contains the complete page contact sheet. `Figure_Contact_Sheet.png` contains all 16 generated figures. The rendered pages were checked for clipped text, overlaps, missing glyphs, and broken tables.

## Metadata audit

The compiled PDF was rewritten only to replace its document-information dictionary. A render comparison before and after metadata normalization reported zero changed pages. Creator, producer, date, custom metadata, and XMP metadata are absent from the final PDF.

## Claim control

The paper distinguishes:

- proved exact identities and congruence theorems;
- finite numerical certificates;
- classical inputs;
- conjectural uniform extensions;
- historical and priority questions reserved for external review.

The uniform odd-prime and weighted dyadic sectors are not conflated. The dyadic formulas, weights, integrality arguments, and unit coordinates are developed separately.

## Archive verification

- Complete release archive extraction: passed
- Complete release tests after extraction: `29 passed`
- Source-focused archive extraction: passed
- Source-focused tests after extraction: `29 passed`
- Source-focused LaTeX recompilation: 29 pages
- Undefined references after source recompilation: none
- Overfull and underfull boxes after source recompilation: none
- Deterministic archive timestamps: normalized to the ZIP epoch
