# Komorebi Large Signal Model

## Projector-Resolved Large Algebraic Signal Model · 2.3.0

PR-LASM is an executable, non-LLM algebraic signal model. It separates a
reconstructible coordinate archive from statistical state, learns coefficients
and weights over a finite typed operator grammar, and provides explicit memory
and planning on controlled interactive systems.

This release also exposes a standalone real-valued signal interface with
polyphase transfer blocks, causal streaming FIR, complete packet refinement,
and versioned source-signal storage. These signal operations do not require an
ARC runtime or a hosted model.

**Status:** Beta / work in progress. The scoped core release has recorded
verification on Linux / Python 3.13.5. Original Komorebi code is available under
the MIT license in `LICENSE`; third-party terms remain as stated in
`THIRD_PARTY_NOTICES.md`. Research and performance claims retain their
recorded finite scope.

## Start here

Install in a separate environment. Do not co-install the separate ARC3 agent
package `komorebi-arc3-offline`, which owns the same compatibility namespace.

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[test]"
python -m komorebi_pr_lasm self-check
python -m pytest -q -m "not local_suite"
```

The dependency installation above may need internet access. An offline install
can use the supplied wheel with `--no-index --no-deps` when compatible NumPy and
SciPy are already installed. The package itself does not download a model.

```powershell
python -m pip install --no-index --no-deps .\dist\komorebi_pr_lasm-2.3.0-py3-none-any.whl
python -m komorebi_pr_lasm self-check
```

In the full handoff, `dist` is beside the `source` directory. Adjust the wheel
path to that location. The source-only archive does not contain `dist`.

## A real signal, not a quantized image

```python
import numpy as np
from komorebi_pr_lasm import analyze_signal, PolyphaseFIR, StreamingFIR

x = np.sin(np.arange(257) * 0.13)
analysis = analyze_signal(x, modulus=4)
print(analysis.reconstruction_residuals())

h = np.array([0.25, 0.5, 0.25])
bank = PolyphaseFIR(h, modulus=4)
y = bank.apply(x)
assert np.allclose(y, np.convolve(x, h))

stream = StreamingFIR(h)
y_stream = np.concatenate([
    stream.process(x[:31]), stream.process(x[31:]), stream.flush()
])
assert np.allclose(y, y_stream)
```

For two-dimensional data, `MultiAtlasAnalyzer` retains the original shape.
Categorical color coordinates are present only for exact integers within the
configured palette. Continuous data is neither rounded nor clipped to create
an allegedly exact color representation.

## What is learned

Atlas transforms, seeded projections and operator families are fixed mechanisms.
Bayesian regression learns numerical coefficients from observed transitions.
Validation data determines weights over the supplied operator candidates.
The final regressions use all supplied training records. Replay memory stores
observed transitions separately. The system does not autonomously invent an
unbounded operator grammar, and this archive contains no pretrained foundation
model checkpoint.

The standalone 1-D signal interface and the frame-based world model are related
components, not a claim that a general time-series forecasting or audio agent
has already been trained. The release guide describes that integration boundary.

## Fresh verification

| Layer | This release |
|---|---:|
| Public core test cases | 184 passed |
| Core plus separately supplied local fixture tests | 192 passed |
| FIR / streaming stress combinations | 2,025 passed |
| Additional irregular-image cases | 160 passed |
| Additional 1-D reconstruction lengths | 160 passed |
| Controlled operator and atlas identification | 35 / 35 across five seeds |
| Deterministic synthetic interactive systems | 4 / 4 |
| Official ARC runtime or score | Not executed or claimed |

These are finite controls, not counts of independent theorems. All source tests
were run with warnings treated as errors. The fixture checks are static and
stubbed integration tests, not execution of official games. Windows and Python
3.12 CI are configured but were not executed in this container.

## Worked examples

Eight examples are exercised in the fresh evidence bundle: exact image
reconstruction, adaptive refinement, continuous signals, explicit polyphase
FIR, streaming, source-signal archives, learned operator identification, and
the finite integer Euler bridge. Run them from the repository after installation.

```powershell
python examples\continuous_signal.py
python examples\polyphase_taps.py
python examples\streaming_signal.py
python examples\operator_identification.py
python examples\euler_signal_bridge.py
```

## Commands

```powershell
python -m komorebi_pr_lasm --version
python -m komorebi_pr_lasm self-check
python -m komorebi_pr_lasm analyze signal.npy --output results\analysis.json
python -m komorebi_pr_lasm benchmark --output results\benchmark
python scripts\stress_release.py --output results\stress
python scripts\build_offline.py --output dist
```

`analyze` accepts real 1-D or 2-D `.npy` and comma-delimited `.csv` files.
Archives use a separate typed Python API. `save_signal_archive` saves source
coordinates and analysis settings, not fitted world-model or agent state.

## Documentation and evidence

The current operational manual is [the release guide](docs/RELEASE_GUIDE.md).
The [migration notes](docs/migration-2.3.md) explain deliberate corrections to
previously accepted invalid inputs. The [audit](RELEASE_AUDIT.md),
[claim boundary](docs/claim-boundary.md), and
[reproduction instructions](REPRODUCIBILITY.md) distinguish fresh results from
historical evidence. The [historical capstone](paper/README.md) is retained
unchanged. It is not a newly revalidated manuscript of every 2.3.0 feature.

The full handoff preserves the recovered signal reconstruction and Euler
companions separately. The older ARC2 diagnostic package is a lineage reference,
not this release's ARC solver, and its score is not transferred to this model.

## License

Copyright Komorebi P. The inherited [license](LICENSE) reserves all rights.
This source handoff is not yet an open-source license grant. Third-party
components retain their own licenses. Nothing has been remotely published.
