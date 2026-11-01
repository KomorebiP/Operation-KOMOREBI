# Resolution Semantics: exact reconstruction counts, companion 0.4.0

For an integrable binary edge field on a finite simple undirected graph with
`c` connected components, Lean 4.24.0 now proves that there are exactly `2^c`
vertex reconstructions. The empty graph has one reconstruction. Isolated
vertices contribute independent Boolean choices. A nonintegrable field has
no reconstructions.

This companion preserves the source and evidence for
[0.3.0](../resolution-semantics-v0.3.0/README.md) and
[0.2.0](../resolution-semantics-v0.2.0/README.md). It uses Lean's bundled `Std`
and has no external library dependencies. Its **119 theorem declarations**
comprise 83 inherited declarations and 36 counting, component-index, example
and supporting declarations. This is not a count of manuscript theorems.

## Reproduce

With the pinned toolchain and Python 3.10 or later, run from this directory:

```text
lake build
lake env lean --run GraphDemo.lean
lake env lean --run GraphCountDemo.lean
python replay.py --lean lean --output ../../verification/current/resolution-semantics-counting-new-run
```

Use a fresh output directory for every replay. The runner compiles fresh proof
objects, checks every theorem's axiom inventory, verifies seven inherited graph
examples and six count examples, and checks eight expected rejections.

The [source-bound Windows replay](../../verification/resolution-semantics/counting-windows-2026-11-01-run1/receipt.json)
passed all 119 declarations, thirteen executable cases and eight rejection
controls. It records clean source commit
`99b8fca55b0fc216e7f09d30102f25b5a0f61944` and every compiled input hash.

## What the count means

`allSolutions G r` is an executable list that checks every binary vertex
labeling against every edge. Lean proves that its members are exactly the
integrating labelings and that the list has no duplicates. Its length is
therefore the number of distinct reconstructions, rather than a count of
search visits or repeated witnesses.

`componentCount G` is the length of a complete, duplicate-free list of the
actual connected-component quotient classes. The proof constructs a canonical
component index for every graph on `Fin n`. It does not assume an unverified
partition or a component count supplied by the caller. Component enumeration
uses standard classical equality and choice; this mathematical definition is
not a fast executable component-counting algorithm.
The index follows the supplied `Fin n` vertex order. No symmetry-invariant
ordering or Boolean projector is claimed.

The component-index certificate is also exposed for concrete examples. Its
edge compatibility, component coverage and representative laws induce inverse
maps between the component quotient and `Fin c`. These laws rule out splitting
a component, merging disconnected components or adding unused labels.

| Manuscript scope | Formal result | Coverage |
|---|---|---|
| Theorem 6.1(3), numerical reconstruction count | `all_solutions_count_by_components` | For every finite simple graph with decidable adjacency and an integrable field, the complete solution list has length `2 ^ componentCount G`. |
| Count with an explicit component index | `all_solutions_count` | The same formula for any verified index with `c` classes. |
| Count under the cycle criterion | `all_solutions_count_of_cycle_zero` | Symmetric edge data and zero XOR on every simple cycle imply the formula. |
| Meaning of component count | `component_list_complete`, `component_list_nodup`, `canonicalComponentIndex` | Enumeration contains each actual component exactly once, including isolated vertices. |
| Meaning of solution count | `all_solutions_complete`, `all_solutions_nodup`, `all_solutions_empty_iff` | Exact enumeration, no duplicates, and emptiness exactly when the field is not integrable. |
| Cardinality of Boolean choices | `assignments_complete`, `assignments_nodup`, `assignments_length` | Every Boolean function on `Fin c` occurs exactly once in a list of length `2^c`. |
| Earlier graph reconstruction and Theorem 7.3 | Inherited declarations | The 0.3.0 graph contracts and two-world obstructions are unchanged. |

The numerical count is proved by connecting two complete duplicate-free lists:
the actual finite solver output and the component choices transported through
the checked reconstruction classification. Equality of their lengths is a
general Lean proof, separate from the numerical examples.

## Executable count examples

```text
diamond-connected: 2
inconsistent-triangle: 0
two-edges-and-isolated-vertex: 8
empty-graph: 1
isolated-vertex: 2
four-isolated-vertices: 16
```

The three additional rejection controls try to apply the power-of-two formula
to a nonintegrable triangle, omit the isolated component in the disconnected
example, and assign zero reconstructions to the empty graph. Each must fail
for a checked mathematical reason. The five earlier controls are retained.

The reference solver still enumerates all binary labelings and is intended for
small examples. A verified spanning-forest implementation remains future work.

## Review and remaining work

[PROOF_AUDIT.md](PROOF_AUDIT.md) gives the exact claim, dependency graph,
obligations and limitations. [PROVENANCE.json](PROVENANCE.json) binds the
manuscript and unchanged inherited sources. This is self-review and Lean kernel
checking, not an independent scientific review.

The inventories explicitly record standard classical choice, quotient
soundness and propositional extensionality where used. Both inherited
two-world obstruction theorems remain axiom-free. No accepted theorem may
depend on `sorryAx` or a custom axiom.

The rank formulas `n-c` and `m-n+c`, numerical counts under partial pinning,
general Boolean-algebra-valued transport, selector/envelope results, weighted
multiresolution and forcing applications remain outside this increment. The paper remains active
development. Abstract graph labelings are not asserted to be realized by
models of ZFC or forcing diagrams.
