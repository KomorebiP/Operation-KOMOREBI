# Continue Special Functions formalization

Current block: **SF-LEAN-B01**. Begin with `formalization/Block01/REPORT.md`, `CLAIM_MAP.json`, `declarations.json`, and `PROGRESS_v0.1.0.json`.

The source is `lean/CoupledFormal.lean`. Its 29 named declarations pass compilation, axiom audit and same-kernel module replay. The unchanged 39-declaration finite projector core also passes. The compact runtime kit is restored from Lean_Compact_01.zip through Lean_Compact_05.zip, with combined SHA-256 f7548038f94ea30789ce28fc2ff769c40e9c37d8879ea133e9bea821056342c7. Do not stop merely because lean or lake is absent from PATH.

Next: connect the proved local absolute convergence to holomorphic germs and verify the termwise derivative/product identities. Then prove extension along radii R/max(q,r,a,b) for strict contractions. The existing results do not yet formalize entire continuation or Perron growth.

Run `tools/verify_coupled_block.py` against the stored kit and a fresh external work directory. Review receipts from every stage. Preserve this ledger and add a new immutable ledger for the next block. Do not overwrite evidence with a stronger status than the actual declaration map supports.
