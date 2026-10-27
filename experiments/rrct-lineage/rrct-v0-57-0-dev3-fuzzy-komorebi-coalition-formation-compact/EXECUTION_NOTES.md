# RRCT v0.57 Execution Notes

## Development

Four development seeds were used to select the fixed architecture, training budget, holdout interpolation family, and frozen thresholds.

The development cohort showed:

- fuzzy mean MSE approximately 0.000506
- direct-edge mean MSE approximately 0.000238
- learned-hard mean MSE approximately 0.08597
- mean idempotence-to-target correlation approximately 0.915
- mean membership-to-ablation correlation approximately 0.552

No development seed appears in the frozen holdout.

## Pre-outcome freeze

Before holdout training, 13 files were bound in `validation/PREOUTCOME_FREEZE.json`.

The seal covered:

- source
- focused tests
- protocol
- endpoint thresholds
- seed selection
- training and analysis scripts
- Windows and Bash runners
- package metadata

Pre-outcome manifest SHA-256:

```text
8f61315b993600763491f6c45aafade46cdc42f134c628a13a4654ca27e27da0
```

All 13 files verified unchanged after holdout execution.

## Holdout execution

Eight seeds were fixed before outcomes:

```text
425186362
440681555
998313287
159272024
228634863
316106489
214436720
756743177
```

Four models were trained per seed:

- fuzzy packet
- hard packet
- direct edge
- exploratory crystallization-pressure packet

The sealed parent process-control wrapper exceeded the available tool execution window after completing part of the cohort. Remaining model jobs were invoked separately, but every job used the unchanged sealed source, model function, training configuration, seed, evaluation seed, case count, and endpoint definitions.

No failed or incomplete model result was included.

## Validation

- frozen endpoints: **22 of 22 passed**
- focused tests: **4 passed**
- Python syntax validation: **9 files passed**
- pre-outcome source verification: passed
- offline wheel build: passed
- isolated wheel installation: passed
- installed packet-partition probe: passed
- exact deterministic replay of fuzzy seed 425186362: passed
- replay curve: exact
- replay analysis object: exact
- replay tensor-state digest: exact

The exact replay tensor digest was:

```text
8288db7eb20720b48bc80240cc220744bff2994af1db8960c5d0f6e6c5ccfdad
```

## Exploratory crystallization control

The model with uniform idempotence pressure was not part of the frozen endpoints. It was trained with the same seeds and architecture after the primary source and endpoint freeze.

It reduced packet defect but increased prediction error. It is retained as a labeled exploratory result rather than merged into the primary claim.
