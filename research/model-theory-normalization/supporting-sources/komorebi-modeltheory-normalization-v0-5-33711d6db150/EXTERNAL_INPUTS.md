# External inputs — v0.5

No new external classification theorem is assumed. New proofs use the unchanged
v0.4 `DiscoveryTrace` interface and its dependencies. The main algebraic inputs are
finite linear-combination characterizations of a submodule span, linearity of a
dot-product functional, and the preceding finite-prime-power queue rank theorem.

The source checkpoint is the immutable v0.4 ZIP with SHA-256
`fca8f85dbf1cff576e4461fc8a1f68e9933770c65c95b8b747ba9338d967243b`.
The compiler and Mathlib pins are checked in `v05_evidence/ENVIRONMENT.json`.
The compiled upstream cache is reused; no claim is made of rebuilding Mathlib.

Public documentation consulted September 21, 2026:

- https://leanprover-community.github.io/mathlib4_docs/Mathlib/LinearAlgebra/Finsupp/LinearCombination.html
  Documents `Submodule.mem_span_range_iff_exists_fun`, the standard finite span
  characterization behind the inherited positive-witness lemma.
- https://raw.githubusercontent.com/leanprover/lean4/6a10ac8c22beadecabdbb0919c2b50214762f91d/src/Lean/Environment.lean
  Consulted to diagnose the runtime's missing split module-data/IR files. It is not
  an external mathematical theorem used by the new result.

Soundness is established against the pinned imported declarations by actual local
compilation, not by a current documentation page. The numerical table and examples
are original current-run computations. No historical priority judgment is claimed.
