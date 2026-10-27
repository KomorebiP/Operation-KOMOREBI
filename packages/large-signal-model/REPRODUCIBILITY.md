# Reproducing the 2.3.0 source release

Fresh verification used Python 3.13.5, NumPy 2.3.5, SciPy 1.17.0 and PyTest 9.0.2
on Linux. Setuptools 82.0.1 built the distributions. The PDF/figure build also
uses Matplotlib, ReportLab and their local rendering dependencies.

## Core tests

Install the wheel or the source into an environment with compatible NumPy and
SciPy. Source development tests additionally require PyTest and Requests.

```powershell
$env:OPENBLAS_NUM_THREADS = "1"
$env:OMP_NUM_THREADS = "1"
python -m pytest -q -m "not local_suite" -W error
python -m komorebi_pr_lasm self-check
python -m komorebi_pr_lasm benchmark --output results\benchmark
python scripts\stress_release.py --output results\stress
```

The public tree runs 184 test cases. The full local run included eight additional
static fixture tests after installing the separately supplied 25-environment
archive. That archive is deliberately not committed to this source repository.
Neither test count represents execution of the official ARC runtime.

The stress script uses seeds 0, 7 and 19 for FIR combinations, with lengths
1, 2, 3, 7, 16, 31, 64, 257 and 1024; residue orders 1, 2, 3, 4 and 7; tap
lengths 1, 2, 3, 8 and 15; and signal amplitudes 1e-9, 1 and 1e6. Its normalized
maximum error divides by max(1, maximum absolute reference output).

The operator sweep uses generator seeds 0, 1, 4, 11 and 23. Each scenario has
120 records, of which 84 are supplied to fit and 36 are reserved for final test.
The model uses 63 of the training records for preliminary coefficient fitting
and 21 for candidate scoring, then refits each candidate on all 84 training rows.
No final test target is supplied to fit. These are in-grammar controls in directly generated typed feature space, not raw-signal inference. The four synthetic game controls also use explicit probe actions and resets, accounted for in the release audit.

## Distribution builds

```powershell
python scripts\build_offline.py --output dist
```

This calls the installed setuptools PEP 517 backend and does not download
anything. Setuptools >=77 is required. A standard connected build can use
`python -m build`. The first attempt to install additional build tools in the
release container failed with DNS resolution errors. The offline backend route
was used successfully instead. The failure log is retained in verification.

The wheel contains the executable package. The source distribution also contains
tests, examples, documentation and evidence selected by MANIFEST.in. The full
handoff additionally preserves the original companion archives. It is not an
all-platform wheelhouse: NumPy and SciPy must already be available for a fully
offline installation.

## Interpretation

Runtime and floating-point last bits can differ across BLAS implementations.
Numerical tolerances, not byte-identical computed floats, define the tests.
Archive source hashes and distributed artifact hashes are exact integrity checks.
Windows and Python 3.12 jobs are configured for subsequent execution; this local
report does not assert that those jobs ran.
