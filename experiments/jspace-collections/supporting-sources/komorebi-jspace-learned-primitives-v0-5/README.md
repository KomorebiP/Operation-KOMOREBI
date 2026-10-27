# J-space: learned primitive kernels, v0.5

Author: **Komorebi P.** · 2026-09-05

This release moves one level below the v0.4 expression library. The new executor calls **learned two-input numerical kernels** and composes those calls. It has no named addition, subtraction, multiplication, or power instruction. A learned composition can become a new signal in a named, editable workspace, with fork, amplitude edit, persistence, and undo.

The decisive limitation is architectural: **square-activation neurons plus a learned linear readout suffice for the successful polynomial results.** Training their hidden weights adds no demonstrated benefit. A same-size tanh model approximates multiplication but fails the required precision, especially when composed or used outside its training range. This is supervised learning of primitive behavior inside supplied architectures, not unrestricted discovery of mathematics.

## Run on Windows

Extract the ZIP. Open PowerShell in this folder and run:

```powershell
.\Run_Learned_Primitives.ps1 -Mode demo
.\Run_Learned_Primitives.ps1 -Mode test
.\Run_Learned_Primitives.ps1 -Mode verify
```

The runner creates a local Python environment and installs NumPy if needed. Python 3.10 or later is required. It does not change your PowerShell execution policy. If your policy blocks scripts, run the Python commands below directly. The Python commands were tested on Linux; the PowerShell wrapper was inspected but not executed in a Windows runtime.

```powershell
python -m pip install -r requirements.txt
python demo.py
python -m unittest -v test_primitives.py
python verify_delivery.py
```

The demo forks a learned cubic workspace and adds 0.5 to its signal amplitude. At the two query points, the value, difference, and sum readers change by **4, 3.5, and 4.5**. Undo restores their previous outputs exactly. It saves a demo bank in `examples/demo_workspaces.json`.

## Edit your own copy

```powershell
python cli.py --bank my_workspaces.json init
python cli.py --bank my_workspaces.json fork rule_0 trial
python cli.py --bank my_workspaces.json read trial 2 1 --other 1 0
python cli.py --bank my_workspaces.json edit-amplitude trial 0.5
python cli.py --bank my_workspaces.json read trial 2 1 --other 1 0
python cli.py --bank my_workspaces.json undo trial
python cli.py primitive channel_42 3 4
```

`init` refuses to overwrite an existing file. `list` lists the workspaces and current revisions. A bank is bound to the exact core and primitive checkpoints that give its expressions meaning. Loading it with changed kernels requires an explicit migration; the loader rejects silent substitution.

This v0.5 interface edits the amplitude of an installed expression. The earlier v0.4 release has the richer point-lock and constraint editor; that full editor has not been ported to learned kernels here.

## Main results

- Nine cubic/quartic functions composed from learned calls pass at absolute error ≤ 10⁻⁶, across three kernel seeds, on both ordinary and larger inputs.
- All 144 synthetic workspace tasks pass for each of those three seeds. These are **144 tasks repeated with three initializations**, not 432 independent tasks.
- The original integration run supplied the correct library entry. A separately labeled post-score follow-up now selects it from demonstrations alone and reconstructs all 432 states exactly. It rejects insufficient, unsupported, or ambiguous admissions. This uses the same tasks, not a fresh benchmark.
- Untrained and shuffled-label controls fail. Random square features with a learned readout match the successful trained-square result.
- `max` is rejected by the strict validation gate; the architecture has not learned a sufficiently precise nonpolynomial primitive.
- Ten semantic/gradient tests pass. All 1,170,432 saved prediction values replay exactly in the tested runtime. Eleven live CLI commands pass, including rejected edits and persistence.

See `RESULTS.md` for matched comparisons and failures, and `DESIGN.md` for the boundary between supplied structure and learned behavior. This release makes **no ARC performance claim**.

To infer which learned signal fits your demonstrations, use a JSON file with `xy` (pairs of input coordinates) and `observations` (scalar outputs). The included example contains demonstration data only:

```powershell
python admit_workspace.py --bank my_workspaces.json --name inferred_rule --demonstrations examples/admission_demonstrations.json
python audit_admission.py
```

The admission function checks all nine learned expressions. It writes the bank only for a unique fit within that library; this is not proof of a globally unique rule. Its supplied workspace form remains a quadratic base plus one learned signal.

## Reproduce the experiment

From the extracted project directory:

```powershell
python run_experiment.py all --output rerun_results
```

Alternatively, run the stages separately with the same output folder: `train`, `predict`, then `score`. The Windows runner's `-Mode retrain` creates a timestamped output folder. Use a new folder to preserve the shipped frozen results. Training uses three seeds, two activation families, and a shuffled-label control; it needs NumPy and CPU, with no GPU dependency.

The exact-replay audit compares the delivered checkpoints and saved predictions. Cross-platform floating-point implementations may differ in their last bits; the scientific success threshold is 10⁻⁶. If an exact replay differs, inspect the reported numeric error rather than treating bitwise identity as the scientific criterion.

## Package map

| File | Purpose |
|---|---|
| `primitive_environment.py` | Supplied operation observations and synthetic scoring oracles |
| `primitive_model.py` | Trainable kernels, controls, checkpoint identity, acceptance gate |
| `executor.py` | Ordered composition of validated neural calls |
| `primitive_workspace.py` | Legacy core plus a new learned signal, revisions and persistence |
| `run_experiment.py` | Training, frozen prediction generation, separate scoring |
| `law_probes.py` | Finite empirical checks of supplied algebraic-law templates |
| `inspect_learned_laws.py` | Read-only expansion of square-network weights into polynomial coefficients |
| `results/` | All 27 model checkpoints, observations, catalogs, traces, programs, predictions and scores |
| `baseline/` | Frozen old core, geometry and original snapshots required to run this release |
| `cli.py`, `demo.py` | Runnable editable workspace interface |
| `verify_delivery.py` | Frozen-file checks, full numeric replay and live CLI audit |
| `admit_workspace.py`, `audit_admission.py` | Post-score follow-up selecting a signal from demonstrations without a family index |
| `export_explorer_data.py` | Actual learned weights and 720 reference probes for interactive inspection |

All necessary executable dependencies from the prior workspace are included. Earlier complete releases remain separate; this ZIP does not repeat their entire historical archives.
