# Sources and provenance

## User-provided research

The sole predecessor of this branch is the preserved v0.1 archive in `history/`.
Its source and 22,758-check deterministic audit were replayed. This release does
not reauthenticate every historical p-adic proof or inventory in the conversation.

The exact chain-ring Smith discovery routine was adapted from the saved Block03
code carried by the Block15 archive. See `source_records/SMITH_LINEAGE.md`. The
new certificate checker does not import that code or the discoverer.

## Toolchain

The saved compact Lean payload SHA256 is
`f7548038f94ea30789ce28fc2ff769c40e9c37d8879ea133e9bea821056342c7`.
The tested core version and key dependency hashes are recorded in
`evidence/ENVIRONMENT_VERIFIED.json`. Only Std is imported.

Official Lean documentation inspected:
https://lean-lang.org/theorem_proving_in_lean4/Axioms-and-Computation/
The quotient construction, classical-choice computational boundary and axiom
inspection are standard Lean facilities. Their use is not a project novelty.

## Bounded external context, NOT a novelty verdict

Quentin Aristote, Sam van Gool, Daniela Petrisan, Mahsa Shirmohammadi,
"Learning Weighted Automata over Number Rings, Concretely and Categorically",
arXiv:2504.16596v1, 23 April 2025; LICS 2025 DOI
10.1109/LICS65433.2025.00038.
https://arxiv.org/abs/2504.16596

The primary metadata and abstract were checked. The work addresses number rings
and active weighted-automata learning. Those are not identical hypotheses to the
complete finite chain-ring systems here. No technical theorem from that paper is
used as an unverified proof leaf, and no claim of being first is made. This was a
limited contextual check, not a full literature or priority audit. Early broad
web searches returned poor matches; unrelated results were not used as evidence.
