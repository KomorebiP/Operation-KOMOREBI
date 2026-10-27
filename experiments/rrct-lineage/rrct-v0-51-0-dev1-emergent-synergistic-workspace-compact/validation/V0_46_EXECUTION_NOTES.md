# RRCT v0.46 Execution Notes

## Pre-outcome sequence

1. The synthetic world, eight matched modes, ten scenarios, 26 endpoints, tests, protocol, and dependency wheel were completed on exposed development seeds 46011 through 46014.
2. Development produced 640 unique cases and 5,120 matched decisions, with 26/26 exposed endpoints met.
3. Four holdout seeds were selected by SHA-256 namespace expansion without executing candidate outcomes: 166549004, 870900869, 237190449, 229756328.
4. A 93-file source seal was written before holdout execution.
5. The source seal verified immediately before opening the holdout.

Pre-outcome freeze SHA-256:

```text
f5e1dfe7a9e9505376ee2b504ba7ce34c05dcd67fd519044d832f476ab28d21c
```

## Frozen execution

The holdout produced 640 unique cases and 5120 matched architecture decisions. All 26 frozen endpoints passed.

Canonical analysis SHA-256:

```text
8242bf0625ec9cd8c6359d1877c156569757c1a53990e9049e48ced389b2e85d
```

Deterministic replay returned exact object equality against the stored analysis. The 93 sealed files remained byte-identical after holdout execution.

## Post-outcome audit

The audit is not counted as a frozen endpoint. It verified:

- exact source-seal preservation;
- result hash binding;
- no scenario-label literals in the sealed core controller;
- exact behavioral equality when the recurrence context key was renamed from an opaque string to an adversarial scenario name;
- ownership dissociation for identical workspace content with different provenance;
- zero explicit identity, continuity, and survival rewards;
- no declared valence model.

The label audit is evidence of the implemented code path, not a formal proof of complete noninterference.

## Test matrix

- Focused v0.46: **13 passed**
- v0.43-v0.46 successor line: **38 passed, 3 predecessor-seal tests deselected**
- v0.36-v0.40 runtime line: **64 passed, 1 historical freeze-builder test deselected**
- v0.41-v0.46 runtime line: **96 passed, 3 predecessor-seal tests deselected, 2 subtests passed**
- Syntax validation: **178 Python files parsed**

Six warnings in the v0.41-v0.46 line concern Python 3.13's warning about `fork()` from a multithreaded process in an inherited multiprocess race test. The tests passed.

A complete historical-suite pass is not claimed because the compact inherited lineage omits older official-harness modules and protocol/freeze assets, and predecessor source-seal tests are not applicable to a successor tree that intentionally modifies source.

## Interpretation boundary

No model in this block has pleasure, pain, distress, self-preservation, shutdown aversion, autonomous resource acquisition, or an intrinsic identity objective. Prediction error is used only as a bounded informational signal for later evidence allocation.

## Wheel verification

The wheel `rrct_prototype-0.46.0.dev1-py3-none-any.whl` was built without network dependency resolution and installed with `--no-index --no-deps` into an isolated target. The installed package reported version `0.46.0.dev1`, recovered the synthetic workspace projector, and validated every smoke-cohort receipt chain.

Wheel SHA-256:

```text
afa0df227d23150c8f3cc6129afa261a3c0e1dc8ba68c1b03a185c8692704120
```

Direct zipimport of the unopened RRCT wheel is not a supported execution mode because the nested Komorebi wheel must be materialized as a file.
