# Resolution Semantics: checked Lean subset

The **0.8.0 formal companion** proves exact image and quotient cardinalities
and their binary cardinality rank formulas. It also constructs checked
traversals automatically and provides a sound and complete reconstruction
solver for finite decidable graphs. It retains exact counts with arbitrary vertex pins, the cycle
criterion, root-fixed uniqueness and the two-world symmetry obstruction. The
package uses Lean 4.24.0 and bundled `Std`. The paper remains active development.

The [source and reproduction guide](../../formal/resolution-semantics-v0.8.0/README.md)
maps each checked claim to the manuscript. For an integrable binary edge field
on a finite simple undirected graph with `c` connected components, there are
exactly **`2^c` distinct vertex reconstructions**. The
[counting proof](../../formal/resolution-semantics-v0.8.0/GraphCounting.lean)
constructs a complete, duplicate-free list of actual component classes for
every finite graph. The final theorem does not need a component index supplied
by the caller.

The executable `allSolutions` list contains every integrating binary vertex
labeling exactly once. Its length is proved equal to `2 ^ componentCount G`.
The empty graph has one empty labeling; an isolated vertex contributes an
independent Boolean choice. A nonintegrable field has no reconstructions.
The mathematical component enumeration in the inherited count theorem uses
standard classical reasoning and the supplied vertex order. No
symmetry-invariant ordering is asserted.

The [partial-pin proof](../../formal/resolution-semantics-v0.8.0/GraphPinning.lean)
extends this contract to any finite list of vertex/value pairs. If the edge
equations and all pins are jointly consistent, there are exactly **`2^u`
reconstructions**, where `u` counts actual components containing no pinned
vertex. Otherwise there are zero. A complete duplicate-free list identifies
exactly these unpinned component classes. Repeated pins and pins at multiple
vertices of the same component remove only one component choice; conflicting
pins remain constraints and can make reconstruction impossible.

The total counting theorem connects the formula to the inherited sound and complete
solver. It needs no caller-supplied component partition or consistency witness.
An executable list contains every jointly satisfying labeling exactly once.

For symmetric edge data, the inherited
[graph proofs](../../formal/resolution-semantics-v0.8.0/GraphReconstruction.lean)
establish integrability exactly when every simple cycle has zero XOR sum.
The kernel is componentwise constant. Fixing one vertex value per component
makes reconstruction unique. The
[finite reference solver](../../formal/resolution-semantics-v0.8.0/GraphSolver.lean)
checks every edge and supplied pin, with universal soundness and completeness
proofs. It enumerates all binary labelings and is intended for small examples.

The [traversal solver](../../formal/resolution-semantics-v0.8.0/GraphTraversalSolver.lean)
chooses component root values from pins, integrates supplied walks and checks
one candidate against every edge and pin. This solver path does not enumerate
Boolean vertex labelings. It succeeds exactly when the reference solver
succeeds. The returned labelings are proved equal when pins cover every
component; a changed root can select another valid labeling otherwise.

The [automatic constructor](../../formal/resolution-semantics-v0.8.0/GraphAutomaticTraversal.lean)
now computes that index and those walks from the graph. Its
[indexed path table](../../formal/resolution-semantics-v0.8.0/GraphPathSearch.lean)
covers every reachable pair after `n` rounds on `Fin n`; actual stored walks
prevent false reachability. Representatives are selected in the supplied
vertex order and duplicate representatives are removed. Array sizes and
dependent entry indices are checked.

`automaticSolve` requires no caller-supplied traversal or partition. It is
sound and complete for arbitrary proposed binary edge fields and pins, and
agrees with the exhaustive reference on existence. It computes graph paths
rather than enumerating binary vertex labelings. Acyclicity, a sparse forest,
symmetry-invariant representatives and a runtime bound are not asserted.

