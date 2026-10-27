# Komorebi Neuralese Completion Surface v0.3.0

This archive contains a preregistered adaptive-developmental audit of two
frozen projective D4 checkpoints. It tests the two-index causal refinement
surface over history depth `L <= 8` and future horizon `H <= 8`, keeps hard and
soft predictive interfaces separate, audits the diagonal maps between adjacent
quotients, and probes repeated algebraic identity words through total observed
history depth 70.

Start with `RESULTS_SUMMARY.md` for the result and `CLAIM_BOUNDARY.md` for the
scientific limits.

## Main result

The strict registered verdict is mixed, not an omnibus pass:

| Gate | Verdict |
|---|---|
| `E0_execution_integrity` | PASS |
| `H0_hard_rectangle` | FAIL |
| `H1_downset` | PASS |
| `S0_soft_exact_collapse` | FAIL |
| `D0_diagonal_action` | FAIL |
| `W0_relator_hard_closure` | FAIL |
| `W1_relator_soft_flatness` | FAIL |
| `C0_nonidentity_control` | FAIL |

The failure pattern is informative. Checkpoint seed 0 has one depth-zero
anchor error, but every ordinary exact history shell after at least one
generator application is perfectly hard-correct through `H=8` for both
checkpoints: 33,358,080 of 33,358,080 decisions. The soft predictive state
does not collapse by semantic label, and repeated identity paths eventually
cross hard decision boundaries. The earliest registered hard loop witness is
at total observed history depth 38 and is first revealed by a suffix of length
3.

The compact interpretation is:

\[
\text{entry transient}
\longrightarrow
\text{metastable hard decision-cone code}
\longrightarrow
\text{margin-crossing path drift}.
\]

## Verify

Python 3.10+ and NumPy are sufficient; PyTorch is not required.

```bash
python -m pip install -r requirements.txt
python verify_manifest.py
```

The verifier checks the release manifest, all twelve pre-endpoint frozen
digests, the fixed registered-result digest, result-to-summary binding,
finite JSON numerics, headline counts, independently recomputed gate
conjunctions, and all 19 structural tests.

## Reproduce

The registered result is already included. To replay it without overwriting
the preserved result, choose a new output filename:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  python run_completion_surface.py \
  --output results/REPLAY_RESULTS.json
```

The reference run took 145.1 seconds; runtime is hardware-dependent. The
runner validates the execution freeze before loading a learned endpoint,
refuses to overwrite an existing output, and marks altered scientific
profiles as unregistered. `summarize_results.py` is a post-hoc, read-only
analysis of the registered source result, although it rewrites the compact
summary files; run it only in a working copy if preserving manifest validity.

## Contents

- `PREREGISTRATION.json` — registered hypotheses, tolerances, gates, and claim rules
- `EXECUTION_FREEZE.json` — twelve scientific-source and checkpoint digests fixed before endpoint inspection
- `RESEARCH_SPEC.md` — mathematical and computational specification
- `run_completion_surface.py` — registered exact surface runner
- `relator_witness.py` — repeated-identity and matched-control audit
- `soft_surface.py` — probability and centered-logit interfaces
- `test_completion_surface.py` — 19 structural and oracle tests
- `results/COMPLETION_SURFACE_RESULTS.json` — complete registered machine-readable result
- `results/POSTHOC_SUMMARY.json` — compact source-bound synthesis
- `RESULTS_SUMMARY.md` — human-readable result
- `CLAIM_BOUNDARY.md` — supported and excluded claims
- `RUN_COMPLETE.json` — execution and independent-integrity receipt
- `MANIFEST.json`, `SHA256SUMS.txt` — release integrity records

## Status

This is an adaptive developmental follow-up on two fixed checkpoints and a
finite reconstructed task family. It is not a confirmatory population study
and does not concern frontier language models.
