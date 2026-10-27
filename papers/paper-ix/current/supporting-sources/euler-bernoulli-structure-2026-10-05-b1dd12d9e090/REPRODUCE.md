# Reproduce this checkpoint

Python 3.12 and its standard library suffice. The original runs record
their precise environment and bounds. Run from this extracted directory.

## Verify the saved bytes and current manifests

```bash
python3 verify_checkpoint.py
```

Historical superseded runs are preserved for provenance; they are not
validated against later source revisions. Current runs are explicitly
listed in bernoulli_closure/CURRENT_EVIDENCE.json.

## Replay computations

These commands write new replay outputs instead of overwriting saved
evidence. The manifest command arrays preserve the original commands.
Result timing fields may vary; finite arithmetic records should agree.

Working directory: `.`.
```bash
python3 bernoulli_closure/nonintersection/check_hankel_separation.py replay_01.json
```

Working directory: `.`.
```bash
python3 bernoulli_closure/hankel_bridge/check_hankel_bridge.py replay_02.json
```

Working directory: `.`.
```bash
python3 bernoulli_closure/root/check_quadratic_form.py replay_03.json
```

Working directory: `.`.
```bash
python3 bernoulli_closure/recurrence/check_constrained_tangent.py replay_04.json
```

Working directory: `bernoulli_closure/separation`.
```bash
python3 check_bernoulli_pade.py replay_05.json
```

Working directory: `bernoulli_closure/separation/carry_adapted`.
```bash
python3 check_carry_adapted.py replay_06.json
```

Working directory: `.`.
```bash
python3 bernoulli_closure/nonintersection/jacobi_height/check_safe_jacobi.py replay_07.json
```

Working directory: `.`.
```bash
python3 bernoulli_closure/root/check_quadratic_form.py replay_08.json
```

Working directory: `.`.
```bash
python3 bernoulli_closure/nonintersection/jacobi_height/check_safe_jacobi.py replay_09.json
```

Working directory: `.`.
```bash
python3 bernoulli_closure/review/check_pade_review.py replay_10.json bernoulli_closure/review/pade_source_results_snapshot.json
```

## Review inherited context

The parent ZIP is included byte-for-byte and its SHA256 is pinned in
CURRENT_EVIDENCE.json. Extract it separately when consulting earlier
radix or higher-address proofs. The new evidence does not reclassify
old finite experiments as universal proofs.
