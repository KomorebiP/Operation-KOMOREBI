# RRCT v0.47 Execution Notes

## Development

Exposed development used seeds `47011`, `47012`, `47013`, and `47014` with 72 trials per mode. All 28 declared development endpoints passed.

One substantive pre-freeze repair was made. The first feedback challenge allowed the recurrence-cut controller to guess the second decision occasionally. The challenge was changed so one coarse round forms a coherent but incorrect consensus while three evidence rounds recover the correct joint state. No challenge label is available to the runtime.

One pre-freeze bookkeeping collision was also corrected. The general compact analysis summary and the frozen release summary initially shared the filename `V0_47_FROZEN_SUMMARY.json`. They now use separate files:

- `distributed_shared_workspace_summary.json`
- `V0_47_FROZEN_SUMMARY.json`

The focused suite passed after both corrections, and the exposed cohort reproduced byte for byte.

## Prospective order

1. The protocol and 28 endpoints were fixed.
2. Fresh seeds were selected without evaluating candidate outcomes.
3. The exact source was sealed in a 90-file pre-outcome manifest.
4. The holdout was executed once.
5. The complete analysis replayed exactly.
6. The source seal was reverified after outcome generation.

Holdout seeds:

```text
161625576
156878792
822521852
294523660
```

Pre-outcome seal SHA-256:

```text
68ce68565078cea313462084a10b0f49b2d4064a1e76fd3629dc205a59790ade
```

## Frozen result

`V047_FROZEN_ENDPOINTS_MET`

- 384 unique dyadic cases
- 3,456 matched decisions
- 28 of 28 endpoints passed
- every receipt chain valid
- no runtime row reported evaluator-label use
- no survival, identity, or continuity reward

## Determinism

The exposed cohort and the complete frozen analysis reproduced exactly under the tested environment. The worlds are pseudorandomly generated from recorded integer seeds. Fixed code, inputs, configuration, dependency versions, and numerical environment produce fixed results.

Bit-identical replay across arbitrary BLAS or hardware implementations is not universally guaranteed, although the release also uses numerical thresholds with large observed margins.

## Validation

Completed post-outcome checks:

- focused v0.47: `10 passed`
- v0.32 plus v0.42–v0.47 direct successor line: `56 passed, 4 deselected`
- v0.36–v0.40 successor-compatible line: `64 passed, 1 deselected`
- v0.41–v0.47 successor-core line: `68 passed, 4 deselected`
- Python AST parse: `188 files`

The deselected tests are immutable predecessor freeze checks whose intended behavior is to reject source and metadata changes in later releases.

A broader v0.41 campaign-and-runtime command did not complete within the 600-second execution window and produced no pytest summary. It is not counted as passed or failed.

A full historical collection is not claimed because this compact lineage omits:

- `validation.aggregate_v029`
- `validation.freeze_v030`
- `validation.freeze_v031`
- `validation/V0_36_LINEAGE_AND_SEED_REGISTRY.json`
- `validation/V0_36_DEVELOPMENT_PROTOCOL.md`
- `validation/freeze_v038_source.py`

## Interpretation limits

The benchmark is intentionally engineered. The common semantic factors exist in both agents' synchronized trajectories, and task decoders are supervised. The shared atlas itself does not receive the hidden factor labels, but the evaluator later uses them to score recovery.

The message-shuffle mode illustrates an important distinction: a structurally complete distributed workspace can carry incorrect content. The reported closure score summarizes architecture, not semantic truth.

The partner-remapping result requires new synchronized calibration trajectories. It does not show zero-shot universal communication.

No result establishes shared phenomenology or a single awareness spanning both agents.
