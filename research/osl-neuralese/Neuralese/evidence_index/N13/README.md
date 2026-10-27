# Komorebi Recurrent-Depth Lab

This package turns the proposed connection between Komorebi Math and *Scaling
up Test-Time Compute with Latent Reasoning: A Recurrent Depth Approach* into a
falsifiable test.

The short verdict is: **the connection is structurally strong, but not yet a
validated identification**. Recurrent depth gives a discrete dynamical system;
Koopman or tangent lifting gives an exact packet-path expansion; cyclic caches
give a finite residue-address quotient. The major scientific claim would be
that a compact packet system remains low-leakage, stable, and causally useful on
held-out Huginn trajectories. This lab is designed to distinguish those levels.

Paper: [arXiv 2502.05171](https://arxiv.org/abs/2502.05171) · implementation:
[recurrent-pretraining](https://github.com/seal-rg/recurrent-pretraining) · pinned
model snapshot:
[Huginn revision bb6621b](https://huggingface.co/tomg-group-umd/huginn-0125/tree/bb6621b65e90b6a4b9b29ef88dc83866d450470c)

## What is already verified

The NumPy suite contains known-ground-truth systems and currently passes every
required gate:

| Gate | What it prevents |
|---|---|
| Contracting fixed point | Mistaking small motion for convergence |
| Exact period-7 orbit | Calling a PCA loop an orbit without a full-space return |
| Jordan slider | Treating unit eigenvalues alone as proof of drift |
| Mixed `C → O → S` lanes | Hand-waving the packet path-power identity |
| Affine and polynomial lifts | Omitting the constant observable |
| Held-out leakage control | Treating training fit as Koopman closure |
| Excitation control | Claiming an unobserved lane was recovered |
| Modulo-cache selector | Confusing overwrite with residue sum or average |
| Certified stopping | Using successive KL or a tiny step as a convergence proof |
| KM36 bridge | Confirms reconstruction with the existing Komorebi core |

The included reference report is `outputs/synthetic_summary.json`.

## Quick start on Windows 11

Extract the package, open PowerShell in this directory, and run:

```powershell
conda activate komorebi-full
python .\scripts\run_synthetic.py
```

To cross-check through an existing KM36 checkout:

```powershell
python .\scripts\run_synthetic.py --komorebi-src "C:\path\to\KM36\komorebi-math\src"
```

Or set the path once and use the wrapper:

```powershell
$env:KOMOREBI_MATH_SRC="C:\path\to\KM36\komorebi-math\src"; .\run_all.ps1
```

NumPy is the only required dependency. For editable imports and the unit suite:

```powershell
python -m pip install -e ".[test]"; python -m pytest -q
```

## Staged real-model test

Do not begin with a claim about semantic packets. Advance through the stages in
order:

1. **Adapter validity:** reproduce manual recurrent stepping with Huginn's own
   forward path at depths 1, 2, and 4.
2. **Paper replication:** test convergence, orbit candidates, sliders, and seed
   robustness in the original latent metric; use PCA only as a chart.
3. **Held-out closure:** fit packet bases on discovery prompts and measure
   one-step and multistep leakage on unseen prompts and seeds.
4. **Causal transport:** intervene on a packet and beat rank- and energy-matched
   random-subspace controls.
5. **Refinement:** test nested projectors and compatibility maps. Recurrence
   depth by itself is path length, not a Komorebi refinement scale.

The complete preregistration is in `EXPERIMENT_PROTOCOL.md`; the mathematical
bridge is in `THEOREM_OUTLINE.md`; claim boundaries are in
`CLAIMS_AND_LIMITS.md`.

`VERIFICATION.md` records exactly what was executed in this build and what still
requires the actual checkpoint and GPU.

### Capture a short trajectory

The capture script is offline-first: without `--allow-download`, it only uses a
locally cached pinned snapshot. It uses the model's public
`embed_inputs → initialize_state → iterate_one_step → predict_from_latents`
interface and disables test-time noise.

```powershell
python -m pip install -e ".[huginn,quant]"
python .\scripts\capture_huginn.py --prompt-id D01_PAPER_MATH --steps 8 --seed 0 --quantization 4bit
```

The lab pins Transformers 4.57.6. Huginn's pinned remote model code uses the
Transformers 4.x tied-weight metadata contract and fails during model
construction under Transformers 5.x. If lab v0.1.0 installed Transformers 5,
downgrade it once and retry from the existing cache:

```powershell
python -m pip install --upgrade "transformers==4.57.6"
python .\scripts\capture_huginn.py --prompt-id D01_PAPER_MATH --steps 8 --seed 0 --quantization 4bit
```

The second command deliberately omits `--allow-download`: the completed model
snapshot is reused. Lab v0.1.1 also checks this compatibility before attempting
any checkpoint download.

If the snapshot is not cached, review the pinned remote code and then opt in:

```powershell
python .\scripts\capture_huginn.py --prompt-id D01_PAPER_MATH --steps 8 --seed 0 --quantization 4bit --allow-download
```

Analyze the resulting NPZ:

```powershell
python .\scripts\analyze_trajectory.py .\outputs\huginn\D01_PAPER_MATH_seed0_depth8.npz --plot .\outputs\huginn\D01_PAPER_MATH_seed0_depth8.png
```

For an RTX 3070 Ti with 8 GB, ordinary BF16 loading is borderline. Pilot with
4-bit NF4 only if `bitsandbytes` works with the pinned remote code, keep the
recurrent core on GPU, and treat the trajectory as belonging to the quantized
model. Any spectral or causal result intended as a Huginn claim should be
repeated on representative prompts in BF16 with CPU offload or a larger GPU.

```powershell
python .\scripts\capture_huginn.py --prompt-id D01_PAPER_MATH --steps 8 --quantization 4bit --allow-download
```

## Result ladder

Report one of these outcomes—do not collapse them into a single yes/no label:

1. **Visual resemblance only:** PCA shapes resemble fixed points, loops, or
   sliders.
2. **Reproducible modes:** full-space diagnostics survive seeds and controls.
3. **Reusable packets:** a discovery-fit finite lift has low held-out leakage.
4. **Causal Komorebi-style transport:** packet interventions predictably alter
   computation and beat matched random bases.

Only level 4 would support the proposed major tie strongly. Levels 1–3 are still
useful findings, but they are progressively weaker claims.

## Package map

```text
src/krd_lab/analysis.py       finite charts, DMD, packets, cache, certificates
src/krd_lab/synthetic.py      known-ground-truth recurrent systems
src/krd_lab/komorebi_bridge.py optional KM36 PacketSystem cross-check
scripts/run_synthetic.py      acceptance runner and JSON report
scripts/capture_huginn.py     pinned, offline-first Huginn trajectory adapter
scripts/analyze_trajectory.py finite-trajectory diagnostics
tests/test_synthetic.py       independent exact and negative-control tests
configs/prompt_suite.json     safe discovery/held-out prompt starter set
```

## Nonclaims

- Initialization endpoint collapse is not automatically chart-path
  independence or holonomy.
- Complex DMD eigenvalues are not proof of a true periodic orbit.
- EDMD/DMD residuals on sampled trajectories are not global operator-norm
  leakage certificates.
- A modulo cache is stateful. Cache contents and recurrence phase must be part
  of the autonomous state before applying Koopman analysis.
- A spectral radius below one is not a Euclidean contraction certificate for a
  nonnormal operator.
