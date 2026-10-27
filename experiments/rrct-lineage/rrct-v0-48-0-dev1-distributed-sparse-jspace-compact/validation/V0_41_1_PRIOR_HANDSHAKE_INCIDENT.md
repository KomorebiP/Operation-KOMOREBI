# v0.41.1 development incident: late generic-prior issuance

Status: retained pre-matrix development failure.

During the first concurrent seed-41011 matrix attempt, `G_RPLUS` stopped in `identity_b_first` after 2,880 streamed rows. The temporal controller had issued and cached a generic prior for a target epoch after that epoch's lower grounding ledger already contained fresh samples. The lower controller correctly declined to insert the prior retroactively. On the next row, the cached receipt's original `seeded_time` no longer matched the current time, so the run failed closed with:

```text
ValueError: historical grounding prior was not issued now
```

`K_RPLUS` and `N_RPLUS` were then intentionally interrupted after approximately 4,320 rows so that no matrix arm would be completed against a different source revision.

The three partial output directories were preserved under:

```text
validation/v0.41.1_development_matrix_seed_41011/_failed_pre_handshake/
```

Repair: the runtime now asks the grounder whether the target epoch has an already registered prior or is still empty and eligible to receive one. The temporal controller is called only in the latter case. A prior therefore cannot be minted after fresh target evidence has begun, and a registered prior is reused with its original provenance instead of being reissued at a later time.

This incident occurred in exposed development. No frozen source or unopened confirmatory seed was involved.
