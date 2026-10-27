# v0.13.0 verification

Current clean cumulative build: PASS. All 83 modules and the root compiled from source. All 880 indexed named theorems and all 455 indexed constructions were audited. Only propext, Classical.choice and Quot.sound occurred. Three Lean negative controls pass.

All 78 v0.12 proof-module sources are unchanged. Five new modules contain 35 named theorems and 41 indexed constructions. Counts are not novelty claims.

The final delivery receipt and separate replay evidence report the fresh extraction build. They are outside this immutable source archive so that the archive replayed is the exact archive delivered.

The compiler/kernel and imported cached dependencies remain trusted and were not independently rebuilt. Source indexing is project-specific, not an independent Lean parser.

Three failed draft compiles were corrected: unused-section-variable and instance-style lints, and missing decidability for concrete finite-patch membership. None is counted as verification. Offline runtime restoration succeeded. An unused artifact RPC process was stopped to relieve memory pressure without interrupting Lean.
