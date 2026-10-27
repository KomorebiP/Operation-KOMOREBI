# Reproduce AVOC v0.41.0

Use Linux x86-64 or WSL and Python 3.10+. The source archive excludes the Lean
runtime and compiled dependency/project objects. Use the separately retained
portable kit with the nine exact package revisions in lake-manifest.json.

- Lean 4.34.0-rc2, commit 6a10ac8c22beadecabdbb0919c2b50214762f91d.
- mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06.

Check the delivered payload before regenerating evidence. The original v0.40
ZIP is needed only to independently repeat the inherited-source comparison.
The pinned baseline record additionally preserves historical evidence and
inherited runtime/check source digests from that exact ZIP.

```bash
export AVOC_LEAN_KIT=/absolute/path/Komorebi_Portable_Lean_4.34.0-rc2
python3 tools/check_manifest.py
python3 tools/check_inherited_v041.py /absolute/path/AVOC_Formal_v0.40.0.zip
python3 tools/inventory_v041.py
python3 tools/verify_v041.py --prepare
python3 tools/build_v041_parallel.py --seconds 45 --workers 3 --per-target-seconds 180
```

Repeat the build command, waiting for each invocation to exit, until CURRENT
222 / 222 REMAINING 0 FAILED []. Do not repeat --prepare between slices: it
removes local objects. The lock prevents overlapping release builds. Resumption
requires current source, import, output, and log hashes. No test using compiled
objects should run during --prepare or their rebuild.

```bash
python3 tools/verify_v041.py --audit --seconds 600
python3 tools/run_negative_v041.py --seconds 45 --workers 2 --per-file-seconds 90
python3 tools/source_scan_v041.py
```

Repeat the negative command until 135/135 substantive rejections are current.
A crash, timeout, parser/setup/resource failure, or mixed such diagnostic does
not count as a mathematical rejection. The audit expects exactly 2,268 named
theorem/lemma reports and only propext, Classical.choice, Quot.sound. The four
new modules add 69 named declarations; all 191 inherited non-audit modules match.

The source-pinned release oracle and bounded-run manifest are already included.
To repeat its scientific comparison while retaining the original manifest and
canonical result, use a separate output file after the complete build:

```bash
python3 checks/test_observation_recorder.py --lean --output results/v0.41.0/oracle_replay.json
python3 tools/run_inherited_regression_v041.py --case all
```

The recorder oracle enumerates 69,905 Python/reference words and compares 4,381
words with the actual Lean endpoint, plus malformed-input, resource-boundary,
registry/export, CLI, and inherited-calibration cases. It records the consumed
Lean executable and recursive local source/object closure separately from its
portable source manifest. See RECORDER_EXECUTABLE.md for the exact finite scope.
The earlier v0.40 observation oracle is preserved and its unchanged inputs are
checked; it is not relabeled as a fresh execution.

The inherited runner replays robust quote oracle, selected-only workflows,
recovery, lazy staged execution, and calibration through actual Lean. It writes
isolated v0.41 evidence and relocates selected fixture paths, leaving historical
results and original check/runtime sources unchanged. Inputs, fixtures, adapted
check sources, and outputs are hashed.

```bash
python3 tools/release_check_v041.py
python3 tools/package_v041.py --output /chosen/AVOC_Formal_v0.41.0.zip
python3 tools/check_manifest.py
```

The final gate validates exact target/name/test membership, current hashes and
compiler provenance, the runtime-bound new oracle, archived baseline data,
independent source/tool reviews, and all fresh inherited regressions. Changing
reviewed source requires actual renewed review, not editing a digest alone.
Packaging reruns the gate and verifies archive CRC, unique exact membership,
every payload digest, and source stability. A separate ZIP checksum and package
report accompany it. Source restoration requires rebuilding excluded objects
before a runtime-bound gate can pass.

## Use the new recorder

```bash
python3 tools/observation_recorder.py examples/observation_recorder/complete.json
python3 tools/run_recorder_lean.py examples/observation_recorder/complete.json
python3 tools/observation_recorder.py examples/observation_recorder/complete.json --registry examples/observation_recorder/registry.json
```

Each request starts empty and reduces supplied commands. No paid operation,
retry, durable journal update, or policy issuance occurs. The optional registry
exports completed observations only when no intent is pending; its identities
must be injective. It does not authenticate labels or prove the source law.

The inherited calibration command remains available and unchanged:

```bash
python3 tools/calibrate_quote.py examples/calibration/n500_k400_grid1000.json --plan examples/robust_quote/uncertain_plan.json
```

Two preliminary bounded recorder runs produced no scientific result. The 2 GiB
virtual-memory cap prevented Lean thread creation; the 8 GiB cap prevented its
startup mappings. A diagnostic run observed about 8.56 GiB peak virtual space
and 3.66 GiB resident memory. The final run adds no RLIMIT_AS cap and records the
inherited shared 20 GiB cgroup limit separately, retaining wall/CPU/log/core
bounds. Both failed manifests and the launcher diagnostic correction are retained.
These resource adjustments do not change the tested mathematical claim.
