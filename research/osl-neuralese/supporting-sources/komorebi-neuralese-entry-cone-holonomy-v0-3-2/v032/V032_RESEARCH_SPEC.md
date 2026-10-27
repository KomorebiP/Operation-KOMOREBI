# Neuralese v0.3.2 execution-correction specification

Author: Komorebi P.

## Scope

Version 0.3.2 is a correction layer around the prospectively frozen v0.3.1 experiment. It introduces no new scientific parameter, checkpoint, episode, word, diagnostic, gate, composite, or claim. It authenticates and delegates all numerical work to the frozen v0.3.1 modules.

The defect that caused the v0.3.1 abort was in its pre-endpoint lineage validator. The authenticated lineage file records `maximum_merge_multiplicity` inside each episode. The v0.3.1 wrapper instead required a nonexistent seed-level field and failed closed with `lineage regression mismatch for checkpoint 0`.

## Abort boundary

The authenticated v0.3.1 bootstrap read both checkpoint files as raw bytes to verify their SHA-256 digests. Its control flow then performs lineage validation before writing `V031_RUN_STARTED.json` and before calling `checkpoint_io.load_checkpoint`, the restricted deserializer. The failed attempt left `V031_RUN_STARTED.json` and `V031_ENTRY_CONE_HOLONOMY_RESULTS.json` absent and created only `V031_INVALID_ATTEMPT.json`. Thus v0.3.1 aborted before its irreversible ledger, before checkpoint deserialization, and before fresh endpoint execution. No learned endpoint was exposed.

## Correction

The v0.3.2 validator requires the registered seed-level lineage fields, validates all eight episode records per seed, and derives the seed maximum merge multiplicity as the maximum of those episode values. It requires that derived maximum to equal one. No missing aggregate is invented.

Before any numerical or local scientific import, the v0.3.2 CLI rejects executable cache/import shadows and authenticates:

1. its own correction freeze and correction sources;
2. the v0.3.1 execution freeze and invalid-attempt evidence; and
3. every byte named by the v0.3.1 execution freeze.

It requires CPython 3.12.13 with NumPy 2.3.5. Structural tests run in an isolated copy containing no checkpoint files. Only after a new `V032_RUN_STARTED.json` ledger exists may either frozen checkpoint be deserialized; the loader receives a private read-only snapshot produced from one authenticated source-byte read.

The correction freeze is created exactly once with:

```bash
PYTHONDONTWRITEBYTECODE=1 python -I -B v032/freeze_v032.py
```

After that succeeds, the sole registered learned-endpoint invocation is:

```bash
PYTHONDONTWRITEBYTECODE=1 python -I -B v032/run_v032.py
```

Isolated mode removes the script directory, current working directory, user site, and `PYTHONPATH` from interpreter import search. After byte authentication, every local project module is loaded from its exact registered absolute path rather than discovered through `sys.path`.

## Inherited experiment

The experiment is exactly the v0.3.1 entry, finite observed-state cone, dense relation-holonomy, and deterministic matched-control profile on episode seeds 940000 and 941000. The wrapper calls the frozen v0.3.1 context builder and four module functions directly. It reproduces the same integrity gates, diagnostic predicates, preregistered composites, scientific class, and claim boundaries under version 0.3.2.

## Claim limit

This remains an adaptive-developmental diagnostic on two frozen eight-state D4 systems. It provides no ambient or infinite cone certificate, causal-quotient minimality result, population inference, task-family generalization, invariant-metric certificate, normally attracting realization, or universal Neuralese claim.
