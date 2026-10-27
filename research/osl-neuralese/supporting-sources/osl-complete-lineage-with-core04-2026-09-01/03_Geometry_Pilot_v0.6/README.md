# OSL Emergent Operator Geometry Pilot v0.6

This package tests whether provenance-sensitive operator structure can arise when a small recurrent model is trained only on generated natural-language stories and questions.

## Result

The pilot found **partial operator-relevant structure**, not a fully emergent OSL-like language.

- Answer-only training generalized above a query-majority baseline and exceeded a TF-IDF baseline on held-out syntax and combined OOD stories.
- Answer-only latents showed weak formal-state alignment and modest equivalent-path retrieval above an untrained network.
- Explicit formal-state supervision produced much stronger alignment.
- Operator-equivalence regularization produced the strongest path-invariant retrieval.
- Random recurrent features and TF-IDF features explained the original linear-probe evidence.
- Untrained recurrent features obtained higher affine transition R² than trained models, invalidating that metric as evidence of learned operators.
- Probe-guided interventions did not produce coherent provenance transformations across logically related queries.

The strongest justified conclusion is therefore:

> Generated sentence pressure can induce task-relevant and partially path-structured latent representations, but this pilot does not show spontaneous formation of a clean, causally manipulable operator-symbolic language.

## Key files

- `EXPERIMENT_PROTOCOL.md`: pre-outcome protocol
- `PREOUTCOME_FREEZE.json`: sealed code, configuration, and holdout seeds
- `results/FINAL_REPORT.md`: human-readable adjudication
- `results/FINAL_ADJUDICATION.json`: compact machine-readable conclusion
- `results/PILOT_ANALYSIS.json`: frozen endpoint analysis
- `results/POSTOUTCOME_CONTROLS.json`: random-feature and lexical controls
- `results/POSTOUTCOME_GEOMETRY_AUDIT.json`: CKA, RSA, and path retrieval
- `results/POSTOUTCOME_INTERVENTION_SWEEP.json`: causal steering audit
- `checkpoints/`: nine trained model checkpoints

## Verification

```bash
./VERIFY_RELEASE.sh
```

## Full reproduction

The full reproduction retrains all nine models and overwrites generated checkpoints and result files:

```bash
./RUN_FULL_PILOT.sh
```

The experiment is deterministic under the tested Python, PyTorch, NumPy, and scikit-learn environment, but bit-identical training across arbitrary BLAS/hardware combinations is not guaranteed.
