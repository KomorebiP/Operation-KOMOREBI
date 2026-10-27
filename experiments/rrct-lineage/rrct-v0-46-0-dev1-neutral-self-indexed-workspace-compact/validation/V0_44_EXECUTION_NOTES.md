# RRCT v0.44 Execution Notes

## Development chronology

1. The v0.43 compact release was extracted and its focused suite passed before successor work began.
2. The next gap was fixed as endogenous transformational self-continuity.
3. An initial controller and matched transformation cohort were implemented.
4. The first live run found a receipt-chain defect: successor registration could occur in `transfer_cut` even though planning had not used transported memory. Registration was changed to require `plan.memory_transfer_used`.
5. Initial continuity scoring was overly conservative because small memory traces used nearly unregularized least squares. A development identity produced a normal-equation condition number above 700 and an unstable held-out residual.
6. The memory estimator was replaced before freezing with deterministic three-fold cross-validated selection between orthogonal transport and a fixed ridge family. The selected model is refit on all current evidence.
7. A multigeneration run exposed an assumption that every successor retained the original memory-row count. The evidence generator was repaired before freezing to use only rows actually retained after compression.
8. Declared tuning identities and additional exposed numerical-stress identities were run. The frozen thresholds and 23 endpoints were then fixed.
9. Four holdout identities were selected with operating-system cryptographic randomness without examining candidate outcomes.
10. A 76-file source manifest was created and verified before holdout execution.
11. The holdout was executed once. All 23 endpoints passed.
12. A second execution to a temporary directory produced exact normalized analysis equality and byte-identical CSV/report artifacts.

## Frozen execution

- Holdout identities: `973948357, 903438047, 119520877, 251222378`
- Pre-outcome manifest SHA-256: `53696bb4179be18239f936234b551abbd7eaee5ed506f3ceb48eb4dbd09775ff`
- Original analysis SHA-256: `439e47a4849d9317be43b6737b48138f62397115defba3836cda1a1bb5ac27c6`
- Normalized replay SHA-256: `c5eaa3cf0d32b3833ee96fff337db47363a47fcb97ac5d95b1d87f52da9de4da`
- Decision CSV SHA-256: `c97a9b835811472c583dd683b448e1ad4616bbc3a9615df6cd83bf5ab718494b`
- Human report SHA-256: `0af936dff2657be76ba29a0833c1f76ee05c8baaee6915e77093eca9a67976d3`

The normalized comparison removes only the execution receipt, whose timestamps and process identifier are intentionally run-specific. All scientific fields are identical.

## Test results

- `tests/test_v044_transformational_self_continuity.py`: 10 passed
- Selected runtime regression from v0.32 through v0.44: 111 passed, 2 deselected
- Forced Python compilation of v0.44 source and runners: passed

### Deliberate regression deselections

- `tests/test_v038_access_generalization.py::test_freeze_builder_is_one_time_and_self_verifying` requires `validation/freeze_v038_source.py`, omitted from the inherited compact continuation bundle.
- `tests/test_v043_whole_loop_causal_closure.py::test_preoutcome_freeze_verifies_when_present` checks byte identity against the old v0.43 source seal. A v0.44 successor necessarily changes `pyproject.toml`, package version, exports, and runtime source.

Neither deselection concerns the v0.44 mechanism or its sealed evidence.

## Scientific boundary

The holdout is fresh with respect to seeds but remains a functional-development study in a synthetic family inherited from prior RRCT blocks. The controller does not receive successor relation labels, but paired probe correspondence and task structure remain supplied by the harness. No conclusion about phenomenal consciousness is licensed.
