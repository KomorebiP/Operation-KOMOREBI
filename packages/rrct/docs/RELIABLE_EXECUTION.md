# Reliable local execution

## Atomic checkpoints

Each checkpoint records:

- stable configuration digest
- episode or training step
- serialized controller state
- state digest
- current metrics
- status and resume count

Writes use a temporary file followed by atomic replacement. `latest.json` always points to the last completely written state.

## Exact resume

The continuous runtime checkpoints:

- episode index
- fuzzy membership matrix and active packet count
- packet birth/death counters and lifetimes
- self/world and partner/sensor estimates
- true hidden synthetic state needed for deterministic continuation
- evidence budget
- memory and provenance counters
- event state
- metric accumulators
- row tail
- NumPy RNG state

A regression test interrupts a run, resumes it, and compares the semantic trajectory digest, metrics, and condition rows against an uninterrupted run.

## Resource limits

`runtime.timeout_seconds` and `runtime.memory_limit_mb` are cooperatively checked during continuous episodes. Other families receive a final common check; fully preemptive single-run process isolation remains partial.

## Parallel sweeps

The sweep scheduler provides:

- stable cell names derived from override digests
- process-based parallel execution
- serialized GPU worker limits
- atomic sweep state
- completed-cell skipping
- retry count
- fail-fast behavior
- stable CSV/JSON aggregation

A second invocation with `sweep.resume=true` skips completed cells.

## Freeze workflow

A freeze binds:

- resolved configuration
- strict feature contract
- stable checkpoint digest
- Python source hashes
- package metadata and local requirements
- seed policy

Commands:

```text
rrct-lab freeze CONFIG --output FREEZE.json
rrct-lab verify-freeze FREEZE.json
rrct-lab holdout FREEZE.json
rrct-lab audit RUN_DIRECTORY
```

The freeze system is generic infrastructure. Passing a frozen smoke run does not convert an exploratory configuration into a scientific result; endpoints and holdout interpretation still need to be predeclared by the researcher.
