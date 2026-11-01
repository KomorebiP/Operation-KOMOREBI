# Resolution Semantics: checked Lean subset

A separate **0.2.0 formal companion** now provides a pinned Lean 4.24.0 build
for the original two-valued scaffold and Theorem 7.3, the two-world symmetry
obstruction. The paper remains an active development.

The [source and reproduction guide](../../formal/resolution-semantics-v0.2.0/README.md)
contains the exact claim map and self-review. The
[two-world proof](../../formal/resolution-semantics-v0.2.0/TwoWorld.lean)
quantifies over arbitrary candidate retractions. It proves that no additive
retraction onto the diagonal of the two-world Boolean ring can commute with
coordinate swap. The Boolean retraction obstruction follows immediately.

The [fresh Windows replay receipt](../../verification/resolution-semantics/windows-2026-10-30-run5/receipt.json)
records 34 accepted theorem declarations: 15 inherited scaffold statements
and 19 new declarations, including the two main assertions and supporting
lemmas and controls. Both main assertions have empty axiom inventories.
One inherited helper uses `propext`; none uses `sorryAx` or custom axioms.
Three rejection controls passed for the intended reasons.

The [original scaffold](../../research/resolution-semantics/formal/KRS_Core.lean)
is preserved with its original uncompiled label. The companion moves its
import before module documentation and fixes three pointwise rewrite proofs,
without changing those theorem statements. Its
[provenance record](../../formal/resolution-semantics-v0.2.0/PROVENANCE.json)
identifies the original source, manuscript and compiler.

The general Boolean-algebra, graph, selector, multiresolution and forcing
theorems still need their own formal contracts. This subset does not verify
the whole paper or construct a model of ZFC. Correspondence review here was
self-review, alongside actual Lean compilation.

[Work overview](../works/resolution-semantics.md) ·
[Original source edition](../../research/resolution-semantics/README.md)
