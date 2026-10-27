# Komorebi Neuralese Operator Workspace v0.1.1

This package begins the **causally auditable recurrent latent operator workspace** program. It tests whether a recurrent model can learn to execute episode-specific operators in a compact hidden workspace when every episode is expressed in a newly randomized coordinate system.

The experiment is intentionally finite and exact. It separates four questions that are often conflated:

1. Can a model solve randomly conjugated operator-composition tasks?
2. Does recurrent depth support extrapolation beyond trained composition lengths?
3. Are the internal state and operator codes causally sufficient under controlled replacement?
4. Can the hidden workspace of one independently trained model be transported into another model's coordinates?

## Core task

The training system is the regular action of the dihedral group

\[
D_4=\langle r,f\mid r^4=e,\ f^2=e,\ frfr=e\rangle
\]

on eight states. Every episode independently samples:

- an arbitrary permutation \(\phi\in S_8\) of the state coordinates
- the conjugated actions \(\phi r\phi^{-1}\) and \(\phi f\phi^{-1}\)
- a random swap of the two visible operator slots
- a start state and an operator word

Training uses only composition lengths 1 through 4. Evaluation includes lengths 6, 8, 10, and 12 plus three held-out operator distributions: conjugated \(C_8\), a mixed-cycle system, and independent random permutations.

## Arms

| Arm | Purpose |
|---|---|
| `linear_terminal` | Terminal-only recurrent latent matrix model |
| `linear_relation` | Same model with endpoint relation and hidden-return pressure |
| `gru_terminal` | Unconstrained recurrent comparison |
| `gru_intermediate` | GRU with explicit intermediate-state supervision |
| `one_shot_terminal` | Fixed-canvas nonrecurrent baseline |
| `token_only_terminal` | Negative control that cannot inspect episode-specific tables |

The linear-hypernetwork arm is an **architectural positive bias**, not evidence of spontaneous operator discovery. It learns the coordinate alignment and dynamic latent matrices from terminal supervision, but the model class was deliberately chosen to make an operator representation possible.

## Evidence generated

Each run writes:

- a pre-outcome source digest and preregistration
- per-seed checkpoints and training trajectories
- exact accuracy by length and held-out operator family
- relation and equivalent-path diagnostics
- causal state-transplant results
- causal internal operator-code replacement results
- norm-matched random displacement controls plus zero-state lesions
- cross-seed affine transport fitted on short D4 anchors and stress-tested on D4, C8, mixed-cycle, and random-permutation episodes when two or more seeds are run
- JSONL audit receipts, CSV summaries, figures, and a Markdown report

## Run on Windows PowerShell

Smoke test:

```powershell
$Root="$HOME\Downloads\Komorebi_Neuralese_Operator_Workspace_v0.1.1"; Set-Location $Root; python .\run_experiment.py --profile smoke --output-dir .\results\smoke
```

Development pilot:

```powershell
$Root="$HOME\Downloads\Komorebi_Neuralese_Operator_Workspace_v0.1.1"; Set-Location $Root; python .\run_experiment.py --profile pilot --output-dir .\results\pilot
```

Verification:

```powershell
$Root="$HOME\Downloads\Komorebi_Neuralese_Operator_Workspace_v0.1.1"; Set-Location $Root; python .\verify_package.py
```

The default runs use CPU because these models are small. CUDA is supported with `--device cuda`, but it is not expected to improve the small pilot materially.

## Profiles

- `smoke`: one seed and short optimization, intended only to verify mechanics
- `pilot`: two seeds and the complete developmental comparison
- `confirmatory`: ten seeds, longer optimization, and larger frozen evaluations

A confirmatory run should use a newly frozen package revision and should not reuse pilot outcomes to revise thresholds.

## Main files

- `run_experiment.py`: complete experiment runner
- `src/komorebi_neuralese/algebra.py`: exact finite operator systems
- `src/komorebi_neuralese/data.py`: randomized conjugation episodes
- `src/komorebi_neuralese/models.py`: recurrent and nonrecurrent arms
- `src/komorebi_neuralese/evaluate.py`: behavior, relations, paths, and interventions
- `src/komorebi_neuralese/transport.py`: cross-seed coordinate transport
- `RESEARCH_SPEC.md`: hypotheses and adjudication logic
- `CLAIM_BOUNDARY.md`: strict interpretation limits
