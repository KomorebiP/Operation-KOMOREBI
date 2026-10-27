# Paper XI visual guide

This standalone companion explains the original finite tame and wild packet route and the actual arithmetic constructions in Blocks 166–167. The general arithmetic packet realization endpoint is Conjecture 66. The local-factor comparison is conditional on an actual compatible candidate and H5 for that same candidate.

The release includes the detailed Markdown (.md) proofs, construction notes, audit records, and remaining research obligations.

## Files

- `Paper_XI_Visual_Guide_Final.pdf`: standalone reader edition.
- `Paper_XI_Visual_Guide_Final.tex`: editable mathematical source.
- `generate_figures.py`: deterministic exact Python/Matplotlib vector artwork.
- `figures/`: 23 vector PDFs and the exact formula-derived figure data.
- `build.py`: portable builder accepting a fresh output directory.

## Rebuild

Requirements are Python with Matplotlib and pdfLaTeX with the ordinary packages named in the source. From this folder, run:

```sh
python build.py --output-dir /absolute/path/to/output
```

The build pins its date epoch to 1791244800, omits variable PDF dates, fixes its trailer identifier, regenerates figures, and compiles the guide in the chosen directory. An isolated copied-source rebuild produced an identical final PDF.

## Source and evidence

Each lesson records its original manuscript section or retained arithmetic proof anchor. The arithmetic arguments remain ordinary proofs using their stated classical type-theory dependencies. Matrix and figure computations are bounded checks; they do not prove universal realization or supply new Lean certificates. Consult the separate traditional paper, Lean guide, release scope record, and supplementary index for the full theorem/proof crosswalk.
