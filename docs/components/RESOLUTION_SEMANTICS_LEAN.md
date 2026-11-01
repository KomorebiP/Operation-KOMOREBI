# Resolution Semantics: checked Lean subset

The **0.5.0 formal companion** proves exact counts for binary graph
reconstruction with arbitrary vertex pins, alongside the inherited cycle
criterion, root-fixed uniqueness and two-world symmetry obstruction. The package uses Lean 4.24.0 and its
bundled `Std`. The paper remains active development.

The [source and reproduction guide](../../formal/resolution-semantics-v0.5.0/README.md)
maps each checked claim to the manuscript. For an integrable binary edge field
on a finite simple undirected graph with `c` connected components, there are
exactly **`2^c` distinct vertex reconstructions**. The
[counting proof](../../formal/resolution-semantics-v0.5.0/GraphCounting.lean)
constructs a complete, duplicate-free list of actual component classes for
every finite graph. The final theorem does not need a component index supplied
by the caller.

The executable `allSolutions` list contains every integrating binary vertex
labeling exactly once. Its length is proved equal to `2 ^ componentCount G`.
The empty graph has one empty labeling; an isolated vertex contributes an
independent Boolean choice. A nonintegrable field has no reconstructions.
The mathematical component enumeration uses standard classical reasoning and
the supplied vertex order. No symmetry-invariant ordering is asserted.

The [partial-pin proof](../../formal/resolution-semantics-v0.5.0/GraphPinning.lean)
extends this contract to any finite list of vertex/value pairs. If the edge
equations and all pins are jointly consistent, there are exactly **`2^u`
reconstructions**, where `u` counts actual components containing no pinned
vertex. Otherwise there are zero. A complete duplicate-free list identifies
exactly these unpinned component classes. Repeated pins and pins at multiple
vertices of the same component remove only one component choice; conflicting
pins remain constraints and can make reconstruction impossible.

The total theorem connects the formula to the inherited sound and complete
solver. It needs no caller-supplied component partition or consistency witness.
An executable list contains every jointly satisfying labeling exactly once.

The inherited [graph proofs](../../formal/resolution-semantics-v0.5.0/GraphReconstruction.lean)
establish integrability exactly when every simple cycle has zero XOR sum.
The kernel is componentwise constant. Fixing one vertex value per component
makes reconstruction unique. The
[finite reference solver](../../formal/resolution-semantics-v0.5.0/GraphSolver.lean)
checks every edge and supplied pin, with universal soundness and completeness
proofs. It enumerates all binary labelings and is intended for small examples.
A faster spanning-forest implementation remains future work.

[Executable count cases](../../formal/resolution-semantics-v0.5.0/GraphCountExamples.lean)
give two reconstructions for the connected diamond, eight for two edges plus
an isolated vertex, one for the empty graph, two for one isolated vertex,
sixteen for four isolated vertices, and zero for the inconsistent triangle.
[Fourteen partial-pin cases](../../formal/resolution-semantics-v0.5.0/GraphPinExamples.lean)
include duplicate and conflicting pins, pins within one or several components,
isolated vertices, the empty graph and a nonintegrable field.
The [source-bound Windows replay](../../verification/resolution-semantics/pins-windows-2026-11-01-run1/receipt.json)
checks **157 theorem declarations**, seven inherited graph cases, six unpinned
count cases, fourteen partial-pin cases and eleven rejection controls. The
declaration count includes supporting
lemmas and examples; it is not a count of manuscript theorems.

The inventories explicitly record standard classical choice, quotient
soundness and propositional extensionality where used. Both inherited
two-world obstruction theorems remain axiom-free. No accepted theorem depends
on `sorryAx` or custom axioms. The
[self-review](../../formal/resolution-semantics-v0.5.0/PROOF_AUDIT.md) states the
claim, dependency graph, assumptions and edge cases. This is author-side
review and Lean kernel checking, not independent scientific review.

The [original scaffold](../../research/resolution-semantics/formal/KRS_Core.lean)
retains its original uncompiled label. The
[0.4.0 counting companion](../../formal/resolution-semantics-v0.4.0/README.md),
[0.3.0 graph companion](../../formal/resolution-semantics-v0.3.0/README.md) and
[0.2.0 two-world companion](../../formal/resolution-semantics-v0.2.0/README.md)
remain unchanged with their dated evidence.
[Provenance](../../formal/resolution-semantics-v0.5.0/PROVENANCE.json) binds the
new companion to the manuscript and preserved inherited sources.

The rank formulas `n-c` and `m-n+c`, general
Boolean-algebra-valued transport, selector/envelope results, weighted
multiresolution and forcing applications remain outside this increment.
Abstract graph labelings are not claimed to be realized by models of ZFC or forcing diagrams.

[Work overview](../works/resolution-semantics.md) ·
[Original source edition](../../research/resolution-semantics/README.md)
