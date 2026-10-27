# Neuralese Semantic Retraction v0.2.0

Author: Komorebi P.

This archive preserves a prospectively frozen primary execution that **aborted after spending its evaluation bank and before publishing any learned checkpoint shard**. The primary result is `NOT EVALUABLE`; it must not be presented as a positive or negative hypothesis result.

It also contains two explicitly separate post-spend artifacts:

- a completed independent NumPy sensitivity cross-check on its frozen, previously exposed null bank;
- a parameter-only projector diagnostic that explains the primary abort without using behavioral evaluation inputs.

Start with [REPORT.md](REPORT.md) for the scientific interpretation and next-study design. [PRIMARY_ABORT_RECORD.json](PRIMARY_ABORT_RECORD.json) is the machine-readable execution disposition, while [VERIFICATION.md](VERIFICATION.md) records the validation boundary and commands.

## Status at a glance

| Artifact | Status |
| --- | --- |
| `primary_probe/RESULTS.bundle` | Invalid partial bundle; no `COMMIT.json` |
| Primary evaluation bank | Irrevocably spent; no prospective rerun or resume |
| `EXACT_CONTROL.json` | Passed, checkpoint-free |
| `independent_crosscheck/RESULTS.json` | Complete posthoc finite-bank sensitivity |
| `postspend_diagnostics/POSTSPEND_PROJECTOR_DIAGNOSTIC.json` | Complete parameter-only forensics |

## Important use boundary

Do not rerun `--execute-learned` and do not add `RUN.json`, `MANIFEST.json`, `COMMIT.json`, or checkpoint shards to the partial primary bundle. The runner's spend firewall will refuse a same-bank prospective rerun; deleting the marker would not restore prospective status.

The cross-check and forensics do not support a universal quotient, global bisimulation, architecture-independent Neuralese, or absence of residual holonomy.

## Contents

- `ANALYSIS_PROTOCOL.md` — frozen primary analysis protocol.
- `THEORETICAL_FRAMEWORK.md` — semantic-retraction framework and claim hierarchy.
- `PROTOCOL_RECEIPT.json` — root freeze receipt.
- `primary_probe/` — frozen primary implementation, tests, receipts, and untouched partial bundle.
- `independent_crosscheck/` — independently frozen NumPy protocol, implementation, tests, and result.
- `postspend_diagnostics/` — clearly labeled parameter-only forensic script and result.
- `REPORT.md` — integrated scientific report and recommended next block.
- `VERIFICATION.md` and `TEST_RESULTS.txt` — reproducibility and observed checks.
- `SHA256SUMS.txt` — package-file checksums.

The sealed v0.4.0 source archive is referenced rather than duplicated. Its required SHA-256 is `4132faa934e94647ec267c0140240397b459c68b6770e95edc30144c39f3662d`; its extracted `MANIFEST.json` SHA-256 is `10f9b59dc7a233dbccad772fa223cd51a8866c18e799c9227c7c3d1a2b5dab8a`.
