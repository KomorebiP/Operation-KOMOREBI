# Resolution Semantics: checked Lean subset

The **0.3.0 formal companion** checks binary graph reconstruction as well as
the inherited two-world symmetry obstruction. The package uses Lean 4.24.0
and its bundled `Std`, with no external library dependency. The paper remains
active development.

The [source and reproduction guide](../../formal/resolution-semantics-v0.3.0/README.md)
maps each checked claim to the manuscript. The
[graph proofs](../../formal/resolution-semantics-v0.3.0/GraphReconstruction.lean)
establish that an undirected binary edge field is induced by vertex labels
exactly when every simple cycle has zero XOR sum. The kernel consists of labels
constant on connected components. Reconstructions are parameterized by one
Boolean value per component; fixing one vertex value per component makes the
reconstruction unique.

The [finite reference solver](../../formal/resolution-semantics-v0.3.0/GraphSolver.lean)
enumerates all binary labelings. Lean proves its soundness and completeness for
every graph on `Fin n` and every supplied list of vertex pins. It checks pin
consistency, including contradictory pins on one vertex. Uniqueness requires
pins to cover every component. This implementation is intended for small
examples; a faster spanning-forest implementation remains future work.

[Executable cases](../../formal/resolution-semantics-v0.3.0/GraphExamples.lean)
include the two diamond reconstructions, an inconsistent triangle, disconnected
components with an isolated vertex, an empty graph and conflicting pins. The
[source-bound Windows replay](../../verification/resolution-semantics/graphs-windows-2026-11-01-run1/receipt.json)
checks **83 theorem declarations**, seven executable cases and five rejection
controls. The declaration count includes supporting lemmas and examples; it is
not a count of manuscript theorems.

The graph existence proof records standard classical choice and quotient
dependencies. Both inherited two-world obstruction theorems remain axiom-free.
No accepted theorem depends on `sorryAx` or custom axioms. The
[self-review](../../formal/resolution-semantics-v0.3.0/PROOF_AUDIT.md) describes the
definitions, cycle-to-walk argument, root hypotheses and exact limitations.
This is author-side review and kernel checking, not independent review.

The [original scaffold](../../research/resolution-semantics/formal/KRS_Core.lean)
retains its original uncompiled label. The
[0.2.0 companion](../../formal/resolution-semantics-v0.2.0/README.md) and its
[dated replay](../../verification/resolution-semantics/windows-2026-10-30-run5/receipt.json)
are preserved. [Provenance](../../formal/resolution-semantics-v0.3.0/PROVENANCE.json)
binds the new companion to the manuscript and unchanged inherited sources.

Numerical cardinality and rank formulas, general Boolean-algebra-valued
transport, selector and envelope results, weighted multiresolution and forcing
applications remain outside this increment. Abstract graph labelings are not
claimed to be realized by models of ZFC or forcing diagrams.

[Work overview](../works/resolution-semantics.md) ·
[Original source edition](../../research/resolution-semantics/README.md)
