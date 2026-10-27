# Parent audit notes: v0.1.1

## v0.3 integrity decisions

- The release is rebased on the clean, independently verified v0.2.0 Library archive.
- Positive projective equivalence uses only strictly positive scale. Negative scalar fits are invalid controls, not gauge.
- Statewise scaling is interpreted only on the anchor section; it is not generalized to arbitrary ambient mixtures.
- Continuation packets are task-relative finite-horizon cells. Construction-bank membership is never counted as independent evidence.
- Packet interiors are full-dimensional in the linear assay, so risk is represented by future-boundary margins rather than a literal smooth tangent/normal split.
- Ordered projective Jacobian products are required because individual spectra cannot exclude nonnormal switched amplification.
- Parent v0.1.1 and v0.2.0 results retain their historical source digests. The v0.3 verifier checks their hashes without pretending they were produced by v0.3 source.

Version 0.1.0 was used as a developmental scaffold. Before retaining its pilot as the primary package result, a code and assay audit identified two issues.

1. Model construction occurred before the per-seed random seed was reset. Runs were deterministic in a fixed arm order, but initialization was order dependent and subset reruns were not seed stable. Version 0.1.1 seeds immediately before model construction.
2. The random hidden-state control inserted an absolute norm-matched random vector. That is a useful off-manifold negative control but is weaker than matching the donor intervention itself. Version 0.1.1 uses a random displacement from the recipient hidden state with the exact donor-minus-recipient displacement norm, and retains the absolute-vector control as a secondary diagnostic.

Version 0.1.1 also applies the D4-fitted cross-seed transport map without refitting to C8, mixed-cycle, and random-permutation episodes.

These changes were made after observing the v0.1.0 developmental output. Therefore v0.1.1 remains a hardened developmental replication, not an outcome-independent confirmatory experiment.

Version 0.2.0 retains that parent package and adds separate stability and projective-training runners. Its own revision history, including the corrected float64 centered-rank calculation, is recorded in `DEVELOPMENT_LOG.md`.
