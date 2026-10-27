# v0.3.0 release status

Author: Komorebi P.  
State: `ARMED_PROSPECTIVE_EVALUATION_UNSPENT`  
Release label: `ARMED_UNSPENT_CAPACITY_GATED`

## Outcome boundary

There is no v0.3 learned-checkpoint finding in this release. The only v0.3 behavioral execution was a public, exact-D4 synthetic fixture. The production fresh bank was drawn once, sealed, independently regenerated, and materialized by the runner, but it was never applied to a learned checkpoint. The bundled immutable v0.2 lineage ZIP contains historical v0.2 spent/aborted outputs solely as provenance.

Accordingly, this release establishes procedural readiness, not whether the semantic-retraction hypothesis passes or fails.

## Gap closed before the draw

The pre-draw audit found that `DESIGN_COMMIT.json` named 14 artifact hashes while the entropy sealer directly verified only 9. The five unverified entries were the lifecycle test, projector test, parameter-preflight receipt, synthetic-test receipt, and spent-registry builder.

Before any production entropy existed, the sealer and tests were amended to:

- verify all 14 frozen artifacts and reject extra unbound design fields;
- cross-bind protocol implementation, preflight, synthetic, scientific-boundary, and parent-lineage receipts;
- require a canonical, passing, bank-free parameter preflight;
- require a canonical, passing, checkpoint-free and entropy-free synthetic receipt;
- prove with coherent-rehash negative tests that a failed preflight or entropy-using synthetic receipt cannot reach the random draw.

The dependency chain was then regenerated in order: synthetic receipt, protocol, protocol freeze receipt, and design commit. The final design commit validated all 14 artifacts before the sole production draw.

## Test and preflight evidence

| Check | Result |
|---|---:|
| Factorial tests | 29/29 PASS |
| Fresh-bank tests | 38/38 PASS |
| Lifecycle tests | 14/14 PASS |
| Projector-semantics tests | 3/3 PASS |
| Total checkpoint-free tests | 84/84 PASS |
| Parameter-only checkpoint preflight | 12/12 authenticated; PASS |
| Full-shape synthetic packed evidence | PASS |
| Full-shape synthetic primary checks | 190 |
| Synthetic prototype usability | true |
| Synthetic repair superiority | `NOT_EVALUABLE_LOW_NATIVE_ERROR` |

The synthetic repair result is intentionally non-evaluable because the exact compiler has insufficient native error. It is not evidence of repair superiority.

## Fresh-bank evidence

| Property | Value |
|---|---|
| Bank ID | `96f86194dde85e15d55f1b886707bd97f85087cd2f4c7e55ae095e4093d671bc` |
| Bank SHA-256 | `358db4d74d8728ee88305eede415f8f351fa26d02f1e08efd3dd2ceae9dbda1c` |
| Draw receipt SHA-256 | `5bc4455c97814ea1000f188d2c367c6f67eca109739e9bcb12616427ded190b1` |
| Seal receipt SHA-256 | `025e37ba4d9aba3312b138316d8054ed726e22d3d8dc19105c6c10bd0be698cf` |
| Calibration/evaluation contexts | 64 / 64 |
| Calibration/evaluation prefixes | 8 / 8 |
| Prefix length | 64 |
| Split disjointness | exact PASS |
| Prior-bank exclusions | PASS |
| Evaluation spent | false |

## Capacity gate and continuation

The runner requires `2,147,483,648` free bytes before reserving a 1 GiB result member and a 64 KiB commit member. The observed free capacity after arming was `1,189,912,576` bytes. No v0.3 reservation, spend marker, checkpoint evaluation, result member, or terminal commit was created.

Continuation must preserve these invariants:

1. Use NumPy `2.3.5` and the exact sealed v0.4 source archive (`4132faa934e94647ec267c0140240397b459c68b6770e95edc30144c39f3662d`) plus its extracted root.
2. Re-run only read-only `fresh_bank.py verify`, runner `--validate-only`, runner `--status`, and `verify_execution_armed()` checks before execution.
3. Confirm free capacity meets the frozen minimum and physical reservation succeeds before spending.
4. Run the learned path at most once. The spend marker must be durably published before the first fresh-bank checkpoint evaluation.
5. Accept a result only when packed evidence recomputes, the staged result verifies, and `COMMIT.json` is written last.

The source checkpoint archive and extracted checkpoints are provenance inputs, not bundled in this release.
