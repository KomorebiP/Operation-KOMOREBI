# Euler Congruences — final strengthened paper package

Komorebi P. · 6 October 2026

Read the three companions in `output/pdf/`:

- `Paper_IX_Euler_Main_Final.pdf`: the complete mathematical paper, with Nishibuchi's original statement, its full completion, new threshold-free prime-power and mixed-step arguments, four-address factorial precision, exact higher-order families, sharp periods and Taylor radii. The entire preceding Paper IX development and its historical appendices are retained. A separate appendix gives the exact boundary of ordinary Euler tail simplicity.
- `Paper_IX_Euler_Visual_Guide_Final.pdf`: indexing, precision, least periods, exact residue permutations, sharpness, analytic slopes, and counterexamples through exact figures.
- `Paper_IX_Euler_Lean_Guide_Final.pdf`: the formal constructions, exact source excerpts, declaration catalog, current coverage map, and the remaining formalization targets.

The original Nishibuchi conjecture is solved throughout its stated parameter range. The universal simplicity conjecture for the separate ordinary-Euler tail program, native presentation invariance, and native global gluing remain open. Several higher-difference classifications remain open as stated in the paper.

## Formal verification boundary

Inherited Lean releases cover Nishibuchi Conjecture 3.9, the four-address all-row common-step bound, exact first differences, least periods, isometry, and the stated lifting/deformation results. The new general prime-power, mixed-step, factorial, sharp higher-order, and analytic-radius proof routes are written proofs with internal audits and bounded exact computation. They have no new Lean kernel acceptance in this edition. A static source/log review was rerun; Lean and Lake executables were unavailable. Compiler evidence in the preserved packages is historical and tied to its own exact sources.

The 1,000-name completion inventory and the 1,876-row broader source/version catalog are different overlapping inventories, not counts of independent discoveries. The guides keep this distinction.

## Rebuild and inspect

With an existing TeX installation, Python, the required fonts, and PyMuPDF:

```bash
python3 rebuild_pdfs.py
```

This compiles the main paper and visual guide with PDFLaTeX and the Lean guide with XeLaTeX. The manifest identifies the shipped bytes; a different TeX environment or metadata run can change fresh PDF bytes without changing the mathematical source. It uses the supplied vector figures. It does not install dependencies, replay Lean, or regenerate the historical research runs. For a fresh exact visual experiment, run:

```bash
python3 sources/generate_figures.py
```

That produces a new dated figure manifest. For static formal-source reconciliation, follow the command in the opening chapter of the Lean guide. Kernel reproduction needs the separately pinned Lean 4.34.0-rc2/Mathlib kit described there. The final release manifest checks hashes, not mathematical truth or authorship.

## Preserved evidence

`preserved/threshold_free/` contains the frozen strengthening proofs, six principal audits, separate exact experiment manifests and outputs, and the statement/source checks. `preserved/PRSC_IX_Consolidated_Manuscript/` contains unchanged formal source frontiers and recorded verification evidence. `preserved/Paper_IX_Pre_Strengthening_Release.zip` retains the complete previous three-part publication byte for byte. `preserved/Euler_Complete_Work_2026-10-05.zip` retains the associated root/tail program and its open boundaries. Current review and rendering evidence is under `evidence/`.

Historical mathematical and build statements are dated checkpoint records. The opening current-scope map and current theorem statements govern this strengthened edition. Retained historical crosswalks explicitly refer to the preceding main-paper pagination. No external peer review, journal acceptance, DOI, or global priority claim is made.

The mathematical delta audit uses portable proof-source locators under `preserved/threshold_free/`. For any older recorded workspace locator, map `../euler_threshold_free_2026_10_06/` to `preserved/threshold_free/`. `python3 verify_release.py` checks that all eleven current reviewed files and the remapped underlying proof sources still have their audited hashes, as well as the package file manifest.
