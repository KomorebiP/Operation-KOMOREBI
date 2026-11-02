# Resolution Semantics: automatic traversal, companion 0.7.0

`automaticSolve G r pins` constructs its own checked component index and root
walks from a finite decidable graph. The caller supplies no traversal or
component partition. Lean proves that it returns a labeling satisfying every
edge and pin exactly when one exists. The executable algorithm does not
enumerate Boolean vertex assignments.

The construction tabulates actual walks for all vertex pairs. After `n` path
extension rounds on `Fin n`, every reachable pair is covered. It then selects
the first reachable representative in the supplied vertex order, removes
duplicate representatives, and constructs the component index and root walks
required by the preserved traversal solver.

The indexed array cache checks its size and the dependent index of every
entry. No unchecked array lookup or assumed path certificate is used. The
result is a traversal constructor; acyclicity, a sparse spanning forest, an
asymptotic runtime bound and a benchmark claim are not part of this increment.

The [0.6.0 companion](../resolution-semantics-v0.6.0/README.md), all earlier
companions and the original manuscript retain their sources and dated
evidence. Fifteen inherited proof and demonstration files are preserved byte
for byte. The package uses Lean 4.24.0 and bundled `Std`, without external
library dependencies.

## Reproduce

Run from this directory with the pinned compiler and Python 3.10 or later:

```text
lake build
lake env lean --run GraphAutomaticDemo.lean
python replay.py --lean lean --output ../../verification/current/resolution-semantics-automatic-new-run
```

Use a fresh output directory for each replay. It compiles fresh proof objects,
inventories every theorem's axioms, checks exact output from five executable
demonstrations, and requires mathematical diagnostics for every rejection.
The runner covers 216 theorem declarations, 62 executable cases and 20
rejection controls. These include 182 inherited declarations and 34 new
supporting, construction, solver and example declarations. They are not 216
manuscript theorems.

## Exact contracts

| Claim | Lean declaration |
|---|---|
| Indexed cache lookup recovers the tabulated value | `cache_get_of_fn` |
| Every walk of length at most `k` is covered after `k` rounds | `bounded_paths_complete` |
| After `n` rounds, stored paths exist exactly for reachable pairs | `bounded_paths_reachable` |
| Representatives are constant on actual components and idempotent | `selected_root_constant`, `selected_root_idempotent` |
| The computed roots are duplicate-free and each index is used | `automatic_roots_nodup`, `automatic_root_fixed`, `automaticIndex` |
| Actual root walks and a component index are constructed automatically | `traversalOfPaths`, `buildTraversal` |
| Every returned labeling satisfies every edge and pin | `automatic_solve_sound` |
| Every jointly satisfiable input is accepted | `automatic_solve_complete` |
| `none` means exactly that no joint solution exists | `automatic_solve_none_iff_no_solution` |
| Agreement with the reference on existence | `automatic_solve_agrees_on_existence` |
| Equal returned labelings under component-covering pins | `automatic_solve_unique_when_covered` |

The finite search proof reduces an arbitrary graph walk to a simple walk using
an auxiliary zero field. That zero field always satisfies the cycle condition;
no integrability or cycle condition is assumed for the caller's field `r`.
The actual field and every original pin are checked by the solver.

Representative selection uses the supplied `Fin n` order. It does not assert
an ordering invariant under graph symmetries or construct a canonical Boolean
projector. Standard classical dependencies in the correctness proofs are
listed explicitly; operational path and component data are computed.

## Executable checks

Twenty-one new cases cover diamonds, consistent and inconsistent triangles,
an asymmetric proposed edge field, disconnected components, duplicate and
conflicting pins, isolated vertices, the empty graph, and paths with 8 and 32
vertices. Four cases check computed component counts, including zero for the
empty graph. Source: [GraphAutomaticExamples.lean](GraphAutomaticExamples.lean).

The replay checks these concrete outputs by executing the program. Universal
correctness is established by the Lean theorems above; no runtime measurement
is used as a substitute for proof. The 41 earlier executable cases remain.

Five new controls reject zero-round reachability, insufficient search rounds,
merging disconnected components, accepting contradictory pins, and inventing
a component for an empty graph. Each false conclusion must be rejected by
`decide`. Fifteen earlier controls remain.

## Review and remaining work

[PROOF_AUDIT.md](PROOF_AUDIT.md) records the precise contract, dependencies,
edge cases and limitations. [PROVENANCE.json](PROVENANCE.json) binds the
manuscript and inherited sources. This is self-review and Lean kernel checking,
not independent scientific review.

Both inherited two-world obstruction theorems remain axiom-free. Other
standard classical dependencies are inventoried where used. No accepted
theorem may depend on `sorryAx` or a custom axiom.

Rank formulas, a verified sparse spanning-forest implementation, complexity
bounds, general Boolean-valued transport and the wider manuscript remain
separate obligations. The paper remains active development; no model-theoretic
or forcing realization claim is added.
