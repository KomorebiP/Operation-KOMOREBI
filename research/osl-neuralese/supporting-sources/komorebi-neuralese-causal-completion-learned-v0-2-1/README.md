# Komorebi Neuralese Causal Completion — learned checkpoints v0.2.1

This package audits six frozen learned checkpoints without retraining. Start with `RESULTS_SUMMARY.md` for the scientific synthesis and `CLAIM_BOUNDARY.md` for the exact limits.

## Main result

The projective checkpoints implement a strong finite hard-decision D4 action on ordinary reachable histories, but repeated identity loops reveal a noncontracting, history-dependent microstate. The system is locally behaviorally closed and globally incomplete over longer adversarial histories.

## Run

Python 3.10+ and NumPy are sufficient; PyTorch is not required.

```powershell
python -m pip install -r requirements.txt
python -m unittest -v test_probe.py
python run_probe.py
python posthoc_numeric_mechanism.py
```

`python run_probe.py --quick` runs a smaller development profile. The registered run takes roughly 30–40 seconds in the reference environment.

## Important files

- `PREREGISTRATION.json` — frozen adaptive-developmental gate specification
- `run_probe.py` — learned-checkpoint causal-completion audit
- `posthoc_numeric_mechanism.py` — clearly separated post-hoc spectral, underflow, and task-support analysis
- `checkpoint_io.py` — restricted NumPy checkpoint reader
- `core.py` — D4 environment and projective diagnostics
- `test_probe.py` — 11 unit and replay tests
- `results/RESULTS.json` — complete registered machine-readable result
- `results/REPORT.md` — report generated directly by the registered runner
- `results/POSTHOC_NUMERIC_MECHANISM.json` — radial and support supplement
- `results/development_v0.2.0/` — preserved failed first smoke

The manifest can be checked with `python verify_manifest.py`.
