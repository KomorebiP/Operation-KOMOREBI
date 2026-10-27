# Worked visual appendix

The 26 concept pages add a reader layer to Paper V v1.1.0. Twenty-four vector plates are generated as editable TikZ. No image-generation model, stock image, screenshot, or external graphic is used for the new plates.

## Build structure

- `appendix.tex`: document style and typesetting entry point.
- `source/pages.tex`: explanations, worked formulas, and manuscript references.
- `source/models.py`: rational/algebraic finite models.
- `source/generate_graphics.py`: deterministic TikZ generator; float coordinates are used for display.
- `graphics/`: the generated TikZ files and plate index.
- `checks/verify_examples.py`: exact example checks and intentionally false controls.
- `checks/EXACT_CHECKS.json`: recorded successful run.
- `build.py`: copies sources to an isolated directory, runs tests, regenerates plates, compiles twice, assembles PDFs, adds links, and audits preservation.

From the bundle root run `python Run-PaperV.py build`. The build leaves the original manuscript and all sources unchanged. Its output includes the reading PDFs, exact-check record, detailed build audit, and compiler logs.

## Page sequence

1. Three worked structures
2. Object atlas
3–7. Signed polyphase addresses, refinement, FIR transfer, delay units, and perfect reconstruction
8–11. Haar alignment, lifting geometry, two-level packets, and exact coefficient tails
12–14. Covering antichains, exhaustive finite optimization, and perturbation margins
15–19. Known edges, Fourier pulse reconstruction, mask and amplitude error, and identification limits
20–21. Cauchy versus pointwise products, and nonlinear neighbor indexing
22–25. Cayley orbit, projective poles, CRT phase labels, and finite sensitivity
26. Evidence guide and unchanged formal boundary

The appendix uses a 16-sample signal and a 26-pruning tree, not the larger manuscript benchmarks. It does not prove universal edge recovery, noise-free identification from ambiguous observations, infinite-tree consistency, or optimal Smith sampling.
