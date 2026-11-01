# Resolution Semantics: graph reconstruction companion 0.3.0

Lean 4.24.0 checks simple-cycle integrability, componentwise ambiguity and
root-fixed uniqueness, with an executable finite reference solver. This extends
the [0.2.0 companion](../resolution-semantics-v0.2.0/README.md), whose files and
recorded evidence remain unchanged. The original manuscript and scaffold are
also preserved.

The package has no external dependencies beyond Lean's bundled `Std`.
It contains **83 theorem declarations**: the 34 inherited declarations and
49 graph, solver, example and supporting declarations. This is a declaration
count, not a count of manuscript theorems.

## Reproduce

From this directory with the pinned toolchain and Python 3.10 or later:

```text
lake build
lake env lean --run GraphDemo.lean
python replay.py --lean lean --output ../../verification/current/resolution-semantics-graphs-new-run
```

Use a new output directory for every replay. The runner compiles fresh proof
objects, treats warnings as errors, checks every declared theorem's axiom
inventory, runs seven graph examples and checks five expected rejections.
Setup, parser and import errors cannot satisfy the rejection controls.

## Exact formal scope

The manuscript is a finite **simple undirected graph** with binary vertex
labels. `SimpleGraph` records a symmetric, irreflexive adjacency relation.
The residual field is a function on ordered vertex pairs, constrained to be
symmetric on edges; its values on nonedges are ignored. Its derivative is XOR
of the two endpoint labels. A simple cycle is a closed walk of length at least
three whose vertex list, with its final repeated endpoint removed, has no
duplicates. The formal argument proves that this simple-cycle condition also
annihilates every closed walk.

| Manuscript scope | Formal result | Coverage |
|---|---|---|
| Theorem 6.1(1), kernel description | `kernel_iff_componentwise_constant` | Zero derivative exactly characterizes labels constant along connected components. The dimension formula is not formalized. |
| Theorem 6.1(2), integrability | `integrable_iff_cycle_zero` | Reconstruction exists if and only if every simple cycle has zero XOR sum. |
| Theorem 6.1(3), root-fixed uniqueness | `root_fixed_unique`, `pins_cover_unique` | Equality at one vertex of every component forces equality everywhere. Empty graphs and isolated vertices are included. |
| Theorem 6.1(3), reconstruction ambiguity | `reconstruction_classification` | Reconstructions are uniquely parameterized by one Boolean value per component. No separate numerical cardinality theorem is asserted. |
| Finite executable reconstruction | `solve_sound`, `solve_complete`, `solve_none_iff_no_solution` | For every `Fin n` graph, search returns an integrating label assignment matching the supplied pins exactly when one exists. |
| Executable cycle criterion | `solve_exists_iff_cycle_zero` | With no pins, successful finite search is equivalent to the simple-cycle condition. |
| Theorem 7.3 | The inherited `KRS.TwoWorld.no_swap_equivariant_*` theorems | The additive and Boolean two-world obstructions are unchanged. |

The graph existence proof selects a representative and a path for each
connected component. It therefore uses standard classical choice and quotient
reasoning. The axiom inventory records these dependencies explicitly. Both
inherited two-world obstruction theorems remain axiom-free. No accepted theorem
may depend on `sorryAx` or a custom axiom.

## Executable examples

`GraphDemo.lean` runs the exact solver defined in `GraphSolver.lean`:

```text
diamond-root-false: some [false, true, false, true]
diamond-root-true: some [true, false, true, false]
inconsistent-triangle: none
disconnected-with-isolated-vertex: some [false, true, true, true, true]
empty-graph: some []
isolated-vertex-true: some [true]
contradictory-root-pins: none
```

The solver enumerates all `2^n` binary labelings and checks every edge and pin.
It is a small reference implementation, not an efficient spanning-forest
implementation. Its universal soundness and completeness proofs are separate
from the concrete examples. Pin consistency is checked; uniqueness requires
the explicit hypothesis that pins cover every component.

## Review and remaining work

[PROOF_AUDIT.md](PROOF_AUDIT.md) records the claim, dependency graph, edge-case
review and limitations. This is self-review and Lean kernel checking, not an
independent scientific review. [PROVENANCE.json](PROVENANCE.json) binds the
manuscript and inherited source identities.

The numerical cardinality and rank formulas of Theorem 6.1, arbitrary
Boolean-algebra-valued transport, selector and envelope results, weighted
multiresolution and forcing applications remain outside this increment.
Binary graph labelings are not claimed to be realized by models of ZFC or
forcing diagrams. The paper remains active development.
