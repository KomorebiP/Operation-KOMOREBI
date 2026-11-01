# Resolution Semantics: checked traversal solver, companion 0.6.0

This companion adds executable reconstruction from supplied, checked
component-root walks. It chooses a root value from any pin in that component,
or false when no pin is present, integrates the supplied walks, and checks the
result against every edge and every pin. This solver path does not enumerate
Boolean vertex labelings.

Lean proves universal soundness and completeness for this input contract. The
new solver succeeds exactly when the exhaustive reference solver succeeds.
Returned labelings are proved equal when pins cover every component. Without
that coverage, a changed root can select a different valid reconstruction.

## Input and remaining scope

`RootedTraversal G c` contains a certified index of the actual components and
an actual finite `Walk` from its component representative to every vertex.
The walk type checks every edge and both endpoints. The examples provide
executable traversal data, with no classical choice used to construct them.

The caller must supply this checked data. Automatic construction from an
arbitrary input graph remains a separate obligation. The walks need not form
an acyclic forest, and no forest-construction algorithm, runtime bound or
performance benchmark is claimed here. The exhaustive `solve` function remains
available as the reference implementation.

The unchanged [0.5.0 companion](../resolution-semantics-v0.5.0/README.md) retains
its original evidence. Twelve inherited proof and demonstration sources are
preserved byte for byte. The original manuscript and earlier companions are
unchanged. The package uses Lean 4.24.0 and bundled `Std`, with no external
library dependencies.

## Reproduce

Run from this directory using the pinned compiler and Python 3.10 or later:

```text
lake build
lake env lean --run GraphTraversalDemo.lean
python replay.py --lean lean --output ../../verification/current/resolution-semantics-traversal-new-run
```

Each replay needs a fresh output directory. The runner compiles fresh proof
objects, checks every theorem's axiom inventory, verifies four demonstrations,
and requires specific mathematical diagnostics for its rejection controls.
It covers 182 theorem declarations, 41 executable cases and 15 rejection
controls. The declarations comprise 157 inherited declarations and 25 new
supporting, solver and example declarations, rather than 182 manuscript
theorems.

The [source-bound Windows replay](../../verification/resolution-semantics/traversal-windows-2026-11-01-run1/receipt.json)
passed at source commit `5786646c1a889becc1c3f03b5af6eb8c8b1e2828` with no local
companion changes. It records every compiled input hash and retains all raw
output and rejection diagnostics.

## Claim map

| Contract | Lean declaration |
|---|---|
| Walk integration recovers the difference of endpoint values | `traversal_potential_of_integrates` |
| A pin anywhere in a component fixes its root value | `component_root_value_at_pin` |
| A jointly satisfiable input makes the candidate pass all constraints | `traversal_candidate_integrates`, `traversal_candidate_matches_pins` |
| Every returned result satisfies every edge and pin | `traversal_solve_sound` |
| Every jointly satisfiable input is accepted | `traversal_solve_of_solution`, `traversal_solve_complete` |
| `none` means exactly that no joint solution exists | `traversal_solve_none_iff_no_solution` |
| Agreement with the reference on existence | `traversal_solve_none_iff_reference`, `traversal_solve_agrees_on_existence` |
| Equal returned labelings under component-covering pins | `traversal_solve_unique_when_covered` |

The root selection retains every supplied pin as a final constraint. Picking
one pin to set a component root does not discard conflicting pins. Checking
the full graph is necessary: a field can fit every supplied root walk while
violating an edge outside those walks.

## Executable checks

Fourteen new cases cover both diamond root values, a non-root pin, duplicate
and conflicting pins, another root, another root-to-vertex path, consistent
and inconsistent triangles, disconnected components, an isolated vertex and
the empty graph. The source is [GraphTraversalExamples.lean](GraphTraversalExamples.lean).
The 27 earlier cases remain in the replay.

Four new rejection controls try to omit an unused triangle edge, ignore a
non-root pin, accept conflicting pins, or demand equality with the reference
without component coverage. Each false mathematical conclusion must be
rejected by `decide`. Eleven earlier controls remain in place.

## Review

[PROOF_AUDIT.md](PROOF_AUDIT.md) records the exact contract, dependencies,
edge cases and limits. [PROVENANCE.json](PROVENANCE.json) binds the original
manuscript and inherited sources. This is self-review and Lean kernel
checking, not independent scientific review.

Standard classical dependencies are recorded explicitly wherever used. Both inherited two-world obstruction theorems remain
axiom-free. No accepted theorem may depend on `sorryAx` or a custom axiom.

Rank formulas, automatic traversal/forest construction, general Boolean-valued
transport, selectors, weighted multiresolution and forcing applications remain
outside this increment. The manuscript remains active development. Abstract
graph labelings are not asserted to be realizable by models of ZFC or forcing
diagrams.
