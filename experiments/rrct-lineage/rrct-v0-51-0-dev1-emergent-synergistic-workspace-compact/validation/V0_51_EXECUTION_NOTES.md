# RRCT v0.51 Execution Notes

## Source integrity

The pre-outcome source manifest sealed 96 files before any holdout model was trained.

```text
947bd94043dd3bb893b7826b6f9aae94407c31febb1ee0f6fb67ec1144ede72b
```

The seal was rechecked after execution. All files and the companion digest matched.

## Frozen cohort

```text
775479101
759701819
811753828
899346405
```

No seed was replaced after selection.

## Parent-runner timeout

The sealed parent runner launched the first curriculum-training child successfully, then exceeded the ten-minute execution window before producing a cohort receipt. Only the first curriculum model existed at that point.

The incomplete invocation is not counted as evidence.

## Isolated continuation

The frozen `train_v051_model.py` helper was invoked in a fresh Python process for each of the remaining curriculum and terminal-only models. This avoided the parent-process scheduling stall.

The frozen `analyze_trained_seed` and `assemble_holdout` functions were then used without modification to produce the cohort result.

No changes were made to:

- model architecture
- training steps
- optimizer
- split
- thresholds
- endpoints
- holdout seeds
- scientific source

The execution receipt records the resumed isolated-process mode.

## Frozen result

```text
V051_FROZEN_BOUNDED_EMERGENCE_ENDPOINTS_MET
```

All 21 endpoints passed.

## Test evidence

- focused v0.51: 9 passed
- v0.47, v0.48, v0.51 fast line: 29 passed
- v0.49 focused: 7 passed
- v0.50 focused: 8 passed
- v0.42–v0.46: 44 passed, 4 predecessor seals deselected
- v0.36–v0.40: 64 passed, 1 historical freeze-builder test deselected
- AST syntax validation: 215 files passed

## Incomplete broad commands

A v0.47–v0.51 combined command exceeded 600 seconds after 22 progress dots and no summary.

A v0.42–v0.51 combined command exceeded 600 seconds after 65 progress dots and no summary.

Neither is represented as passed or failed. The same files were subsequently run in smaller completed subsets as documented above.

## Scientific limitation

The positive result depends on round-level curriculum targets. The matched terminal-only control reached only partial performance and did not discover the full recurrent algorithm under the frozen budget.

The representation is learned. The recurrence scaffold is not.
