# Audit notes for v0.1.1

Version 0.1.0 was used as a developmental scaffold. Before retaining its pilot as the primary package result, a code and assay audit identified two issues.

1. Model construction occurred before the per-seed random seed was reset. Runs were deterministic in a fixed arm order, but initialization was order dependent and subset reruns were not seed stable. Version 0.1.1 seeds immediately before model construction.
2. The random hidden-state control inserted an absolute norm-matched random vector. That is a useful off-manifold negative control but is weaker than matching the donor intervention itself. Version 0.1.1 uses a random displacement from the recipient hidden state with the exact donor-minus-recipient displacement norm, and retains the absolute-vector control as a secondary diagnostic.

Version 0.1.1 also applies the D4-fitted cross-seed transport map without refitting to C8, mixed-cycle, and random-permutation episodes.

These changes were made after observing the v0.1.0 developmental output. Therefore v0.1.1 remains a hardened developmental replication, not an outcome-independent confirmatory experiment.
