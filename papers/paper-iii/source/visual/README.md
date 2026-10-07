# Paper III visual appendix

A 24-page reader's companion to the proofread finite-algebraic v1.0.1 release. All 22 plates are deterministic TikZ generated from explicit mathematical models. Values are integers/rationals or symbolic polynomials; floating point is used only for display coordinates. No artwork generation, network request, or Lean invocation is part of this build.

## Source layout

- `appendix.tex`: document style, notation, page headings, links.
- `source/pages.tex`: full explanatory text, examples, limitations, and source references.
- `source/models.py`: shared exact matrix, edge, chart, connection, packet, and tree data.
- `source/generate_graphics.py`: writes 22 editable `graphics/*.tex` plates.
- `checks/verify_examples.py`: 124 exact checks plus four false controls that must be rejected.
- `checks/EXACT_CHECKS.json`: recorded named results, tested ranges, and source hashes.
- `build.py`: isolated TeX build and PDF assembly; no mutation of original manuscript or appendix sources.

## Build

```bash
python build.py --output-dir ../rebuilt_reader
```

Requires the Python packages pinned in `requirements.txt` and a `pdflatex` installation providing geometry, fontenc, lmodern, microtype, amsmath, amssymb, mathtools, graphicx, array, booktabs, tabularx, multicol, xcolor, TikZ/PGF, tcolorbox, fancyhdr, hyperref, and bookmark. Normal TeX font packages are prerequisites, not copied into this archive as font files.

The builder expects 27 original pages and 24 appendix pages. It runs the exact checks and graphic generator, compares regenerated plate hashes to the shipped files, rejects unresolved references and box warnings, and checks all 51 assembled pages against their inputs. Source-line links are added only to the combined PDF. The appendix is not compiled as part of the original theorem document, so original numbering and proof pages cannot shift.

## Content map

| Pages | Topic |
|---|---|
| V–1–2 | Three distinct structures; typed object atlas. |
| V–3–8 | Edge orientation, noncommuting coefficients, word sums, cancellation, reachability, rectangular products. |
| V–9–12 | Exact frames, nonlinear chart conjugation, minimal versus reversible connection hypotheses, scalar loop defects. |
| V–13–18 | Shear holonomy, gauge size, flat versus calibrated data, complete obstruction blocks, oblique packets, mixing gauges. |
| V–19–22 | Candidate-specific certificates, operation-tree locality, chosen nonlinear defects, mixed terms and roadmap scope. |
| V–23–24 | End-to-end matrix diagnosis, formal boundary, and reproducibility. |

Every drawn table is tied to the displayed data. Word enumeration is bounded to the named finite graph and lengths; it is not a substitute for the general Lean theorem. Symbolic polynomial checks establish the displayed identities, not a general nonlinear chain rule. The real plots are exact formulas sampled for rendering, not numerical proof evidence.
