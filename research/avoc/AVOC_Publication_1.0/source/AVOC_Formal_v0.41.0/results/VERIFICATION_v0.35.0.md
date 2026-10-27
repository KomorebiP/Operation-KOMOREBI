# AVOC v0.35.0 verification record

## Result

**PASS within the declared finite model and executable-test scope.**

- Lean: `4.34.0-rc2`, commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`.
- mathlib: `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.
- New theorem/lemma declarations: **48**.
- Complete declaration inventory: **1,860**.
- Non-audit modules: **170**.
- Non-audit Lean source lines: **26,913**.

## Fresh local build

The local project build directory was deleted.  The 193 indexed local targets were rebuilt
against the nine exact pinned external dependency caches.

- Current local compilation targets: **193/193 passed**.
- Inherited non-audit proof modules: **166/166 byte-identical to v0.34**.
- External dependency pins: **9/9 matched**.

This was not a fresh source rebuild of mathlib or an independent Lean kernel verification.

## Axiom and source audit

`AVOC/FullAudit.lean` names all 1,860 declarations.  The exact expected name set was found.
The union of reported axiom dependencies is only:

```text
propext
Classical.choice
Quot.sound
```

The positive-source scanner found no `sorry`, proof `admit`, project-specific `axiom`,
`native_decide`, or unsafe theorem-like declaration.

## Deliberately invalid files

All **100/100** negative files were substantively rejected.  New cases attempt to:

- deploy the warm implementation before cache inspection succeeds;
- turn an infrastructure fault into a model report;
- refund the warm setup charge after the operation.

Import/setup failures and timeouts were not counted as mathematical rejections.

## Executable staged-controller regression

The actual Lean JSON entrypoint was compared with a separately written exact Python
`Fraction` dynamic program.

- Valid requests: **96**.
- Malformed, unsupported, or impossible requests: **8 rejected**.
- Stable action tie order, values, state transitions, budgets, status updates, and
  proof-derived setup/gross/net summaries agreed.

Headline results:

| Case | Choice | Bellman continuation value |
|---|---|---:|
| Certain warm and cold result, horizon 2 | inspect warm | 14,867 |
| Warm probability 1/2, cold certain, horizon 2 | generate cold | 14,804 |
| Horizon 1 | stop | 0 |
| After successful warm inspection | deploy warm | 15,000 |
| Budget 132 | stop | 0 |
| After failed warm inspection with remaining budget 63 | stop | 0 |

## Interpretation

The universal mathematical statements are established by Lean.  The bounded executable
regression supports the JSON adapter and concrete finite cases.  Success probabilities,
operation fees, and deployment counts are supplied model inputs, not empirical measurements.
The codec validates both certificates eagerly while constructing the typed model; physical
validation cost is not selected lazily by the current Bellman process.
