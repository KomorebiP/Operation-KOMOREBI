# Paper XI — synchronized publication checkpoint

**Publication Block 06 · version 0.6.0 · 10 October 2026**

This package synchronizes the original Paper XI reader trio with the separate Conjecture 66 progress paper and its visual atlas. It is a reviewed synchronization checkpoint, not a claim to have proved Conjecture 66 or performed a new Lean compilation. The final five-reader release audit is the next task.

## Read the five documents together

All five PDFs are under `publication/pdfs`. Keep their delivered filenames and place them in the same directory. Relative companion links require a PDF reader that supports opening a local linked PDF. Some browser and mobile viewers restrict that operation. Printed section references remain available.

| Document | Pages | Status in this checkpoint |
|---|---:|---|
| `Paper_XI_Traditional_Synchronized_v0.6.0.pdf` | 109 | Revised and rebuilt original monograph |
| `Paper_XI_Visual_Guide_Synchronized_v0.6.0.pdf` | 53 | Revised and rebuilt core visual guide |
| `Paper_XI_Lean_Guide_Synchronized_v0.6.0.pdf` | 235 | Revised and rebuilt Lean/evidence guide |
| `Paper_XI_Conjecture66_Progress_v0.4.0.pdf` | 77 | Preserved unchanged research paper |
| `Paper_XI_Conjecture66_Visual_Atlas_v0.5.0.pdf` | 36 | Preserved unchanged research atlas |

The set has 510 PDF pages. This count includes the large formal-source catalogue and does not count independent theorems or new discoveries.

## What changed

The three originals have consistent research routes and evidence notes. The Lean guide's historical 66-obligation table now links to the current monograph. The table-of-contents layout and build dependencies were repaired. Appendix D restores the factor `[k:F_p](n-n/p)` from the unchanged raw construction note after a Markdown conversion had mistaken it for a hyperlink. See `evidence/block06/SOURCE_CHANGES.md` and the exact patch.

The 68 explicit main proof bodies and all 105 main statement-environment bodies are preserved. Fourteen of fifteen construction appendix files are unchanged, and the fifteenth contains the single documented formula repair. All 423 selected Lean sources, all 40 teaching excerpts, and the inherited catalogue of 4,342 named lexical declarations are retained. These are source-preservation checks, not a new compiler acceptance record.

## Reproduce and inspect

Start with `BUILD.md`. From the package root:

```text
python tools/verify_package.py
python tools/replay_block06.py --output ../paper_xi_b06_replay
python tools/build_readers.py --output ../paper_xi_b06_build
```

All build, replay and rendering outputs must stay outside this checkpoint. No font binaries are included. The builder discovers locally installed URW fonts, or accepts an explicit installed font directory. The package does not download dependencies or run shell escapes.

## Continuity and provenance

`PROGRESS_LEDGER.md` and `.json` retain 23 stable task IDs and all earlier history. `CONTINUE_HERE.md` specifies the next release audit. `predecessor/block05` is the unchanged complete Block 05 compact checkpoint, including its selected earlier sources and staged original reader baseline. The full recovered-source ZIP additionally carries the unchanged complete Block 01 archive under `historical/`. Neither packaging form supplies the missing complete editable Block 02 archive.

Current reports are under `verification/block06`. Reports inside preserved predecessor directories or inside the original reader source folders retain their historical meaning. Their older page counts and dates are not claims about this new build.

## Boundaries

General arithmetic realization, same-candidate H5, corrected-character occurrence in the fixed candidate, and the independently prescribed native-marking certificate remain separate open tasks. The transported-marking positive contract is not silently strengthened by the latter task. No new Lean/Lake build, matrix-constructor replay, external peer review, or fresh classical-source audit is claimed.