The [rank proofs](../../formal/resolution-semantics-v0.8.0/GraphRanks.lean)
index each actual undirected edge once. If the graph has `n` vertices, `m`
edges and `c` components, the derivative image contains exactly **`2^(n-c)`**
fields, and the additive quotient of edge fields by that image contains
exactly **`2^(m+c-n)`** classes. Both lists are complete and duplicate-free.
The proof counts equal derivative fibers and equal cosets before taking `log2`
to obtain the cardinality ranks `n-c` and `m+c-n`. These are the cardinality
forms of manuscript Theorem 6.1(4), with no external module/basis library.

The bound `c≤n` and the bound `n-c≤m` are proved. The quotient formula uses
natural subtraction only after adding `c`; `(m-n)+c` would truncate too early
on edgeless graphs. The paper's integer notation `m-n+c` has the intended value.
Eleven new [rank cases](../../formal/resolution-semantics-v0.8.0/GraphRankExamples.lean)
enumerate the actual image and quotient for paths, cycles, disconnected graphs,
isolated vertices, the complete four-vertex graph and the empty graph.
The exhaustive rank enumerations carry no efficiency claim.

[Executable count cases](../../formal/resolution-semantics-v0.8.0/GraphCountExamples.lean)
give two reconstructions for the connected diamond, eight for two edges plus
an isolated vertex, one for the empty graph, two for one isolated vertex,
sixteen for four isolated vertices, and zero for the inconsistent triangle.
[Fourteen partial-pin cases](../../formal/resolution-semantics-v0.8.0/GraphPinExamples.lean)
include duplicate and conflicting pins, pins within one or several components,
isolated vertices, the empty graph and a nonintegrable field.
[Fourteen traversal cases](../../formal/resolution-semantics-v0.8.0/GraphTraversalExamples.lean)
include changed roots and paths, non-root pins, conflicting pins and non-tree
edge constraints.
[Twenty-one automatic cases](../../formal/resolution-semantics-v0.8.0/GraphAutomaticExamples.lean)
include 8/32-vertex paths, asymmetric proposed fields, non-root pins,
disconnected graphs and computed component counts. Exact executable outputs
are checked by the replay; the generic Lean theorems establish correctness.
The [source-bound Windows replay](../../verification/resolution-semantics/ranks-windows-2026-11-01-run2/receipt.json)
checks **266 theorem declarations**, 73 executable cases and twenty-six rejection
controls. The declaration count includes supporting lemmas and examples; it
is not a count of manuscript theorems.

The inventories explicitly record standard classical choice, quotient
soundness and propositional extensionality where used. Both inherited
two-world obstruction theorems remain axiom-free. No accepted theorem depends
on `sorryAx` or custom axioms. The
[self-review](../../formal/resolution-semantics-v0.8.0/PROOF_AUDIT.md) states the
claim, dependency graph, assumptions and edge cases. This is author-side
review and Lean kernel checking, not independent scientific review.

The [original scaffold](../../research/resolution-semantics/formal/KRS_Core.lean)
retains its original uncompiled label. The
[0.7.0 automatic-traversal companion](../../formal/resolution-semantics-v0.7.0/README.md),
[0.6.0 supplied-traversal companion](../../formal/resolution-semantics-v0.6.0/README.md),
[0.5.0 partial-pin companion](../../formal/resolution-semantics-v0.5.0/README.md),
[0.4.0 counting companion](../../formal/resolution-semantics-v0.4.0/README.md),
[0.3.0 graph companion](../../formal/resolution-semantics-v0.3.0/README.md) and
[0.2.0 two-world companion](../../formal/resolution-semantics-v0.2.0/README.md)
remain unchanged with their dated evidence.
[Provenance](../../formal/resolution-semantics-v0.8.0/PROVENANCE.json) binds the
new companion to the manuscript and preserved inherited sources.

A module/basis library interface, a verified sparse forest implementation,
complexity bounds, general
Boolean-algebra-valued transport, selector/envelope results, weighted
multiresolution and forcing applications remain outside this increment.
Abstract graph labelings are not claimed to be realized by models of ZFC or
forcing diagrams.

[Work overview](../works/resolution-semantics.md) ·
[Original source edition](../../research/resolution-semantics/README.md)
