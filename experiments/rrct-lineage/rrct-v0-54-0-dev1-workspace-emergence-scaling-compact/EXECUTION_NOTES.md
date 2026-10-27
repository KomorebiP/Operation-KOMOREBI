# RRCT v0.54 Execution Notes

## Development campaign

The development grid used seeds `54011, 54029, 54047`. PyTorch model creation caused allocator/resource stalls in long single-process sweeps. The grid was therefore executed in short isolated chunks with identical source, optimizer, training schedule, and evaluation functions. Partial files were retained incrementally.

No scientific threshold was changed because of those execution stalls.

## Frozen holdout

Fresh seeds were selected by SHA-256 counter expansion without model execution:

```text
346629959
886135314
325650043
346151134
```

Nine source/protocol/threshold files were sealed before holdout execution.

Pre-outcome freeze SHA-256:

```text
13045c0c8468dcbfbf7135adba48ddd85b3a5868f7485ca05121b21eb18a7d58
```

Each of the 28 holdout models was trained in a fresh Python process to avoid cumulative PyTorch allocator stalls. All points used the sealed source and full evaluation criteria.

## Frozen result

`V054_HOLDOUT_ENDPOINTS_NOT_MET`

Thirteen of sixteen endpoints passed. The failed endpoint values were retained unchanged.

## Post-hoc extension

After the frozen failure was known, d2/width32 was evaluated at 1200 updates on the same four fresh seeds. All four passed full emergence. This result is explicitly labeled post hoc and was not used to rewrite the frozen status.


## Final verification

The release verifier passed 52 of 52 integrity and evidence checks. Two representative frozen configurations were retrained with exact equality on every scientific field except wall-clock time. All four post-hoc d2/width32/1200 configurations were retrained with exact equality on every scientific field except wall-clock time.

A complete 28-cell frozen retraining replay was attempted but not completed in one uninterrupted command because repeated long one-dimensional runs exceeded the packaging execution window. The original point files, aggregate recomputation, source seal, representative frozen replays, and complete post-hoc replays are all retained. No claim of a complete 28-cell replay is made.
