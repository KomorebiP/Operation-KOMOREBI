# Resolution Semantics: partial vertex pins, companion 0.5.0

For arbitrary finite lists of binary vertex pins, this companion proves an
exact reconstruction count. If the edge equations and pins are jointly
consistent, there are exactly `2^u` distinct reconstructions, where `u` counts
the actual connected components containing no pinned vertex. Inconsistent
inputs have no reconstructions. Repeated pins do not remove extra component
choices; conflicting pins are retained as constraints.

This refines the checked binary graph contract associated with Theorem 6.1(3).
It does not modify the manuscript or the
[0.4.0 companion](../resolution-semantics-v0.4.0/README.md). All nine inherited
proof and demonstration sources are preserved byte for byte. The package uses
Lean 4.24.0 and its bundled `Std`, with no external library dependencies.

## Reproduce

Run from this directory with the pinned compiler and Python 3.10 or later:

```text
lake build
lake env lean --run GraphPinDemo.lean
python replay.py --lean lean --output ../../verification/current/resolution-semantics-pins-new-run
```

Use a new output directory for each replay. The runner compiles fresh proof
objects, inventories every theorem's axioms, checks all three demonstrations,
and requires mathematical diagnostics from each rejection control. It covers
157 theorem declarations, comprising 119 inherited declarations and 38 new
supporting, counting and example declarations. This is not a count of manuscript
theorems. There are 27 executable cases and 11 rejection controls.

## Exact contracts

| Claim | Formal result |
|---|---|
| Complete solution enumeration with all pin constraints | `pinned_solutions_complete`, `pinned_solutions_nodup` |
| Empty output exactly for joint inconsistency | `pinned_solutions_empty_iff` |
| Exactly `2^u` solutions when jointly consistent | `pinned_solutions_count_by_components` |
| Total formula: `2^u` if the verified solver succeeds, zero otherwise | `pinned_solutions_count_total` |
| The counted classes are exactly the components containing no pinned vertex, each once | `unpinned_components_complete`, `unpinned_components_nodup` |
| An explicit certified index supports executable examples | `pinned_solutions_count` |
| Removing all pins recovers the previous contract | `pinned_solutions_no_pins`, `unpinned_component_count_no_pins` |

`unpinnedComponentCount` is the length of a complete duplicate-free list of
actual component quotient classes containing no pinned vertex. Its construction
uses the earlier canonical component index, rather than an assumed partition or
caller-supplied number. It uses classical choice and quotient reasoning and is
not an efficient component-counting program.

The proof translates any jointly satisfying labeling by a componentwise Boolean
offset. A component containing a pin forces its offset to zero. The remaining
offsets are enumerated completely and without duplicates. The actual executable
solution list has exactly the same members as this translated enumeration.

Joint consistency includes the values of all pins, not only their locations.
The general conditional theorem requires a satisfying labeling; the total
formula uses the inherited sound and complete solver to distinguish success
from inconsistency. No pin compatibility test is assumed correct without proof.

## New executable cases

```text
diamond-no-pins: 2
diamond-one-pin: 1
diamond-duplicate-pin: 1
diamond-compatible-pins: 1
diamond-conflicting-pins: 0
diamond-contradictory-vertex-pins: 0
disconnected-no-pins: 8
disconnected-one-pin: 4
disconnected-same-component-pins: 4
disconnected-two-components-pinned: 2
disconnected-all-components-pinned: 1
empty-graph-no-pins: 1
isolated-vertex-pinned: 1
nonintegrable-triangle-pinned: 0
```

The three new rejection controls deliberately count pin entries instead of
distinct pinned components, ignore conflicting pins, or omit a free isolated
component. Each incorrect numerical conclusion must be rejected by Lean's
`decide` tactic. The eight earlier controls remain in place.

## Review and boundaries

[PROOF_AUDIT.md](PROOF_AUDIT.md) records the claim, dependencies, adversarial
checks and remaining scope. [PROVENANCE.json](PROVENANCE.json) binds the unchanged
manuscript and inherited sources. This is self-review and Lean kernel checking;
no independent scientific review is claimed.

Standard classical choice, quotient soundness and propositional extensionality
are recorded explicitly where used. The inherited two-world obstruction
theorems remain axiom-free. No accepted theorem may use `sorryAx` or a custom
axiom.

The solver still searches all binary vertex labelings. Rank formulas, an
efficient spanning-forest solver, general Boolean-algebra-valued transport,
selectors, weighted multiresolution and forcing applications remain outside
this increment. Abstract graph labelings are not asserted to be realized by
models of ZFC or forcing diagrams. The paper remains active development.
