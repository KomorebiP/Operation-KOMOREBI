# V0.3 hard-QR learned-checkpoint probe

This is a post-hoc, no-retraining audit of the separate v0.3 Stage A
`hard_correct` lineage. It does not pool v0.3 with the v0.4 packet-closure
lineage.

The probe loads all 12 frozen primary checkpoints, enumerates all 2,080 eligible
D4 coordinate permutations whose two primitive maps are in the frozen test
split, and evaluates all eight starts. These contain 260 unique ordered
observable map pairs, each with the same multiplicity of eight. It reports the
raw-decoder and logit-contrast
observability ranks, hard-QR orthogonality, and the `r4`, `f2`, and `frfr`
identity loops after one and 16 repetitions.

Run from any directory with:

```bash
/workspace/scratch/e8fe53ed30d5/learned_archive_retry/.venv/bin/python /workspace/scratch/e8fe53ed30d5/learned_checkpoint_probe_v0.1.0/v03_probe/probe_v03_hard_qr.py --archive-root /workspace/scratch/e8fe53ed30d5/learned_archive_retry/extracted_v03/Komorebi_Neuralese_Operator_Workspace_v0.3.0 --output /workspace/scratch/e8fe53ed30d5/learned_checkpoint_probe_v0.1.0/v03_probe/RESULTS_v03_hard_qr.json
```

The result is deterministic under the recorded runtime. Its SHA-256 is
`7dd6967d2405153f9f6c7b590d9d51bdd632987c2135797a5733ee1d76e7a5c2`.

Interpretation boundary: the decoder is full rank in every seed, and the
combined controlled-horizon-one observer `[C; C M_r; C M_f]` is full rank in
every tested context after removing the common-logit gauge. Therefore the
tested linear causal quotient has no persistent null fiber. The large 16-loop
errors occur with negligible radial gain, identifying angular holonomy in this
hard-QR model. This is a diagnostic of frozen learned checkpoints, not a
preregistered gate or a general Neuralese claim.
