# RRCT v0.52 dev3 — Hierarchical Nested Workspace Limited Pilot

## Status

**`V052_LIMITED_NESTED_WORKSPACE_ENDPOINTS_MET`**

All **18 of 18** declared endpoints passed across four fresh held-out seeds.

## Question tested

Can four lower-level agents form two learned local workspaces that then act as effective agents for a smaller global workspace, with both bottom-up causal influence and top-down writeback?

## Architecture

```text
leaf A1 + leaf A2 → local workspace A ┐
                                      ├→ global workspace → top-down writeback → all leaf actions
leaf B1 + leaf B2 → local workspace B ┘
```

The two local workspaces compress 16 dimensions of leaf task code into 5 dimensions each. The global workspace compresses the combined 10 local dimensions into 4 dimensions.

## Exact information structure

For values in `Z_4`:

- `U = (a1 + a2) mod 4`
- `V = (b1 + b2) mod 4`
- `Y = (U + V) mod 4`

Each leaf contains **0 bits** about its local target, while each leaf pair contains **2 bits**. Either local workspace alone contains **0 bits** about `Y`, while the two together contain **2 bits**.

## Main results

| Mode | Local A | Local B | Global | Mean leaf action | Private routine |
|---|---:|---:|---:|---:|---:|
| Global cut | 1.000000 | 1.000000 | 0.250000 | 0.250000 | 1.000000 |
| Intact | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| Leaf A1 cut | 0.250000 | 1.000000 | 0.250000 | 0.237305 | 1.000000 |
| Leaf A2 cut | 0.250000 | 1.000000 | 0.250000 | 0.271973 | 1.000000 |
| Leaf B1 cut | 1.000000 | 0.250000 | 0.250000 | 0.257812 | 1.000000 |
| Leaf B2 cut | 1.000000 | 0.250000 | 0.250000 | 0.262207 | 1.000000 |
| Local A cut | 0.250000 | 1.000000 | 0.250000 | 0.250000 | 1.000000 |
| Local B cut | 1.000000 | 0.250000 | 0.250000 | 0.250000 | 1.000000 |
| Top-down cut | 1.000000 | 1.000000 | 1.000000 | 0.250000 | 1.000000 |


## Decisive dissociations

### Global workspace cut

Both local workspaces remain perfect:

\[
\operatorname{Acc}(U)=\operatorname{Acc}(V)=1,
\]

but global classification and all leaf actions fall to chance:

\[
\operatorname{Acc}(Y)=\operatorname{Acc}(A_i)=0.25.
\]

This shows that the global workspace is causally separable from the two local coalitions.

### Top-down writeback cut

Local and global classifications remain perfect, but all four leaf actions fall to chance. Thus computing a higher-level state is not enough; that state must be written back into lower-level control.

### Upward causal patching

Replacing either local workspace with the corresponding state from another episode changed the global state and all downstream actions coherently with 100% accuracy.

### Downward causal patching

Replacing the global workspace changed all four leaf actions coherently with 100% accuracy while preserving private routines.

## Important limitation

A flat controller with simultaneous access to all four leaf task codes also solved perfectly. The result therefore establishes that a nested architecture is viable and causally decomposable; it does **not** show that nested organization is uniquely necessary or more efficient for this finite task.

Private routines are architecturally separated from the shared task path. Their preservation is a control, not an emergent privacy result.

## Development boundary

An earlier frozen development version passed 16 of 18 endpoints but failed strict off-manifold patch generalization. Its thresholds were not relaxed. The final dev3 model adds predeclared causal-recombination training only to the frozen downstream interface and uses entirely fresh holdout seeds.

## Claim boundary

This is a two-level synthetic existence and causal-dissociation pilot. It does not establish spontaneous coalition formation, dynamic workspace hierarchies, biological realism, brain equivalence, functional awareness, or subjective experience.
