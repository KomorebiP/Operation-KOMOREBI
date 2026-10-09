# AM-SPD 0.2.0 release notes

AM-SPD 0.2.0 turns the recovered research implementation into a broader executable toolkit while preserving the original audited source under `research/original`.

## Main additions

- Portable, checksummed `.amspd` decomposition archives
- Dense, sparse exact, thresholded sparse, and approximation-only residual modes
- Raw, bounded, and exact model decoding
- Packet, singular-mode, tree, Pareto-frontier, and portfolio-trial inspection
- Migration from 0.1.x result `.npz` archives
- Public component APIs for packet fitting, singular completion, tree optimization, portfolio selection, and pixel-coordinate closure
- Fourier, DCT, global SVD, adaptive-quadtree, and total-variation baselines
- Structured benchmark output in images, JSON, and CSV
- Exact four-case paper replay from resources bundled in the installed package
- Expanded command-line interface and full package verification
- Root workflow templates for the Operation-KOMOREBI monorepo

## Typical use

```powershell
python -m pip install -e ".[dev,research]"
am-spd decompose input.png image.amspd --preview approximation.png
am-spd inspect image.amspd --packets --trees --trials
am-spd decode image.amspd recovered.npy --mode exact
```

Upgrade an earlier result archive:

```powershell
am-spd convert-archive reconstruction.npz reconstruction.amspd
```

Replay the finalized benchmark:

```powershell
am-spd reproduce-paper --output-dir paper-replay --strict-reference
```

## Verification record

- 25 package tests passed
- Full package verification passed all checks
- Wheel installation and execution passed outside the source checkout
- All four final benchmark cases matched the required reference invariants
- 291 of 291 preserved-source checksums passed
- 16 core groups, 8 SPD groups, and 15 intermediate groups passed
- 11 final groups and all 12,154 final scenarios passed with zero failures

Two historical Lagrange-proxy diagnostics and one tie-equivalent camera seed label differ from the archived intermediate ledger. They are reported explicitly. Final reconstructions, budgets, and required benchmark invariants match.

## Boundary

This remains a research reconstruction toolkit, not an entropy-coded image codec. GPU acceleration, streaming tiles, statistical denoising, automatic hyperparameter selection, signed provenance, and loaded-model continuation remain future work. The repository retains an all-rights-reserved license until the author selects a public-use license.
