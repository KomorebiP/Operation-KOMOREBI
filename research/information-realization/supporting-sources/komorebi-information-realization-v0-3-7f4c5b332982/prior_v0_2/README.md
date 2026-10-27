# Komorebi Information Realization v0.2.0

An exact finite research companion for representations, recovery, information loss, and admissible repair. This release audits and preserves the supplied v0.1 rather than silently replacing its provenance.

## Run

Python 3.10 or later is required. The mathematical code and tests use only the standard library. No network access or installation is needed.

From this folder:

```powershell
python tests/run_audit.py --suite all
python examples/worked_examples.py
```

For an optimized-interpreter regression check:

```powershell
python -O tests/run_audit.py --suite all
```

Each suite writes a separate JSON report and exits nonzero on failure. No checks rely on Python `assert`, which disappears under `-O`. Runtime depends on the machine. The current execution environment used Python 3.13.5. Figures are optional and require matplotlib; none of the mathematical tests require it.

## Read

Start with `AUDIT_REPORT.md`, then `WORKED_EXAMPLES.md`. General statements and proofs are in `THEORY.md`. `PROGRESS_LEDGER.md` records the next restart point. `reports/` contains actual outputs, not proposed test counts. `baseline/` preserves the original mathematical note and Python probe.

The main API is `src/information.py`. Examples of its use:

```python
import sys
sys.path.insert(0, 'src')
from information import FiniteModel

# Two observed classes, each hiding two task labels.
m = FiniteModel((0, 0, 1, 1), ('a', 'b', 'c', 'd'), (3, 1, 3, 1))
print(m.profile())
print(m.optimal_success(1))  # 3/4, no informative extra message
print(m.optimal_success(2))  # 1, one supplemental bit suffices
code, decoder = m.exact_repair()
print(code)
print(decoder)
```

## Contracts

States are indexed by their row positions. Observation and target values must be hashable. Weights are exact nonnegative integers; they are normalized internally. Floats are deliberately rejected by the exact probability constructor. Zero-probability states remain part of structural recovery unless `support_only=True` is explicitly selected.

The least repair alphabet assumes the encoder can inspect the state, or at least observation and task. It is not a method to regenerate erased information from an inadequate observation. The constrained-encoder example shows why this matters.

Prime-field matrix operations are included for the linear obstruction bridge. Finite extension-field arithmetic, numerical conditioning analysis beyond a counterexample, and integration into the larger Komorebi libraries are not implemented.

## Verification status

The supplied v0.1 results were reproduced. Three implementation issues were found and corrected in v0.2. Exact finite tests, independent decoder and encoder searches, Markov-channel checks, linear-algebra comparisons, dynamics checks, and adverse examples passed. The general proofs are written mathematical arguments. Lean and Lake were not available in the checked runtime, and no Lean compilation was performed.

This is not a claim of a completed universal information theory or a novelty certification.
