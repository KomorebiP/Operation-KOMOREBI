# Reproduce AVOC v0.38.0

## Pinned environment

Use Linux x86-64 or WSL, Python 3.10+, and the preserved AVOC portable Lean layout.

- Lean `4.34.0-rc2`, commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`
- mathlib `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`
- nine exact package revisions in `lake-manifest.json`

The source archive excludes the runtime and compiled dependency caches.

```bash
export AVOC_LEAN_KIT=/absolute/path/Komorebi_Portable_Lean_4.34.0-rc2
python tools/check_manifest.py
```

## Inventory and clean local build

```bash
python tools/inventory_v038.py
python tools/verify_v038.py --prepare
python tools/build_v038_parallel.py --seconds 60 --workers 3 --per-target-seconds 240
```

Repeat the bounded build command until it reports:

```text
CURRENT 205 / 205 REMAINING 0 FAILED []
```

Do not repeat `--prepare` between slices.  A timeout or interrupted child is inconclusive and must be rerun.

The final release evidence uses the 205 direct local targets, including aggregate `AVOC.lean` and every Lean executable entrypoint.  Redundant `lake build` frontend attempts were interrupted by the host limit and are not release evidence.

## Axiom audit

```bash
python tools/verify_v038.py --audit --seconds 900
```

Expected:

- 2,044 exact reports;
- no missing, extra, or duplicate declaration names;
- axiom union only `propext`, `Classical.choice`, `Quot.sound`.

## Complete negative suite

```bash
python tools/run_negative_v038.py --seconds 60 --workers 2 --per-file-seconds 90
```

Repeat until it reports 111/111 substantive rejections.  Import errors, missing objects, timeouts, and absent logs are not successful negative tests.

## Robust quote executable

```bash
python tools/run_robust_quote.py examples/robust_quote/exact_plan.json
python tools/run_robust_quote.py examples/robust_quote/uncertain_plan.json
python tools/run_robust_quote.py examples/robust_quote/dominance_plan.json
python tools/run_robust_quote.py examples/robust_quote/warm_transition.json
python tools/run_robust_quote.py examples/robust_quote/warm_recover.json
```

The wire interface uses integers and exact rational strings.  Floats and malformed fractions are rejected.

## Independent exact regression

```bash
python checks/test_robust_quote.py
python checks/test_robust_quote_workflow.py
python checks/test_robust_quote_recovery.py
```

The `Fraction` oracle is independent of the Lean Bellman evaluator.  The workflow tests use fresh SQLite run directories and actual Lean subprocesses.

## Recheck inherited lazy staged behavior

Run cases separately on execution-capped hosts:

```bash
python checks/test_lazy_staged_workflow.py --case warm
python checks/test_lazy_staged_workflow.py --case cold
python checks/test_lazy_staged_workflow.py --case invalid
python checks/test_lazy_staged_workflow.py --case crash
```

## Source and release checks

```bash
python tools/source_scan_v038.py
python tools/summarize_v038.py /path/to/AVOC_Formal_v0.37.0.zip
python tools/package_v038.py --output /chosen/AVOC_Formal_v0.38.0.zip
python tools/check_manifest.py
```

Check the original package manifest before regenerating evidence.  Regenerating logs intentionally changes manifest-covered files.  Historical evidence is not fresh v0.38 evidence.

## Trust boundary

Compilation and execution rely on the installed Lean runtime, pinned cached dependencies, Python, SQLite, OS, and protected filesystem.  Exact formal theorems do not by themselves calibrate real quote probabilities or prove the physical runtime trustworthy.
