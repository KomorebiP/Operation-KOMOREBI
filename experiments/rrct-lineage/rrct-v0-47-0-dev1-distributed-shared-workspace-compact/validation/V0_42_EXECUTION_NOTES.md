# RRCT v0.42 Execution Notes

## Scope

This block targeted the causal-decorativeness gap in temporal self-identity. Development began from the frozen v0.41.1 compact continuation bundle. Historical evidence files were not modified.

## Implemented runtime changes

1. Added `CausalSelfModelNecessityUnifiedCausalLoop`.
2. Added a precommitted intervention on an internally recognized return.
3. Added exact nonmatching-source enforcement for the substitution control.
4. Added fail-closed behavior when no nonmatching grounded source exists.
5. Added pre-outcome counterfactual, intervention, commit-event, and action-authorization receipts.
6. Added a complete receipt-chain validator with cross-digest, signature, identity, episode, source-key, and temporal-order bindings.
7. Added a streaming path to the inherited post-change runner so rows can be sealed without retaining them in memory.
8. Preserved v0.41 behavior for callers that do not use the new intervention parameters.

## Compact evidence execution

The executable adjudication consumed 24 frozen summary artifacts:

- 4 seeds
- 6 conditions per seed
- keyed, withheld, and generic history
- true recurrence and same-key null-lure worlds

The exact input set is bound by `v0.42.0_causal_self_model_necessity/INPUT_SUMMARY_SHA256.json`. This is a post-hoc packaging-integrity manifest, not a prospective scientific preregistration.

Executed status:

`V042_SUMMARY_LEVEL_CAUSAL_NECESSITY_ENDPOINTS_MET`

All eight declared endpoints passed. The primary contrasts use the first recognized return, where the compact summaries establish an identical pretarget temporal episode fingerprint. Later returns are included as replication evidence but are not described as strictly pretarget-yoked.

## Development campaign attempts

Several fresh end-to-end development runs were attempted before selecting the compact adjudication path:

- A full 10,560-transition reference arm did not return a summary within the initial execution window.
- A reduced 1,840-transition schedule completed in approximately 20.76 seconds but produced no discovered boundary or temporal episodes. It was scientifically uninformative and is not counted as positive evidence.
- A 3,520-transition schedule was attempted under reduced retention and permutation settings. It did not return a completed summary within either a ten-minute or a fifteen-minute execution window. Incomplete runs are not treated as evidence.

These attempts identified runtime cost as an engineering barrier to a fresh full-duration campaign. They did not produce a negative scientific result. The compact retrospective adjudication and live mechanism tests are kept distinct from a future prospective campaign.

## Final executed checks

### Focused v0.42 tests

Command:

```bash
PYTHONPATH=src python -m pytest -q tests/test_v042_causal_self_model_necessity.py
```

Result:

`7 passed`

The tests cover:

- internally triggered policy-specific intervention
- nonmatching-source enforcement
- fail-closed source absence
- wrong-source quarantine after consequence mismatch
- direct commit and authorization bindings
- rehashed but misbound receipt rejection
- compact causal adjudication
- post-manifest summary tamper rejection
- row streaming without retention

Some test functions cover more than one item.

### Downstream focused regression

Command:

```bash
PYTHONPATH=src python -m pytest -q tests/test_v036_unified_causal_loop.py tests/test_v037_post_change_closure.py tests/test_v038_access_generalization.py tests/test_v039_autonomous_self_diagnosis.py tests/test_v040_robust_reflexive_diagnosis.py tests/test_v041_temporal_self_identity.py tests/test_v042_causal_self_model_necessity.py -k "not freeze_builder_is_one_time_and_self_verifying"
```

Result:

`85 passed, 1 deselected`

The deselected v0.38 check requires `validation/freeze_v038_source.py`, which is absent from the supplied compact continuation bundle.

### Compilation and import

`python -m compileall -q src/rrct validation/run_v042_causal_necessity_analysis.py` passed.

The installed package imported as `rrct 0.42.0.dev1`, including `validate_self_model_receipt_chain`.

### One-command reproduction

`./RUN_V042_CAUSAL_NECESSITY.sh` completed successfully, regenerated the analysis, and returned `7 passed`.

## Historical-suite limitation

A complete `pytest` collection is impossible from this compact bundle because these older validation modules are absent:

- `validation.aggregate_v029`
- `validation.freeze_v030`
- `validation.freeze_v031`

After excluding the three associated test modules, the first historical-suite failure occurred after 181 passing tests because this file is absent:

- `validation/V0_36_LINEAGE_AND_SEED_REGISTRY.json`

Older immutable-freeze tests may also reject expected v0.42 source changes or require omitted freeze-builder assets. These failures must not be suppressed or misreported as a clean full-suite pass.

## Claim boundary

The executed result supports a causal role for keyed temporal self-history in one bounded synthetic grounding subsystem. It does not establish whole-system self-awareness or phenomenal consciousness. A fresh prospective multi-seed v0.42 campaign remains required for a stronger whole-runtime claim.
