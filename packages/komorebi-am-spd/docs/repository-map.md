# Repository map

## Installable code

| Module | Role |
|---|---|
| `src/am_spd/atlas.py` | Moving packet grammar, packet reconstruction, image metrics, and classical baselines |
| `src/am_spd/singular.py` | Packet-span SVD, global SVD, and local singular packet completion |
| `src/am_spd/multiscale.py` | Local models, Lagrange tree selection, orthogonal completion, and adaptive blocks |
| `src/am_spd/exact.py` | Independent exact finite Pareto recursion used by verification |
| `src/am_spd/final.py` | Exact-budget tree result and backward replacement portfolio |
| `src/am_spd/api.py` | High-level reconstruction configuration and result API |
| `src/am_spd/components.py` | Public component-level stage APIs, pixel closure, and baselines |
| `src/am_spd/model.py` | Checksummed `.amspd` model format, inspection, and decoding |
| `src/am_spd/continuation.py` | Shared reconstruction continuation helpers |
| `src/am_spd/tiling.py` | Tile region construction and blending windows |
| `src/am_spd/tiled.py` | Tiled reconstruction, `.amspdt` archives, and tiled continuation |
| `src/am_spd/tuning.py` | Finite-grid method and budget selection |
| `src/am_spd/batch.py` | Directory processing and configuration-aware restart manifests |
| `src/am_spd/benchmark.py` | Structured built-in benchmark runner |
| `src/am_spd/reference.py` | Exact four-case paper replay and reference comparison |
| `src/am_spd/resources/` | Compact packet histories and benchmark reference ledgers |
| `src/am_spd/io.py` | Image input and output |
| `src/am_spd/cli.py` | `am-spd` command-line interface |
| `src/am_spd/verification.py` | Smoke and full package integration verification |

## Research snapshot

`research/original` is a byte-preserved copy of the recovered final source archive. It retains the original script names, generated tables, figures, results, logs, checksum ledger, release audit, and claim map.

The installable package is derived from the stable algorithmic modules but uses package-relative imports and a public wrapper. The research snapshot is not rewritten to match the package layout.

## Documentation

`docs/paper` contains the final PDF, LaTeX source, KaTeX conversion, source package, and audit.

`docs/model-format.md` specifies schema 2 of the single-image archive and schema 1 of the tiled archive.

`docs/cli.md` documents the complete command-line surface.

`docs/algorithm.md` explains the finite pipeline.

`docs/claim-boundaries.md` separates theorem-level statements, computed evidence, heuristic components, and software-format boundaries.

`docs/reproducibility.md` gives package replay, historical verification, benchmark regeneration, and manuscript build commands.

## Operation-KOMOREBI monorepo integration

`monorepo/.github/workflows` contains root-level workflow templates. Copy them to the root `.github/workflows` directory of `Operation-KOMOREBI`; workflows nested beneath `packages/komorebi-am-spd` are not executed by GitHub.
