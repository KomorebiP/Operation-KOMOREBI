# Cut-comparison continuation

Start with `RESEARCH_NOTE.md`. Run `python checks/run_all.py` using Python 3.10 or later and the standard library. No network, solver, compiled extension, or Lean installation is required.

The target remains P versus NP. This block does not settle it. It proves a direct comparison identity for arbitrary restored dirty circuits, derives an unrestricted one-sided-immunity Toffoli lower bound, applies it to a uniformly encoded NP-complete family with asymptotic bound `(2-o(1))N`, and proves why low-degree packet counting cannot amplify this to a superpolynomial bound.

`results/` and `logs/` contain reproducible finite evidence. `COMPUTATION_MANIFEST.json` records exact commands and provenance. `ARTIFACT_SEAL.json` records file hashes only, not formal proof acceptance. `predecessor/` preserves the immediately preceding checkpoint, not the entire Komorebi project history.
