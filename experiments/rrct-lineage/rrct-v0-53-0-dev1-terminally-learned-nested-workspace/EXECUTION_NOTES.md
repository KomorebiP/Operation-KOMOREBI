# RRCT v0.53 Execution Notes

## Pre-outcome seal

SHA-256:

```text
4e372d6dfd231479edfb215f9fb1f77cc7fd20d6cc48e0c0340f58b773202dc2
```

The seal covered 8 scientific files, all unchanged after execution.

## Process isolation

A combined parent invocation completed two seeds but exceeded its execution window before producing a cohort result. It is not treated as evidence. The same sealed training/evaluation functions were then invoked once per frozen seed in isolated Python processes, and a post-freeze wrapper aggregated the outputs using the frozen thresholds. No source, seed, model, training budget, threshold, or endpoint changed.

## Replay

Seed `109716655` was rerun. The nested, one-dimensional, and flat model files were byte-identical and the complete per-seed JSON object was exactly equal.

## Validation

- focused tests: 3 passed
- frozen endpoints: 18 of 18 passed
- model/result integrity: passed
- one-seed exact byte replay: passed

## Limits

Synthetic continuous task; supplied hierarchy; supplied second-order interaction primitive; rich terminal output supervision; flat controller also solves; no dynamic coalition formation or consciousness claim.
