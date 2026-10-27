# Collatz visual guide

This is the separate visual companion to `../collatz/`, with 24 landscape educational spreads plus a cover. It introduces the maps, clocks, valuations, ordered affine offsets, exact cylinders, uniform progression certificates, common-height counting argument, and remaining quantified obligations.

Regenerate the figures with:

```bash
python conjecture_set/collatz_visual/figures.py
```

Build the guide from the bundle root with:

```bash
python conjecture_set/build.py --only collatz_visual
```

`data.json` preserves every claim-supporting plotted integer and rational value, plus the figure reading notes. `COMPUTATION_REPORT.json` records software versions, exact finite ranges, checks, runtime and SHA-256 hashes. `FIGURE_LAYOUT_CHECK.json` records the drawn-text canvas check. `PROOFREADING.md` describes mathematical and visual review, including resolved authoring failures.

All mathematical proofs and project evidence citations belong to the current companion Collatz monograph and its `SOURCES.md` and `evidence/` directory. This visual guide uses those formulas without asserting new universal results. The saved historical residue count was not replayed. No fresh Lean replay is claimed.
