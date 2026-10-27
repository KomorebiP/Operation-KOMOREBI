# Rank-aware execution copy

This file is a separate working copy of the preserved unknown-edge script.
`REPAIR.diff` and `REPAIR_PROVENANCE.json` describe the complete change.

The background projector uses an SVD numerical-rank basis. Its threshold is
`eps(float64) * max(B.shape) * largest_singular_value`. Dependent background
columns therefore do not cause extra QR directions to be projected away.
The restricted separation function returns zero when a support has more
columns than observation rows, because that coefficient map has a kernel.

The original documented full-rank example retains its support, reconstruction
and separation value. Sixteen bounded regression controls are stored separately
under the current verification index. This numerical repair does not certify
exact arithmetic rank or guarantee stability for nearly singular matrices.

The theorem's zero-edge case remains a separate trivial mathematical branch.
The `EdgeModel` constructor and native recovery API are for nonconstant packets
with at least two nonzero jumps. This copy does not add a zero-edge wrapper.

For a full inherited scientific rebuild into a new output area:

```bash
python execution/unknown_edge/universal_unknown_edge_recovery.py --out new_unknown_edge_output
```

Install `requirements-verification.txt` first. The inherited plotting and
benchmark driver is included unchanged apart from the two documented repairs.
