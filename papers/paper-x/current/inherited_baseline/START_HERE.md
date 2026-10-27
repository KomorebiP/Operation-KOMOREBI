# Paper X — complete recovered sources with a visual appendix

**Author:** Komorebi P.  
**Editorial edition:** 12 September 2026.  
**Current formal status:** 17 checked / 3 partial (9.1, 9.2, 11.1).

“Complete” in this bundle's filename means the recovered source-and-evidence package,
not completion of the three partial manuscript claims.

## Read

- `reading_editions/Paper_X_With_Visual_Appendix.pdf`: 80 pages.
- `reading_editions/Paper_X_Visual_Appendix.pdf`: 30 explanatory pages.
- `reading_editions/Paper_X_Amended_Manuscript.pdf`: 50-page inherited amended text.

The Block 27 release contained amended LaTeX without its compiled PDF or figure assets.
The original figure assets and numerical companion were recovered from the original
Paper X release. This edition typesets that inherited amended text without changing it.
The later arithmetic continuation has its own source notes and proof records, not a new
full manuscript; its scope is explained on the appendix's first and last pages and in
`current_continuation/CURRENT_STATUS.md`.

## Directory map

| Directory | Contents |
|---|---|
| `current_continuation/` | Latest recovered Scalar/Mellin + Arithmetic Separator source overlay, 271 cumulative PaperX Lean source modules, 16 new saved objects, latest status and evidence. |
| `original_releases/residue_counting/` | Preserved predecessor release, 255 source/object pairs and its own replay tools. |
| `original_releases/block27/` | Preserved full Block 27 source/history, amended LaTeX, earlier theorem ledgers, and nested baseline archive. |
| `original_companion/` | Original manuscript/PDF, finite Python package, 28 tests, 16 figure pairs, result records, and historical source map. |
| `manuscript/` | Convenience copy of the inherited amended LaTeX plus recovered figures, ready for an isolated rebuild. |
| `visual_appendix/` | Editable LaTeX, 28 TikZ vector plates, exact mathematical models, checks, and PDF assembly code. |
| `editorial_evidence/` | Fresh example/build/packaging evidence, unchanged-input hashes, and development corrections. |
| `tools/` | Isolated original-code replay, manuscript rebuild, and saved-evidence correspondence checks. |

Current status files supersede earlier scope summaries. Historical sources are not
independent current modules and must not be added together as a theorem census.

## Verify and rebuild

From this extracted folder, with Python available:

```powershell
python Run-PaperX.py verify
python Run-PaperX.py examples --output-dir .\new_example_check
python Run-PaperX.py appendix --output-dir .\new_appendix_build
python Run-PaperX.py original --output-dir .\new_original_replay
python Run-PaperX.py manuscript --output-dir .\new_manuscript_build
python Run-PaperX.py saved-evidence
```

Output directories must be new or empty. `verify` requires only Python's standard library.
The example and PDF commands need the tested packages in `requirements.txt`; PDF builds
also need a working `pdflatex` installation with the packages used in the supplied preamble.
The scripts neither install dependencies nor access a network. Original files are never
used as a writable working directory by these new launchers.

## Lean is preserved, not freshly certified here

No new Lean run was performed for this editorial edition. The saved records refer to
Lean 4.34.0-rc2 / Mathlib `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.
The portable compiler, Mathlib cache, TeX distribution, and installed Python packages
are not included.

The latest continuation is a source overlay. Its inherited `README.md` and
`checks/replay_residues.py` describe the older residue-counting layout, not a standalone
271-module replay. Read `README_CLAIM91_CONTINUATION.md` and the corresponding verification
JSON for the latest 16-module scope. The intact predecessor replay is in
`original_releases/residue_counting`; use a disposable copy and the pinned kit to run it.
`Run-PaperX.py saved-evidence` reconciles the 255 predecessor pairs and 16 latest pairs
without claiming compiler verification.

General Frobenius occurrence, remaining attachment/transport comparisons, universal
companions and universal automorphic occupancy are not established by this appendix.
