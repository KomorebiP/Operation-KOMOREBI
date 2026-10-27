# v0.4 learned-checkpoint causal-completion probe

Author: Komorebi P.  
Version: 0.1.0

This is a standalone, posthoc audit of the twelve official sealed checkpoints
in `Komorebi_Neuralese_Packet_Closure_v0.4.0`. It implements the frozen
`ANALYSIS_PROTOCOL.md` in the parent directory. It does not retrain a model and
does not repair or supersede the original v0.4 gates.

Run with the designated interpreter:

```text
/workspace/scratch/e8fe53ed30d5/learned_archive_retry/.venv/bin/python -m unittest -v test_v04_probe.py
/workspace/scratch/e8fe53ed30d5/learned_archive_retry/.venv/bin/python run_v04_probe.py
```

The script verifies the source archive and all checkpoint SHA-256 receipts,
uses only strict `weights_only=True` checkpoint loads, constructs one shared
bank of 32 deterministic unique D4 coordinate contexts, and writes the full
machine-readable output to `RESULTS.json`.

The rank ladder is computed in recurrence-metric whitened coordinates. Each
matrix-product block is Frobenius-rescaled before stacking. The centered-logit
decoder removes the common-logit direction. Rank sensitivity is retained at
relative tolerances `1e-2`, `1e-3`, `1e-4`, and `1e-6`.

Checkpoint tensors, operator encoding, anchor normalization, and the hard-polar
SVD remain on the sealed model's float32 path. Only the extracted recurrence
matrices, normalized anchors, decoder, and metric are promoted to float64 for
the subsequent rank and geometry calculations. This avoids silently making
the hard-polar recurrence more exact than the checkpoint implementation.

Instantaneous-null perturbations use magnitude `0.10` in whitened coordinates
and both signs of each inferred direction. The typed-loop audit uses oriented
positive rays, so antipodes have angle pi. Its future-behavior tensor averages
over all 32 contexts and all eight shortest D4 continuations. Its canonical
centered-logit tensor averages signed, context-canonicalized direction changes
over contexts, prefixes, and continuations. An RMS companion is retained to
prevent signed cancellation from hiding a defect.

In addition to the pooled `8 x 3 x 8` future-behavior tensor, `RESULTS.json`
retains the continuation-averaged tensor separately for each context with
shape `32 x 8 x 3 x 8`. It also retains per-context signed and RMS canonical
centered-logit tensors with shape `32 x 8 x 3 x 8` before pooling contexts.

The exact control compiles each visible D4 action as
`B P B^+ + (I - B B^+)` in the whitened anchor chart. It tests the full
estimator, including coordinate conjugation and slot swapping.
The control gate requires a negligible full-ambient relator residual, unit
behavioral congruence, and unit joint correctness under the `B^+` oracle
decoder. Learned-decoder anchor accuracy is retained descriptively, rather
than letting an unrelated decoder miss invalidate the algebra estimator.
