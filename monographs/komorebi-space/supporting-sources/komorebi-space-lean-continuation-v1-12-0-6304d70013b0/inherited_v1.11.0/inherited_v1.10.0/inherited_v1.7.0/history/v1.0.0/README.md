# Komorebi Space — monograph edition 1.0.0

**Komorebi P. · Operation Komorebi · 10 October 2026**

## Reader set

| Document | Pages | Role |
|---|---:|---|
| `publication/Komorebi_Space_Monograph.pdf` | 48 | The mathematical exposition, proofs, examples, source concordance, and references. |
| `publication/Komorebi_Space_Visual_Guide.pdf` | 17 | Fourteen reproducible visual plates with their mathematical interpretation and scope. |
| `publication/Komorebi_Space_Lean_Guide.pdf` | 20 | Exact declaration correspondence, source lineage, historical verification, and reproduction instructions. |

The monograph has four parts and seventeen numbered sections. It develops coherent views, extension obstructions, protected correction, split tower repair, multiscale reconstruction, nonabelian cocycles, effective descent, the composition-site stack, equivalent presentations, graph holonomy, closed-range stability, quantitative descent, and moving exact spaces.

Version **1.0.0 is the publication version**. It is not the version of a newly integrated Lean library and does not designate completion of every proposed universal or higher-categorical extension.

## Evidence at a glance

- 54 stable principal exposition identifiers, KS01–KS54.
- 53 source-aligned items containing 112 declaration references. References can repeat and are not counts of discoveries. KS54 is an explicitly identified written example.
- 123 foundation source files including the root and 12 focused source files including the root match their frozen archives and historical replay hashes.
- 14,224 fresh assertions in the independent exact-example checker, plus 2,767 assertions in a fresh run of the recovered focused finite checker.
- All three PDFs passed mechanical preflight and rendered visual review. No final overfull-box, undefined-reference, missing-glyph replacement, or unembedded-font issue was found.

**A fresh Lean build was not run.** No Lean executable was available in the working environment, and the pinned external runtime was not restored. Historical successful compiler and axiom records are included under their original dates and scope. They are not presented as a current execution.

## Source layout

`source/` contains the editable LaTeX monograph, companion guides, shared publication style, and fourteen TikZ/vector figure sources. `data/claim_ledger.json` records the declaration names, source paths, starting lines, hashes, and correspondence notes. `checks/` contains the publication's executable checks. `audit/` records their outputs and the review history.

`evidence/archives/` preserves four original ZIP archives unchanged: the foundation v0.20.0 source and replay evidence, and the focused moving-space v0.32.0 source and replay evidence. `evidence/foundations_v020/` and `evidence/moving_v032/` expose their production sources and selected supporting material for reading. Extract the original archives for a complete historical project, including all original audit files.

`evidence/selected/HilbertHolonomyRepair.lean` is an additional recovered source. Its complete build closure is not certified by this publication. Its role in the infinite-dimensional holonomy discussion is marked separately.

## Reproduce the publication

Run `bash build.sh` from this directory. Python 3, PyMuPDF, a TeX Live installation with the packages declared in `source/preamble.tex`, and Poppler's `pdffonts` are required. The build script performs current integrity and finite checks, regenerates the source catalogue, compiles the three PDFs, runs mechanical preflight, and regenerates the payload hash manifest.

This is a **publication build**, not a Lean toolchain installer. The Lean companion and the original project READMEs explain separate replay of the two frozen projects with the pinned external runtime.

## Scope and notices

The mathematics is relative to declared views, coefficients, covers, preservation maps, and analytic hypotheses. The paper does not establish a unique ambient object containing all mathematics, unrestricted arithmetic realization, or a complete infinity-stack theory. One dependent-index dyadic proof is explicitly an outline; its full formal declaration is identified in the source concordance.

Original source notices and historical documents are retained. Their old scope statements are not automatically current: the later standard stack theorem supersedes the early outline's treatment of stackhood as a target. Original archives have not been rewritten to erase that history.
