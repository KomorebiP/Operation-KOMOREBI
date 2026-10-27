# RRCT v0.49 Execution Notes

## Development

Development seeds: `49001`, `49007`.

The initial larger transformer exceeded the short CPU training window. The final frozen architecture used one 24-dimensional transformer block per agent and converged deterministically in 150 steps on all development and holdout seeds.

The original early-state J-space hypothesis failed. Stage scanning was added during development. The final protocol freezes that failure as a required negative endpoint.

## Source seal

The pre-outcome manifest covered 89 runtime, protocol, runner, test, and environment files.

Manifest SHA-256:

```text
01c040c3493bcdae21cd64b4a5bb2ca07f1493db733cb17736392eb45a606fc9
```

All files verified before holdout execution.

## Holdout

Seeds:

```text
781763488
381195510
811722952
585185981
```

Execution completed in approximately 31 seconds in the recorded CPU environment.

All 23 frozen endpoints passed.

## Replay

A complete independent reanalysis of seed `781763488` reproduced:

- the exact trained model SHA-256;
- the exact per-seed analysis digest;
- the exact complete analysis object.

A later four-seed replay command stalled after producing three weight files and exceeded the allowed execution window. No complete replay summary was produced. It is treated as incomplete and is not counted as a successful full replay.

## Tests

Focused v0.49 tests:

```text
7 passed
```

Selected v0.46–v0.48 successor unit tests:

```text
29 passed, 4 deselected
```

The deselected tests are predecessor benchmark or source-freeze checks inappropriate for a modified successor tree.

Python syntax validation:

```text
199 files parsed
```

A first combined successor command exceeded its execution window before producing a pytest summary and is not counted as passed or failed.

## Dependency boundary

PyTorch is required for the v0.49 experiment but is not vendored in the compact archive. The recorded holdout used:

```text
Python 3.13.5
PyTorch 2.10.0+cpu
NumPy 2.3.5
```

The agents were trained from scratch. No pretrained checkpoint was used.

## Installed-wheel probe

The built `rrct_prototype-0.49.0.dev1` wheel was installed without dependencies into an isolated target directory while using the recorded local PyTorch runtime. The installed package imported as version `0.49.0.dev1` and the sealed seed `781763488` passed all 23 endpoint predicates with an analysis digest exactly matching the canonical result.

A first reporting command requested a nonexistent result key named `model_digest` after the analysis had already completed and raised `KeyError`. The corrected probe used the actual public result keys and passed. No source, threshold, endpoint, or holdout evidence was modified.

The inherited `uv.lock` still describes the v0.48 project and does not include the optional PyTorch extra. An offline lock refresh failed because registry packages were unavailable in the cache. The v0.49 runners and wheel verification do not use that lockfile.
