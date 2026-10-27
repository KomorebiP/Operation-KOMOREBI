# API map

## `Direction`

One primitive direction with a name, parameter, cost, family, resolution, and metadata.

## `DeformationSystem`

Required methods:

- `directions(state, depth)`
- `apply(state, direction)`
- `canonical_key(state)`

Optional methods:

- `validate(state)`
- `invariants(state)`
- `serialize_state(state)`
- `distance(left, right)`

## `PerturbationForest`

Stores raw paths and relation-reduced endpoints together.

Primary calls:

- `explore(config)`
- `raw_counts()`
- `quotient_counts()`
- `new_node_counts()`
- `shortest_path_labels(node_id)`
- `summary()`
- `export(directory)`

## `ExplorationConfig`

Controls depth, path, node, edge, strategy, invalid-state handling, and local direction limits.

## `IntervalDirectionFamily`

Creates exact dyadic nets of a compact interval and returns the associated cover radius.

## `follow_branch`

Evaluates one selected route to a declared depth.

## `InteractionRule` and `generate_interactions`

Generate a finite prefix of multi-input operations.

## `FamilyCertificate`

Stores closure and relation verification for a generated family.

## Metrics

- `branching_entropy`
- `growth_series`
- `weighted_partition_function`
- `geometric_tree_partition`
- `propagated_cover_error`

## Extended exact example systems

Version 1.1.0 also exports:

- `SequenceTransformSystem`
- `GaussianFamilySystem`
- `QubitGateSystem`
- `MatrixDeformationSystem`
- `AffineShapeSystem`
- `GraphDeformationSystem`
- `CongruenceLiftSystem`

These systems are reference realizations, not assumptions built into the abstract calculus.

## Visual atlas

`visual_atlas.py` generates the 20 vector-PDF and PNG figures used by the manuscript. The experiment driver creates the underlying forests before rendering, so figure labels and counts are derived from the recorded objects rather than inserted manually.

## Command-line examples

The `explore` command accepts `walk`, `dyadic`, `polynomial`, `analytic`, `sequence`, `gaussian`, `qubit`, `matrix`, `shape`, `graph`, `adic-simple`, and `adic-singular`. Every run exports `forest.json`, `nodes.csv`, and `edges.csv`.
