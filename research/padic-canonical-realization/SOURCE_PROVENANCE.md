# Source and verification provenance

Authoritative predecessor: the exact Block33 ZIP recorded in PREDECESSOR_ARCHIVE.json.
PREDECESSOR_SOURCE_HASHES.json records all prior mathematical modules. The sole
inherited source edit is one additional root import. New files are ResidualBehavior,
CanonicalLinearRealization, MinimalMaskRealization, FiniteBehaviorComparison and
ResidualMinimalityExamples.

All proof dependencies are imported from the pinned Lean/mathlib/source tree.
The generic residual argument is given explicitly in MATHEMATICS.md and uses
span mapping, quotient observation, and linear equivalence constructors. No
literature theorem about weighted-automaton minimality is assumed as an axiom.
No novelty or priority claim is made.

The official mathlib documentation was consulted for submodule image/equivalence
interfaces; the actually compiled declarations were checked against the local
pinned source, rather than assuming the live documentation matched the old pin.

  https://leanprover-community.github.io/mathlib4_docs/Mathlib/Algebra/Module/Submodule/Map.html
  https://leanprover-community.github.io/mathlib4_docs/Mathlib/Algebra/Module/Submodule/Equiv.html

The five preserved compact runtime parts were assembled and their full SHA256
matched f7548038f94ea30789ce28fc2ff769c40e9c37d8879ea133e9bea821056342c7.
Extraction exited zero. Runtime and cached dependency binaries are not included
in this focused release. This is artifact integrity, not external authorship or
proof that dependencies were independently rebuilt.
