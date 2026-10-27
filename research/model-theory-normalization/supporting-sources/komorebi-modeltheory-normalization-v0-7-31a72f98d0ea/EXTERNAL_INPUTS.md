# External mathematical and formal inputs — v0.6

The computational replacement uses standard integer-lattice and Bezout methods.
It does not claim historical novelty for these ideas. The exact theorem statements
are the attached Lean sources, not an inference from a document title.

The pinned environment is Lean 4.34.0-rc2, commit
6a10ac8c22beadecabdbb0919c2b50214762f91d, and Mathlib
`aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. The original runtime pin,
compiler hash and selected source hashes are checked in v06_evidence/ENVIRONMENT.json.

New direct algebraic inputs include Int.gcdA, Int.gcdB, Int.gcd_eq_gcd_ab,
integer gcd divisibility and Euclidean division; the actual ZMod reduction and
finite span infrastructure; submodule joins and singleton-span characterization.
All are existing library definitions/theorems, not supplied project axioms.

Primary documentation consulted (public current documentation is navigational;
the pinned local source is the authority for this build):
- https://leanprover-community.github.io/mathlib4_docs/Mathlib/Data/Int/GCD.html
- https://leanprover-community.github.io/mathlib4_docs/Mathlib/Data/ZMod/Basic.html

The all-word and standard logical consequences reuse the byte-preserved prior
DiscoveryLogic, FiniteCodeCertificate and standard first-order translation sources.
The enough-fuel termination proof is inherited from DiscoveryRank/Termination.
The old finite coefficient-enumeration procedure appears only in equivalence
proofs, not in the new solver's execution path.

Only standard propext, Classical.choice and Quot.sound dependencies are allowed
by the recorded audit. This is not independent external refereeing or verification
that a human's informal intent was correctly encoded in the source matrices.


## v0.7 additions

The exact predecessor is frozen in history/Komorebi_ModelTheory_Normalization_v0.6.zip.
The new basis normalizer uses the pinned integer Euclidean remainder/division laws,
positive-pivot order properties, and the predecessor's proved lattice insertion
and modular-preimage construction. Canonicity is proved in the project rather
than imported as a claimed Smith/Hermite classification theorem. The mathematical
method is standard triangular integer reduction; this release makes no priority
claim for it.

The proof kernel binary, Mathlib metadata revision, and selected pinned upstream
source checks are recorded in v07_evidence/ENVIRONMENT.json and the inherited
v06_evidence/ENVIRONMENT.json. Upstream compiled Mathlib is reused, not rebuilt.

Two audit-only protocol revisions preserved the mathematical source and build
hashes. They reduced unfinished axiom groups and enabled module-mode imports.
Both failed invocation records remain under v07_evidence/protocol_revision/.
