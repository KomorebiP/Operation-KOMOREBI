# RRCT v0.52 dev3 Limited Nested-Workspace Protocol

Four leaf agents form two learned 5-D local workspaces. Those two workspaces feed one learned 4-D global workspace. The global state is written back to both local coalitions before all four leaves act.

For values in `Z_4`:

- `U = (a1 + a2) mod 4`
- `V = (b1 + b2) mod 4`
- `Y = (U + V) mod 4`
- leaf action `i = (x_i + Y) mod 4`

The exhaustive distribution has exact synergy at both levels: each leaf contains zero information about its local target, and either local state alone contains zero information about `Y`; the corresponding pairs contain two bits.

The pilot predeclares 18 endpoints covering intact performance, leaf/local/global cuts, top-down writeback, causal patching upward and downward, private routine preservation, compression, a flat full-access baseline, and absence of valence/self-preservation rewards.

Development seeds: `52011, 52012, 52013, 52014`.

Fresh SHA-256-derived holdout seeds: `392208712, 743448271, 793186123, 445719542`.

The pilot is not a test of spontaneous hierarchy formation or human-brain equivalence. Private routines are architecturally separated from the shared task path. A flat controller with full access is expected to solve, so the result cannot establish unique superiority of the hierarchy.
