# Environment incidents retained for v0.6.0

1. The compact runtime assembly verified all five parts byte-for-byte. A combined assemble-and-extract command reached the execution ceiling during extraction. The Lean binary was present, but the Mathlib package tree was incomplete.
2. Before the offline package cache was fully attached, Lake attempted to obtain a dependency from the network. This was an environment wiring failure. The project was then attached to the exact pinned local package cache.
3. The missing Mathlib cache was restored from the verified compact runtime archive. Existing v0.5 load-bearing modules then compiled strictly.
4. A clean-path batch passed `CrossRadixWidthOperatorBasis`, `CrossRadixCyclotomicClosure`, and `CrossRadixReynoldsDFT`, then reached the command execution ceiling while entering `CrossRadixAffineDecoder`. The incomplete batch was not used as certification. `CrossRadixAffineDecoder`, `CrossRadixReynoldsAverage`, `CrossRadixRankNullity`, and `CrossRadixV06AxiomAudit` were subsequently compiled individually and passed.

Only successful strict module runs are treated as certification evidence.
