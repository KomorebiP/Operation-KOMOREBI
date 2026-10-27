# Neuralese Entry–Recurrence Counterfactual Probe v0.3.1-draft

This standalone developmental probe reads the frozen v0.3.0 checkpoints and
episodes without modifying that package. It asks whether the seed-0 depth-zero
failure belongs specifically to the learned entry anchors or persists after
placing each semantic state on the recurrently reached code.

For semantic state `q`, the probe constructs both canonical incoming routes:

```text
incoming_R[q] = normalize(M_R anchor[R^-1(q)])
incoming_F[q] = normalize(M_F anchor[F^-1(q)])
```

It exhausts every binary suffix through `H=8` for all eight states, two
checkpoint seeds, and eight fresh coordinate-resampled D4 episodes per
checkpoint, generated with seeds `940000` and `941000`. This is `196,224`
decisions across the three initialization schemes.

Hard predictions and margins are assessed exactly. Probability,
centered-logit, and positive-ray differences are reported separately and are
not thresholded into a soft-equivalence claim.

## Run

From this directory:

```bash
python -m unittest -v test_entry_recurrence_probe.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python entry_recurrence_probe.py
```

The default source path is the sibling directory
`Komorebi_Neuralese_Completion_Surface_v0.3.0`. An alternate location can be
provided with `--source-package`, but its two source files and two checkpoint
digests must exactly match the v0.3.0 freeze.

The runner refuses to overwrite an existing result unless `--overwrite` is
explicitly supplied. Changing the horizon or episode count marks the output as
an unregistered custom profile.

The runner also refuses to load a learned endpoint until
`EXECUTION_FREEZE.json` binds the preregistration, research specification,
runner, synthetic tests, and registered profile.

## Interpretation limits

The incoming representatives depend on the episode's encoded operator tables.
They are therefore a diagnostic counterfactual, not yet a single deployable
replacement embedding table. A hard pass would isolate an entry-interface
defect over this finite suffix window. It would not prove soft collapse,
unbounded recurrence, held-out table generalization, or a stable causal
quotient.
