# Foundations used by block 08

Pinned Mathlib supplies orthogonal projection and the Banach open mapping theorem.
The new restriction, inverse, source-optimality, conditioning and integration code
is built on those imported theorems rather than claiming to re-prove the entire
functional-analytic foundation. The exact upstream source is preserved in the
portable runtime at revision aeb72f1e9981b6d35b426b16dca7759be3e7ba06.

Relevant modules: Mathlib.Analysis.InnerProductSpace.Projection.Basic and
Mathlib.Analysis.Normed.Operator.Banach. Online reference pages consulted:
https://leanprover-community.github.io/mathlib4_docs/Mathlib/Analysis/InnerProductSpace/Projection/Basic.html
https://leanprover-community.github.io/mathlib4_docs/Mathlib/Analysis/Normed/Operator/Banach.html

The formal checker and axiom trust boundary follow Lean's validation model:
https://lean-lang.org/doc/reference/latest/ValidatingProofs/

The runtime source, not a changing online documentation page, determined the APIs
actually compiled. No literature-priority or historical novelty audit was run.
