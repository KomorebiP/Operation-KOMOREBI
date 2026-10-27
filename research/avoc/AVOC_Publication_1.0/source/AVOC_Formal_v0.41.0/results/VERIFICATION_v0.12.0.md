# AVOC Formal v0.12.0 verification record

- Lean: `leanprover/lean4:v4.34.0-rc2`
- mathlib: `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`
- Project version: `0.12.0`
- Non-audit theorem/lemma/proposition/corollary declarations: **512**
- Non-audit definition/structure/inductive/abbreviation declarations: **211**
- Non-audit AVOC Lean source lines: **9,817**
- Non-audit modules: **58**

## New v0.12 source block

- `AVOC/QRateDistortion.lean`: 12 theorem-like declarations, 8 definition-like declarations, 289 lines.
- `AVOC/QRateDistortionFinite.lean`: 20 theorem-like declarations, 4 definition-like declarations, 283 lines.
- `AVOC/QRateDistortionExamples.lean`: 8 theorem-like declarations, 2 definition-like declarations, 85 lines.
- `AVOC/HorizonDecisionRateDistortion.lean`: 6 theorem-like declarations, 5 definition-like declarations, 132 lines.
- `AVOC/QValueBridge.lean`: 5 theorem-like declarations, 1 definition-like declaration, 85 lines.

Total new theorem-like declarations: **51**.

## Build

The incremental aggregate library passed before clean verification:

```text
Build completed successfully (1078 jobs).
```

A `lake clean` was then followed by resumable bounded build slices. Each slice resumed the same build graph only after the preceding bounded child had stopped. No concurrent clean rebuild was used.

The final clean slice rebuilt all new Q-signature modules and reported:

```text
Build completed successfully (1078 jobs).
```

A subsequent cached confirmation also returned:

```text
Build completed successfully (1078 jobs).
```

## Post-clean checks

- `AVOC/Audit.lean` with `-DwarningAsError=true`: **PASS**.
- `AVOC/QRateDistortion.lean`: **PASS**.
- `AVOC/QRateDistortionFinite.lean`: **PASS**.
- `AVOC/QRateDistortionExamples.lean`: **PASS**.
- `AVOC/HorizonDecisionRateDistortion.lean`: **PASS**.
- `AVOC/QValueBridge.lean`: **PASS**.
- Source scan for `sorry`, `admit`, AVOC-defined `axiom`, and unsafe theorem-like declarations: **zero hits**.

## Deliberately false negative tests

All **14 / 14** files under `tests/negative/` fail compilation as required.

The new `FalseScalarValueSufficesForDecision.lean` tries to equate exact Q-signature and scalar-value context complexity in the crossed-action example. After rewriting with proved exact values, Lean reaches:

```text
⊢ 2 = 1
```

and rejects the file.

## Axiom boundary

No AVOC-specific axiom declaration is present. The newly audited Q-signature declarations report only standard Lean/mathlib foundations such as `propext`, `Classical.choice`, and `Quot.sound` where applicable.

The exact minimum `N^Q_η` uses finite classical choice / `Nat.find`; this is a proof-existence construction, not an empirical claim about production AI contexts.

## Formal interpretation boundary

v0.12 proves exact finite context cardinality for rational complete action/Q signatures under coordinatewise absolute error. The scalar maximum is proved to be a projection of the richer signature and may require strictly fewer codes. The release does not provide a greedy exact algorithm for general multidimensional signature covering, a Shannon information-theoretic coding theorem, or a token-count guarantee for real LLM context windows.
