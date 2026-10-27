# Sources and external inputs

The authoritative project predecessor is the complete v0.2 archive under history,
whose hash is recorded in FORMAL_NOTE.md and evidence/PREDECESSOR_PRESERVATION.json.
Its source/certificate specifications, discoverer and checker are preserved.

Proof dependencies are Lean/Std from the pinned Lean 4.34.0-rc2 toolchain,
commit 6a10ac8c22beadecabdbb0919c2b50214762f91d. Modular arithmetic is the standard
Fin implementation exposed by Init.GrindInstances.Ring.Fin. Finite list
cardinality and semiring laws are upstream foundations, not new results.
The actual used key file hashes and restoration limits are in
`evidence/ENVIRONMENT_VERIFIED.json`. No Mathlib is imported by this release.

Official Lean documentation consulted for API interpretation:
- https://lean-lang.org/doc/reference/latest/Tactic-Proofs/Tactic-Reference/
- https://lean-lang.org/doc/reference/latest/Basic-Types/Finite-Natural-Numbers/
These changing documentation pages are not theorem dependencies; the compiled
pinned source and proof terms are the dependency evidence.

No systematic literature/priority audit or held-out comparative benchmark was
performed. Neither a compiled proof nor failed web searches establishes novelty.
