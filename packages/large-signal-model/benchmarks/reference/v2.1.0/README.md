# Projector-Resolved Large Algebraic Signal Model

**PR-LASM** is a finite, executable signal-world model built around exact
multi-atlas coordinates, adaptive packet refinement, a typed Bayesian
operator grammar, explicit memory, deterministic transition graphs, and
active planning.

The repository separates two objects that are often conflated:

1. an exact coordinate archive that retains reconstructible information
2. compressed statistical states used for prediction and planning

The exact archive is never replaced by the learned state.

<p align="center">
  <img src="paper/figures/01_pr_lasm_architecture.png" alt="PR-LASM architecture" width="860">
</p>

## Repository status

| Item | Status |
|---|---|
| Package version | `2.1.0` |
| Supported Python | `3.12` and `3.13` |
| Clean-repository core tests | `32` |
| Optional local-suite tests | `8` additional tests when the 25-environment fixture archive is installed |
| Controlled operator scenarios | `7` |
| Deterministic synthetic interactive systems | `4` |
| Official ARC-AGI-3 score | Not claimed |
| License | All rights reserved |

The reference benchmark output from release 2.0.0 is retained under
[`benchmarks/reference/v2.0.0`](benchmarks/reference/v2.0.0). It records
exact reconstruction checks, controlled mechanism identification, and
deterministic synthetic planning results. New outputs are written to the
ignored `results/` directory.

## Installation

### Editable development install

```powershell
git clone <REPOSITORY_URL>
Set-Location komorebi-pr-lasm
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python -m pytest -q -m "not local_suite"
```

Conda users can instead run:

```powershell
conda env create -f environment.yml
conda activate pr-lasm
python -m pytest -q -m "not local_suite"
```

The unified Windows entry point is:

```powershell
.\pr-lasm.ps1 help
.\pr-lasm.ps1 test
.\pr-lasm.ps1 benchmark
```

Add `-EnvName pr-lasm` to execute a command through `conda run` without
activating the environment.

## First exact-reconstruction example

```python
import numpy as np
from komorebi_pr_lasm import MultiAtlasAnalyzer, MultiAtlasConfig

frame = np.arange(64, dtype=np.int16).reshape(8, 8) % 16
analysis = MultiAtlasAnalyzer(MultiAtlasConfig(haar_levels=3)).analyze(frame)

print(analysis.reconstruction_residuals())
print(np.max(np.abs(analysis.tight_frame_synthesis() - frame)))
```

The complete analysis record contains spatial, unitary Fourier,
orthonormal Haar, phase-2 polyphase, phase-4 polyphase, and categorical
color coordinates.

Run the supplied examples:

```powershell
python examples\exact_reconstruction.py
python examples\adaptive_refinement.py
```

## Mathematical core

For exact atlases `U_a` and positive weights `w_a`, the redundant analysis
and canonical synthesis maps are

```text
A(x) = (w_a U_a x)_a
S((c_a)_a) = [sum_a w_a U_a* c_a] / [sum_a w_a^2]
```

and satisfy `S A = I` in the declared finite setting. Coordinate selectors
pull back to packet projectors

```text
P_(a,alpha) = U_a* E_(a,alpha) U_a.
```

A complete Haar packet tree provides mixed-depth exact prunings. Dynamic
programming chooses a complete antichain under an additive cost, while
synthesis remains exact.

## Typed world model

The learned posterior ranges over

```text
atlas × resolution × operator family × parameters × memory mechanism.
```

The finite grammar includes linear transfer, quadratic interaction,
action-state bilinear transfer, finite delay, power-law memory,
exponential memory, phase-conditioned dynamics, smooth gated regimes, and
nonlinear memory-bearing hybrids. Each candidate has an explicit design
map, complexity, mechanism count, predictive distribution, and posterior
probability.

Exact replay transitions are stored separately in a state-action graph.
The planner combines known graph outcomes, posterior predictions, novelty,
model disagreement, loss risk, progress, role statistics, and repeat
penalties. Replay is disabled after a state-signature mismatch.

## Command-line interface

```powershell
komorebi-pr-lasm benchmark --output results\pr_lasm_benchmark
komorebi-pr-lasm smoke --output results\pr_lasm_smoke
komorebi-pr-lasm run --game <GAME_ID> --environments-dir environment_files
komorebi-pr-lasm suite-run --environments-dir environment_files --order easy
```

`python -m komorebi_pr_lasm` is equivalent to the `komorebi-pr-lasm`
command. The older `komorebi_arc3_offline` namespace remains available for
compatibility with the 2.0.0 handoff.

## Optional ARC-AGI-3 integration

The public repository does **not** commit downloaded ARC environment source
files. Extract the separate local-fixtures archive into the repository root
when you need the 25-environment integration suite:

```powershell
Expand-Archive .\Komorebi_PR_LASM_Local_ARC3_25_Fixtures.zip -DestinationPath . -Force
python -m pytest -q
.\pr-lasm.ps1 suite-audit
```

Those files remain ignored by Git. The adapter is pinned to `arc-agi 0.9.9`
and `arcengine 0.9.3`, forces offline mode, clears the API key, and installs
a process-level network guard. See
[`docs/arc3-integration.md`](docs/arc3-integration.md).

## Repository layout

```text
src/komorebi_pr_lasm/        public project-native API
src/komorebi_arc3_offline/   compatibility implementation namespace
tests/                       core and optional local-suite tests
examples/                    minimal executable examples
docs/                        architecture, claims, development, and release notes
paper/                       canonical PDF, LaTeX, and Python-generated figures
benchmarks/reference/        immutable machine-readable reference outputs
environment_files/           ignored location for user-local ARC environments
scripts/                     figure generation, validation, and historical wrappers
```

## Verification

Core verification:

```powershell
python -m compileall -q src examples
python -m pytest -q -m "not local_suite"
python -m pip wheel . --no-deps --no-build-isolation --wheel-dir dist
```

Full controlled benchmark:

```powershell
python -m komorebi_pr_lasm benchmark --output results\pr_lasm_benchmark
```

GitHub Actions runs the core suite on Windows and Linux under Python 3.12
and 3.13, executes both minimal examples, builds the wheel, installs it into
an isolated target, and publishes the wheel as a workflow artifact.

The current verification ledger is in [`RELEASE_AUDIT.md`](RELEASE_AUDIT.md).
The exact first-push commands and recommended repository settings are in
[`GITHUB_PUBLISHING.md`](GITHUB_PUBLISHING.md).

## Claim boundary

This repository establishes a finite implementation under the transforms,
operator programs, priors, replay assumptions, and benchmark systems
supplied here. It does not establish universal program induction,
universal planner optimality, an official ARC score, AGI, or historical
priority over every related architecture. The strongest defensible
description is:

> A projector-resolved, exact-reconstruction, multi-atlas, fully algebraic
> large signal model with typed Bayesian operator selection and active
> planning.

See [`docs/claim-boundary.md`](docs/claim-boundary.md) for the complete
statement.

## Paper and citation

The canonical manuscript is
[`paper/Projector_Resolved_Large_Algebraic_Signal_Model.pdf`](paper/Projector_Resolved_Large_Algebraic_Signal_Model.pdf).
Editable LaTeX and all figure sources are included. GitHub recognizes the
repository citation metadata in [`CITATION.cff`](CITATION.cff).

## License

Copyright © Komorebi P. All rights reserved. Public visibility does not
grant permission to copy, modify, redistribute, or sublicense the code or
manuscript. See [`LICENSE`](LICENSE). Third-party packages and interfaces
retain their own licenses, as summarized in
[`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).
