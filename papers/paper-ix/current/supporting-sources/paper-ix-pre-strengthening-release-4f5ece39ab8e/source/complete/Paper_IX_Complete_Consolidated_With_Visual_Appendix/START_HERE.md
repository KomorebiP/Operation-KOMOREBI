# Paper IX — complete recovered source and visual reader edition

**Arithmetic Packets, Dyadic Towers, and Local Polynomial Deformation**  
Komorebi P. · Consolidated manuscript of 8 September 2026  
Visual reader package produced 12 September 2026

## Read

- `reading_editions/Paper_IX_With_Visual_Appendix.pdf`: the unchanged 48-page consolidated manuscript followed by the 30-page visual appendix, 78 pages in total.
- `reading_editions/Paper_IX_Visual_Appendix.pdf`: the appendix on its own.
- `reading_editions/Paper_IX_Consolidated.pdf`: the original selected manuscript.

The appendix has 28 editable vector plates and 30 guided concept pages. Its gray source lines link back to the appropriate original pages in the combined edition. There are exact running examples of normalization loss, least dyadic periods, isometric residue permutations, sharp Euler truncations, correction fibers, dead lifting branches, prescribed parameters, controlled inverse weights, and the distinction between completion and global descent.

## What is preserved

`original_snapshot/` contains all 2,278 files from the selected proofread handoff, unchanged. Its current LaTeX is under `manuscript/consolidated/`, including seven section files. Its saved proof sources, contracts, theorem maps, negative controls, dependency pins, and logs remain in their original layout. There are 633 loose `.lean` files across current and historical snapshots, plus the preserved baseline ZIP. These are not 633 independent current modules or a unique theorem count.

The consolidation maps 62 manuscript statements to 202 declaration references. Fresh index replay reproduces those exact saved map files. Checking source/name correspondence is not a new proof of manuscript-to-formal-statement equivalence.

**Recovery boundary:** the complete original older 28-page manuscript's TeX, original figure generator, and historical numerical experiment package were not recovered with the consolidated source. They are not manufactured here. The current consolidated manuscript's editable LaTeX and the recovered arithmetic/polynomial scripts are included in full.

## New appendix sources

- `visual_appendix/appendix.tex`: A4 layout, typography, macros, navigation.
- `visual_appendix/source/pages.tex`: all exposition, formulas, captions, and source references.
- `visual_appendix/source/models.py`: exact rational and finite modular models.
- `visual_appendix/source/generate_graphics.py` and `drawing.py`: deterministic editable TikZ generation.
- `visual_appendix/graphics/`: 28 vector plates and their index.
- `visual_appendix/checks/verify_examples.py`: 214 positive assertions and 19 rejected false controls, with 30,987 recorded positive case evaluations across the bounded sweeps.
- `visual_appendix/build.py`: isolated example/graphics/TeX build, PDF assembly, source links, and page-preservation checks.

## Reproduce

From this directory, using Python 3.10 or newer:

```powershell
python Run-PaperIX.py verify
python Run-PaperIX.py examples
python Run-PaperIX.py appendix
python Run-PaperIX.py original
```

`verify` needs only Python's standard library. `examples` needs SymPy. The appendix build also needs PyMuPDF, pypdf, and an installed `pdflatex` with the packages listed in `visual_appendix/README.md`. `original` runs the selected recovered exact scripts, reconciles the saved proof evidence and statement map, and rebuilds the consolidated LaTeX. Use `--skip-tex` with `original` for the non-TeX part. Use `--output-dir` for a new destination; existing sources and evidence trees are protected.

Builds use temporary working copies. Output defaults to `rebuilt/`. The saved baseline and older proof records are not modified. No tool downloads anything.

## Evidence in this edition

`editorial_evidence/appendix_build/` records the new exact checks, successful TeX passes, and preservation of all 78 input pages. `editorial_evidence/original_replay/` records the recovered polynomial-obstruction, Mahler-kernel, and dyadic-displacement checks, the evidence index, the exact statement-map replay, and the original manuscript rebuild. `PROVENANCE.json`, `PRESERVATION.json`, `MANIFEST.json`, and `SHA256SUMS.txt` record the selected input and output identities.

The original TeX rebuild retains one underfull-box warning; its 48 pages match the preserved PDF in extracted text and 72-dpi rendered appearance. The new appendix has no overfull, underfull, missing-glyph, or unresolved-reference warnings. Draft issues and their fixes are recorded in `DEVELOPMENT_NOTES.md`.

## Formal and software boundary

**No Lean compilation was performed for this editorial package.** The selected archive's earlier proof statuses and all open questions remain unchanged. The evidence replay checks hashes and recorded axiom sets; it does not rerun the kernel or reauthenticate the external Nishibuchi paper. Four legacy logs lack prior hashes and remain fingerprints only.

The Lean compiler, Mathlib cache, TeX distribution, font files, and installed Python dependencies are not bundled. The original pinned Linux/WSL-oriented Lean reproduction commands remain in the preserved README. Packaging and finite Python checks do not constitute a new universal theorem or a fresh all-paper census.
