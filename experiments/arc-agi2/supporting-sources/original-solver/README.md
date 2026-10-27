# Komorebi PR-LASM — Block 17

Author: Komorebi P.

This release combines the inherited live ARC solver and candidate banks through Block 15, then tests a task-local, witness-based repair veto. The reference G47 frontier is evidence only. It never supplies runtime predictions.

The large recorded censuses use losslessly compressed JSON (`.json.gz`). To replay the frozen dispatcher without recomputing the compiler bank:

```sh
python dispatch_cached.py --challenges data/challenges.json --census results/census.json.gz --policy typed_recent --output results/replayed_predictions.json
```

`dispatch_cached.py` only decodes the evidence file before calling the unchanged dispatcher. Its source hash and the storage helper are bound into the prediction freeze. Fresh compiler scans still accept and produce ordinary JSON.

Python 3.12 and NumPy 2.3.5 were used for this run. No other third-party package is required by the runtime. Run commands from this directory.

## Recompute the complete solver

```sh
python run_scan.py --challenges data/challenges.json --include-new --workers 8 --output results/fresh_full_census.json
python solver.py --challenges data/challenges.json --census results/fresh_full_census.json --policy typed_recent --output results/fresh_predictions.json
```

The fixed feature-induction budget is conjunction depth 2, beam width 32 and at most 32 emitted programs. Both core entry points use nominal tier 2.0 (2,200 composition expansions). Other banks use their inherited limits. The deeper feature search was profiled but is not the reported complete-run budget.

The same interface accepts another challenge file with demonstration input/output pairs and test inputs. Attached test outputs are rejected. The full scan runs each compiler, including normal abstentions and failed activations. Checkpoints are bound to code, source manifests, limits and challenge content; a changed input requires a new output path.

## Reproduce the recorded experiment

The recorded run saves compute by reusing the source-matched 48-compiler Block 16 census, while recomputing the older bank and live base:

```sh
python run_scan.py --challenges data/challenges.json --workers 8 --output results/legacy_census.json
python finish_run.py
python validate.py --output results/validation.json
```

The source and prediction freezes precede the recorded scoring. `evaluate.py` is the separate, solution-open evaluator. It checks the frozen prediction hashes before computing all metrics. It is never imported by the runtime.

`run_scan.py` invokes the unchanged engine with spawned workers, avoiding inheritance of loaded checkpoints. The canonical run switched to this launcher after 574 records. Its three-task full-bank sample census exactly matches the earlier worker configuration, with the comparison in `results/spawn_validation.json`. Direct `engine.py scan` remains available and uses the platform default process startup.

`PROTOCOL.md` describes all six policies and their limits. The primary policy keeps the live base's first attempt; it spends the second slot on the highest-ranked distinct behavior. `recent_control` uses identical ranking without the repair veto. `typed_joint` allows candidates to fill both slots. `typed_agreement` tests source-vote priority. The `base` policy exposes the live base unchanged. The additional `typed_supported` control abstains when a feature-table candidate reports unseen test keys, recording uncertainty rather than a falsification.

Earlier native compilers and the Block 13 adapters have different verification interfaces from the 48 modern replay-hook entrants. Their provenance is retained rather than upgraded by assertion. This is development on an exposed public training corpus. A runtime score here is an unfiltered training result, not an unseen benchmark estimate.

A small, task-local memoization adapter avoids repeated construction of identical features. It keys on exact array content, never task identity. Both original and optimized candidate outputs are compared in `results/memo_equivalence.json`. An earlier partial scan is preserved as evidence of that pre-score optimization.

The release includes scoring labels solely under `evidence/`, alongside the unchanged G47 reference and the previous source-matched census. Prediction APIs do not accept those labels. Runtime source authentication checks hashes; it does not constitute an operating-system isolation boundary.

The three saved compiler-replay inputs are in `results/replay_challenges.json`. Re-run them with `engine.py scan --include-new`; their records must match `results/live_replay_sample.json` and the complete census. This validates the saved sample without requiring the earlier work checkpoint.

The isolated geometry repair is in `repair_entrants/micro_schemas_v2.py`. `repair_scan.py` checks all 1,000 original/repaired compilations; `geometry_repair.py` supplies its separately frozen dispatch variants. It adds dimension preconditions to three input-frame operators. The paired run removes 237 exceptions and introduces no new activations.
