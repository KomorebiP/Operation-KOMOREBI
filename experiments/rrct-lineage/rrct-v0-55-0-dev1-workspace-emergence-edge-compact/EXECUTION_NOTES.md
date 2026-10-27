# RRCT v0.55 Execution Notes

## Primary seal

The primary implementation, analysis logic, thresholds, tests, seeds, and runners were sealed in 12 files before primary or crossed outcomes were generated.

Primary pre-outcome manifest SHA-256:

```text
c8da5194946a1aa5f1043604bae93c97e0a8e7678c63825d2753b27dc5688566
```

The seal verified unchanged after execution.

## Primary execution

- 132 parameter-matched trajectories
- 32 crossed initialization/data trajectories
- deterministic CPU PyTorch
- one training trajectory per model
- dense checkpoint evaluation

## Analysis serialization repair

The sealed analysis completed all numerical computations but raised a JSON serialization error because one endpoint comparison returned a NumPy boolean scalar.

A post-outcome wrapper supplied scalar conversion to `json.dumps` and reran the unchanged sealed analysis logic. No metric, model, threshold, seed, or endpoint definition changed.

## D=2 tail extension

The sole trajectory censored at 1400 updates was retrained to the preexisting 2400-update checkpoint horizon. It reached stable onset at 1800 updates.

The full 24-seed D=2 tail extension is labeled post outcome and does not alter the primary frozen endpoint evaluation.

## Overcomplete extension

After the primary edge showed a plateau at D=6–8, a separate fresh-seed extension was prospectively sealed for D=10,12,14,16,20.

Overcomplete pre-outcome manifest SHA-256:

```text
f3e5b277246ca1fbe4c11c57c09df3c5f0f5e40d65cfa54549dbe6351973bc67
```

All four extension endpoints passed.

## Representative replay

Four representative trajectories were retrained and compared after removing only elapsed wall-clock time:

- D=1 structural failure
- D=2 late tail
- D=8 plateau
- D=20 congestion edge

Every numerical checkpoint and scientific outcome matched exactly.

## Validation boundary

A complete retraining of all 248 trajectories is not included in package verification because it would be unnecessarily expensive. The package contains every trajectory record, source file, seed receipt, protocol, result table, figure, and checksum needed for independent rerun.
