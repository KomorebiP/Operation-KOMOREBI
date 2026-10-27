# Finite release verification: SF-DISCOVERY-100

`run_release.py` runs all ten frozen scripts sequentially with assertions enabled. It preserves full JSON reports and stdout/stderr for every script. It executes byte-identical copies of the scripts, API, target contract and mathematical notes in a minimal snapshot tree. This redirects scripts whose report destination depends on `__file__` and preserves the existing author reports. The four stdout-only base scripts and three explicit-output scripts also receive full JSON reports in the run's `reports/` directory.

The computational input set consists of 25 files listed in `evidence/release_contract.json`: ten check scripts, `family_lab.py`, the target contract, ten mathematical notes, this README, the aggregate driver and its contract. The monograph and figure builders are outside this input set. The manifest pins all inputs before and after execution and hashes every declared result. `input_hashes.json` also verifies byte identity and unchanged snapshots. Python and mpmath versions are recorded; the external mpmath Python source tree is hashed before and after the run.

## Assertion accounting

| Check | Principal exact | Supplemental exact helpers | Numerical statements |
|---|---:|---:|---:|
| nonlinear dilation | 1,218 | 0 | 0 |
| asymmetric dilation | 1,811 | 0 | 0 |
| complex depth | 301 | 0 | 3 |
| orbit zeta | 138 | 0 | 0 |
| arithmetic polynomials | 0 | 0 | 2,273 |
| dilation type | 6,091 | 0 | 0 |
| arithmetic inverse | 304 | 540 | 88 |
| multi-prime sieve | 1,019 | 0 | 3,182 |
| spectral continuation | 411 | 0 | 30 |
| family API | 8,038 | 0 | 0 |
| **Total** | **19,331** | **540** | **5,576** |

The actual exact total is **19,871 assertion statements**. Inverse reconstruction visits 180 atoms and checks an exact square root, an integral inverse power and an exact integer root for each atom. Its script counter reports only the 304 principal assertions; these 540 helpers are retained separately. Numerical counts count each successful assertion statement once. An `all(...)` positivity group, a compound positivity condition, or a maximum-residual comparison counts once. Sieve orthogonality and recurrence counters are subsets of its numerical total and are not added again. Its finite iteration guard is recorded separately as operational bookkeeping. Decimal display tables and inverse rank estimates are not numerical assertions.

The full reports and the contract state the finite parameter grids, degrees, truncation bounds and precisions. The spectral run includes 16 classical continuation benchmarks, four derivatives at zero, six N=3/N=5 precision comparisons and four shifted N=2 product benchmarks. The family API suite includes the two input-validation regressions added before the freeze.

## Reproduce

Use Python without `-O`. In this workspace the dependency directory is `/workspace/scratch/de82c13900d1/special_work/verification_dependencies`. The computation-audit runner belongs to Mathbox 3.2.0; its path and SHA-256 are recorded in the contract. Set a fresh project-relative run name, since existing evidence is never overwritten. From the project root:

```python
import json, os, subprocess, sys
from pathlib import Path

root = Path.cwd()
run = "evidence/release-run-002"  # release-run-001 is the preserved release run
deps = Path("/workspace/scratch/de82c13900d1/special_work/verification_dependencies")
tool_dir = Path("/root/.codex/plugins/cache/openai-curated-remote/mathbox/3.2.0/skills/computation-audit/scripts")
contract = json.loads((root / "evidence/release_contract.json").read_text())
checks = list(contract["expected_assertion_counts"])
snapshots = contract["mathematics"]["inputs"]
results = [f"{run}/summary.json", f"{run}/input_hashes.json"]
results += [f"{run}/reports/{name}.json" for name in checks]
results += [f"{run}/logs/{name}.{stream}.txt"
            for name in checks for stream in ("stdout", "stderr")]
results += [f"{run}/snapshot/{name}" for name in snapshots]
results += [f"{run}/snapshot/evidence/{name}" for name in (
    "arithmetic_polynomial_checks.json", "spectral_continuation_checks.json",
    "family_lab_checks.json")]
argv = [sys.executable, str(tool_dir / "run_experiment.py"),
        "--root", str(root), "--contract", str(root / "evidence/release_contract.json"),
        "--output", run, "--timeout", "600", "--max-output-bytes", "8388608",
        "--max-memory-bytes", "2147483648", "--max-cpu-seconds", "300",
        "--max-cores", "1", "--max-threads", "1"]
for name in contract["execution_artifacts"]:
    argv += ["--input", name]
for name in results:
    argv += ["--result", name]
argv += ["--", sys.executable, "checks/run_release.py", "--output-dir", run,
         "--dependencies", str(deps), "--script-timeout", "300"]
env = os.environ.copy()
env.pop("PYTHONOPTIMIZE", None)
env["PYTHONDONTWRITEBYTECODE"] = "1"
subprocess.run(argv, cwd=root, env=env, check=True)
subprocess.run([sys.executable, str(tool_dir / "validate_manifest.py"),
                str(root / run / "manifest.json"), "--root", str(root)], check=True)
```

The runner enforces a 600-second wall limit, 2 GiB address-space limit, 300 CPU seconds, one core and cooperative one-thread settings. CPU time and address space are per process, not aggregate budgets over descendants. Child scripts inherit those restrictions and also have a 300-second wall timeout. The runner caps its captured aggregate log at 8 MiB; the driver checks a 4 MiB per-script report bound.

## Interpretation and failure history

Passing these bounded checks supports the stated finite identities and examples. It does not prove the universal analytic theorems, historical priority, or analytic formalization. Ordinary mpmath comparisons at the declared precisions are not interval or ball arithmetic certificates. Resource limits and a successful exit do not validate mathematical interpretation.

Full reports retain their embedded author history. The arithmetic-polynomial history records an earlier failed absolute determinant-residual criterion and the successful correction to a scale-normalized residual. The inverse report records a failed primary-page retrieval and its authenticated substitute. These are prior author events, separate from current release failures; current failures appear in the aggregate summary and manifest, without removing earlier records.

The release manifest is `evidence/release-run-001/manifest.json`; the package-level result and validator status are in `evidence/release_summary.json` and `evidence/release_summary.md`. Revalidate the manifest against the current project before interpreting it as current evidence.
