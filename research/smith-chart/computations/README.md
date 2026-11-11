# Five-node reactive-placement recount

The archive reports 168 symmetry classes after applying specified graph
filters to five-node placements of three inductors and three capacitors. The
[recount](check_five_node_orbits.py) reimplements that finite calculation
using breadth-first connectivity and an alternate-path cycle test. It reads
the archived catalogue directly from the checksum-bound research ZIP.

For the ten possible undirected edges, each component type occupies three
distinct edges; an inductor and capacitor may share an edge. Vertices 0 and 1
are the terminals. The implemented filters reject a terminal connection by
inductors alone or capacitors alone, a same-type cycle, and the two stated
endpoint-visibility failures. The quotient permits exchanging the terminals
and permuting the other three vertices, while keeping component types
distinct.

The [recorded run](verification/five-node-002.json) obtains 14,400 labelled
placements, 1,934 filter survivors, and 168 orbits. It checks that the
archive's representatives cover those orbits exactly and that every recorded
orbit size agrees. As a check on the equivalence relation, omitting terminal
exchange yields 336 classes. Orbit sizes with terminal exchange are 2, 6, and
12, occurring 1, 12, and 155 times respectively.

This is an independent implementation of the **finite graph calculation**,
not an independent mathematical review. It does not prove that the filters
are necessary for every electrical realization, solve the resistor values,
cover larger graphs, or establish six-element feasibility or impossibility.
The original archive and its mathematical arguments remain unchanged.

Run `python research/smith-chart/computations/check_five_node_orbits.py` with
Python 3. Pass `--output <new-file>` to save a fresh JSON receipt. The checker
uses only the standard library and verifies the ZIP and catalogue hashes.

## A bounded attempt at one candidate

The archive's best reported five-node fit uses catalogue placement 142. The
[restart experiment](probe_five_node_fit.py) starts from that saved fit and
49 seeded random starts, with at most 1,600 function evaluations per start.
Its [record](verification/five-node-fit-003.json) includes all parameters,
the training and disjoint holdout grids, component conventions, numerical
environment, termination statuses, and a finite-difference Jacobian check.

The smallest observed maximum scaled error was approximately
`0.00113538469` on the 48-point training grid and `0.00115751662` on the
128-point holdout grid. These are floating-point residuals, not exact
identities. The search varied only one placement, bounded all log-parameters
to `[-25, 25]`, and did not exhaust starting points or possible networks. It
neither constructs an exact circuit nor proves that one does not exist.

An [exact rational follow-up](check_saved_candidate.py), with its
[receipt](verification/candidate-142-exact-001.json), interprets the best
recorded decimal parameters as exact rational numbers and solves the nodal
equations at \(s=1/10,1,10\). All three differences from the target are
nonzero. This rules out those recorded decimal values as an exact witness; it
does not exclude nearby real values or the topology itself.

The experiment uses NumPy and SciPy; exact versions and the seed are recorded.
In an environment with those versions installed, run:

```text
python research/smith-chart/computations/probe_five_node_fit.py --starts 50 --max-nfev 1600 --seed 20261111 --output <new-file>
```

The script verifies its archived input hashes before running and never
overwrites an existing receipt.
## Exact continuation

`derive_candidate_142.py` now gives an exact formulation for the archived
five-node reactive placement 142. The
[system record](verification/candidate-142-system-001/system.json) contains
seven ascending numerator coefficients, seven denominator coefficients, and
all thirteen coefficient equations against the degree-six target. The 125
spanning trees and 50 separating two-forests agree **symbolically** with direct
nodal determinant expansions. All equations have total degree at most four.
This completes the encoding step; positivity feasibility remains unresolved.

`check_completion_boundary.py` supports the separate
[singular-completion note](../../../docs/demonstrations/SMITH_SINGULAR_COMPLETION.md).
It checks exact determinant and nullspace identities and five rational
examples. These are symbolic checks for a written proof, with six selected
statements also checked in Lean.

The new run directories include version-2 manifests with observed input
hashes before and after execution, software versions, logs, result hashes,
and limits:

- `verification/candidate-142-system-001/`
- `verification/completion-boundary-003/`

The run status is `completed` in both. Their mathematical interpretation is
recorded in `../edition/review.md`. The exact checks can be reproduced in new
output paths with:

```text
python -B research/smith-chart/computations/derive_candidate_142.py --output <new-system-json>
python -B research/smith-chart/computations/check_completion_boundary.py --output <new-check-json>
```
