# Reproduce the ABC computations

After extracting the source and evidence ZIP, open a shell in the directory containing `paper`, `visual`, and `evidence`. The commands below use that directory as the project root. The original recovered archives are evidence inputs, not working directories. The replay procedure copies mutable verifier inputs into a fresh output directory before running them.

The recorded environment is Python 3.12.14, SymPy 1.14.0, and mpmath 1.3.0. Python 3.10 or later is required by the inherited jet verifier. SymPy and mpmath are required only for the canonical and implementation companions and the CRT regression. The jet replay, independent census and named prime-boundary control have no third-party Python dependency.

Run the following from the extracted project root. It writes a new directory named `abc_computation_reproduction` beside the extracted project. If that directory already exists, choose a new directory name in the first assignment. Existing evidence and archives remain unchanged.

```bash
python3 - <<'PY'
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys

project = Path.cwd().resolve()
area = project / 'evidence' / 'computation'
assert (area / 'exact_controls.py').is_file(), 'Open the extracted project root first'
output = project.parent / 'abc_computation_reproduction'
output.mkdir(exist_ok=False)
records = []

def launch(label, argv, result_path, timeout):
    destination = output / label
    destination.mkdir(exist_ok=True)
    completed = subprocess.run(
        argv,
        cwd=project,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    (destination / 'stdout.txt').write_text(completed.stdout)
    (destination / 'stderr.txt').write_text(completed.stderr)
    record = {'label': label, 'argv': argv, 'exit_status': completed.returncode}
    if completed.returncode != 0:
        records.append(record)
        (output / 'execution_summary.json').write_text(json.dumps(records, indent=2))
        raise RuntimeError(f'{label} failed: see its retained logs')
    assert result_path.is_file(), f'{label}: expected scientific result is missing'
    result_copy = destination / 'results.json'
    if result_path != result_copy:
        shutil.copyfile(result_path, result_copy)
    record['result_sha256'] = hashlib.sha256(result_copy.read_bytes()).hexdigest()
    records.append(record)

jet = output / 'jet' / 'input'
shutil.copytree(area / 'jet_replay' / 'input', jet)
launch('jet', [sys.executable, str(jet / 'verification' / 'verify.py')],
       jet / 'verification' / 'results.json', 120)

canonical = output / 'canonical' / 'input'
shutil.copytree(area / 'canonical_replay' / 'input', canonical)
launch('canonical', [sys.executable, str(canonical / 'final_math_audit.py')],
       canonical / 'final_math_audit_results.json', 180)

implementation = output / 'implementation' / 'input'
shutil.copytree(area / 'implementation_replay' / 'input', implementation)
launch('implementation',
       [sys.executable, str(implementation / 'portable_final_code_audit.py')],
       implementation / 'final_code_audit_results.json', 120)

controls = output / 'controls'
controls.mkdir()
launch('controls', [sys.executable, str(area / 'exact_controls.py'), str(controls)],
       controls / 'results.json', 120)

crt = output / 'crt'
crt.mkdir()
launch('crt', [sys.executable, str(area / 'crt_guard_regression.py'),
              str(area / 'crt_input' / 'abc_moving_interval_search_arbitrary_precision.py'),
              str(crt / 'results.json')], crt / 'results.json', 60)

prime = output / 'good_prime'
prime.mkdir()
launch('good_prime', [sys.executable, str(area / 'good_prime_boundary_control.py'),
                     str(prime / 'results.json')], prime / 'results.json', 30)

(output / 'execution_summary.json').write_text(json.dumps(records, indent=2) + '\n')
print(f'Completed six runs. Results and logs: {output}')
PY
```

This convenience replay does not replace the publication's version 2 provenance records. Those records are retained in each original `run` directory, together with the contracts used to create them. Their manifest validator was fetched from the current computation-audit skill. The exact helper hashes and validation outputs are recorded in `manifest_validation.json`. The recorded wall-clock limits are execution safeguards, not mathematical bounds and not evidence against a theorem if a slower machine reaches them.

Expected outputs are:

| Run | Key result |
|---|---|
| Jet | 149,306 finite assertion evaluations |
| Canonical mathematical audit | 152,095 phase triples, 195 polyphase cases, 2,499 Wronskian packets, 5,001 divisor packets, 391 Kummer cases, 254 Walsh packets, weighted packet height 6 |
| Implementation companion | Nine groups, including moving-search heights 8, 62 and 4,072,242 |
| Independent census | 15,198,743 primitive triples, 121 satisfying the exact inequality `c > R` |
| CRT guard | 2,928 finite brute-force comparisons |
| Good-prime boundary | Raw rank-two valuation 4 at `p=5,t=10`, depleted valuation 3, both valuations 3 at `p=7,t=14` |

Compare the scientific fields with the published outputs. Timestamps, interpreter strings, platform strings, elapsed seconds, temporary paths, and whole-file hashes of output containing those diagnostics need not match. Floating quality columns may differ in their final display digits across platforms. Exact integer classifications and result counts should match.

The only randomness is the inherited Wronskian test, whose seed is 20260731. It samples a finite family of null vectors and is not an exhaustive packet search. Approximate polylogarithm residual tests in the implementation companion remain numerical evidence. The exact modular prime controls have explicit tail bounds, while the full ABC height comparison and global arithmetic realization remain open.

Formal replay is separate. Follow `../FORMAL_STATUS.md` and its formal evidence commands. A Python pass does not compile the Lean files or validate the IUT source interpretation.
