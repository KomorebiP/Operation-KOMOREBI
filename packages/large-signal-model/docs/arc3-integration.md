# Optional ARC-AGI-3 integration

PR-LASM can drive the official local ARC interface through a narrow adapter.
The integration is optional and is not required for the exact coordinate,
packet-refinement, operator-posterior, or synthetic planning benchmarks.

## Pinned contract

```text
Python >= 3.12
arc-agi == 0.9.9
arcengine == 0.9.3
```

The adapter constructs `Arcade` with an empty API key and
`OperationMode.OFFLINE`. It reads public observations and submits public
actions. It does not inspect a game's internal `_game` object.

## Environment files

Downloaded or user-supplied environment sources are excluded from the Git
repository. Extract the optional fixture archive into the repository root,
or place your own local tree under `environment_files/`.

## Offline guard

Runtime startup blocks socket connections, DNS lookups, `urllib`,
`http.client`, and Requests. Proxy variables are redirected to an
unreachable loopback address. This process-level guard supplements, rather
than replaces, operating-system sandboxing.

## Test layers

- Core tests use synthetic observations and stubbed official interfaces.
- Eight `local_suite` tests require the separate 25-environment fixture archive.
- Static audit verifies metadata, source layout, prohibited imports, and selected dynamic-execution calls.
- No official score is reported by this repository.
