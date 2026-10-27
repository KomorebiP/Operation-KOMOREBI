# Reproduce AVOC v0.39.0

Use Linux x86-64 or WSL and Python 3.10+. This source archive excludes the Lean
runtime and compiled dependency caches. Use the separately preserved portable
Lean kit, whose nine package revisions must match lake-manifest.json.

- Lean 4.34.0-rc2, commit 6a10ac8c22beadecabdbb0919c2b50214762f91d
- mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06

```bash
export AVOC_LEAN_KIT=/absolute/path/Komorebi_Portable_Lean_4.34.0-rc2
python3 tools/check_manifest.py
python3 tools/inventory_v039.py
python3 tools/verify_v039.py --prepare
python3 tools/build_v039_parallel.py --seconds 45 --workers 3 --per-target-seconds 180
```

Repeat only the last command until it prints CURRENT 212 / 212 REMAINING 0
FAILED []. Do not repeat --prepare between slices. It deletes local build
outputs, while retaining only external pinned caches. Timeouts, missing imports,
and unfinished jobs are inconclusive, never successes.

```bash
python3 tools/verify_v039.py --audit --seconds 180
python3 tools/source_scan_v039.py
python3 tools/run_negative_v039.py --seconds 45 --workers 2 --per-file-seconds 90
```

Repeat the negative command until CURRENT 119 / 119. Expected axiom reports:
2,122 explicitly named theorem/lemma declarations, including two inherited
private helpers, and only propext, Classical.choice, Quot.sound. Six inherited
negative setup defects were repaired; originals and diagnostics are preserved.

```bash
python3 checks/test_calibration.py --lean
python3 tools/run_inherited_regression_v039.py --case all
```

The new exact regression uses an independent Fraction implementation and exact
count convolution, then compares actual Lean evaluation. It also checks
calibration-to-planning action change with positive-radius dominance. The
inherited runner relocates old selected-artifact paths and retains missing
unselected paths. Fresh temporary run directories prevent replay interference.

## New executable

The log snapshot schema and explicit assumptions are in
examples/calibration/README.md. The request includes the protected identity,
prospective finite schedule, error allowances, and immutable operation outcomes.

```bash
python3 tools/calibrate_quote.py examples/calibration/n500_k400_grid1000.json \
  --plan examples/robust_quote/uncertain_plan.json
```

--plan executes the actual Lean interval
functions, compares them with independent Python endpoints, and executes the
actual Lean planning/dominance functions. It emits a new plan and does not run
external warm/cold operations or mutate an active durable checkpoint.

The lower-level endpoint accepts an array
["calibration-binomial-v1",n,k,m,"numerator/denominator"] through
`python3 tools/run_calibration_lean.py request.json`. Batch requests use
["calibration-batch-v1",[requests...]]. Exact integer tokens or reduced
nonintegral rational strings are supported. Decimal/exponent tokens, malformed
fractions, invalid counts, and execution-cap violations are rejected.

## Final evidence and package

```bash
python3 tools/release_check_v039.py
python3 tools/package_v039.py --output /chosen/AVOC_Formal_v0.39.0.zip
python3 tools/check_manifest.py
```

Check the original payload manifest before regenerating any evidence. A rerun
intentionally changes timed regression outputs; regenerate the computation
manifest's hashes before asserting its consistency. `release_check_v039.py`
checks current source, object, import, log, negative, inventory, and axiom data.
Packaging separately checks all payload hashes, archive CRC, and file membership.

Read PROOF_BOUNDARY.md before interpreting the statistical and policy guarantees.
