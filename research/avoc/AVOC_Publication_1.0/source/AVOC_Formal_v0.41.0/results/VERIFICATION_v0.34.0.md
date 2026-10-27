# AVOC v0.34.0 — verification record

## Result

**PASS within the stated formal and bounded executable scopes.**

- Fresh local project compilation: **188 / 188 targets passed**.
- Complete theorem/lemma inventory and axiom audit: **1,812 / 1,812 passed**.
- New declarations: **60** across five proof modules.
- Deliberately false files: **97 / 97 substantively rejected**.
- Inherited non-audit AVOC modules: **161 / 161 byte-identical to v0.33**.
- Positive-source scan: no `sorry`, proof `admit`, project `axiom`, `native_decide`, or unsafe theorem-like declarations.
- Reported axiom union: only `propext`, `Classical.choice`, and `Quot.sound`.

The local build directory was deleted before the final rebuild.  The nine pinned external dependency caches were retained; this was not a fresh source rebuild of mathlib or an independent implementation of Lean's kernel.

## New source block

- `AVOC/AffineTerminal.lean`
- `AVOC/MultiLevelOperational.lean`
- `AVOC/AffineTerminalCodec.lean`
- `AVOC/CertifiedOperationalCatalogue.lean`
- `AVOC/OperationalExamples.lean`
- `tools/AffineTerminalMain.lean`
- `tools/execute_multi_level.py`

## Exact executable regression

`checks/test_operational_bridge.py` sent 120 requests through the actual Lean terminal entrypoint in one batch:

| Request class | Count |
|---|---:|
| Exact normalization | 32 |
| Cold certificate/deployment | 32 |
| Changed-offset warm certificate/deployment | 20 |
| Entry/minor reports | 30 |
| Malformed requests | 6 |

It independently checked 208 program/input executions, affine coefficients, determinant reports, per-call non-regression and exact rational payoff formulas.  Seed: `20260914`.

`checks/test_operational_policy.py` independently reconstructed the finite controller with Python `Fraction` arithmetic.  It matched both complete traces:

- cold-only catalogue: root value `391/2`, first action probe 0, realized branch net `-1`;
- warm catalogue: root value `14867`, first action reuse, realized net `14867`.

The warm catalogue's fixed cold expectation was `14804`.  The cold-only catalogue's fixed cold expectation was `257/2`.

## Formal interpretation

The model's terminal rewards are derived from proof-carrying deployments.  Every accepted deployment has exact behavioral equality with its source and no greater declared per-call tariff.  Infrastructure faults do not enter the algebraic report channel.

The runtime preconstructs checked terminal alternatives for every supplied hidden world.  It reports those setup charges separately from Bellman value.  Therefore this release does not claim that its current metareasoning process is net-optimal.

## Trust boundary

Lean 4.34.0-rc2, the pinned dependency binaries, compiler/interpreter, Python, JSON parsing, operating system and host remain trusted.  The Python factor proposer is not proved complete; accepted candidates are independently checked by Lean.  The finite runtime regression is implementation evidence, not a replacement for the universal Lean proofs.
