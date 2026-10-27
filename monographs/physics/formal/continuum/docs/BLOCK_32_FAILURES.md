# Block 32 failure and repair ledger

## Mathematical development failures

1. **Treating the full walk as a single directional estimate.**
   This loses the repeated-factor multiplicities. The repaired proof expands
   the physical order `M-X-Y-Z-Y-X-M`, producing `2δx + 2δy + δz`.

2. **Mixing the edge and curvature channels.**
   A curvature-only estimate would contradict the checked flat-but-edge-wrong
   witness. The final theorem uses a two-stage defect and retains two additive
   budgets.

3. **Using scalar phase defects only on one spinor fiber.**
   The final source lifts uniform phase transport and all five path swaps to the
   same finite Hilbert state used by the complete walk.

## Verification and environment failures

1. A command used `lake build -j 1`; this Lake version does not accept `-j` in
   that position. It failed immediately and supplied no proof evidence.

2. A one-worker monolithic cumulative build reached the terminal portion of the
   project but exceeded the external command window without a success receipt.
   It is classified as inconclusive and excluded.

3. A parallel monolithic cumulative-build retry also reached the terminal
   portion but exceeded the external command window without a success receipt.
   It is also excluded.

The accepted verification mode is modular cumulative verification: the 130
v0.31 parent modules are byte-identical, the complete Block 32 import closure
is rebuilt, the new source and API compile with warnings as errors, all 40 new
declarations are axiom-audited, and all three negative controls are rejected.
