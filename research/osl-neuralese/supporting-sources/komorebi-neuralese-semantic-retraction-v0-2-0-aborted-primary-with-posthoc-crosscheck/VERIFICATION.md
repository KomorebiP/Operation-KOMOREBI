# Verification Record

This record separates artifact integrity from scientific validity. The frozen primary bundle is expected to be rejected because execution aborted before its commit. The independent cross-check and projector forensics have their own narrower validity boundaries.

## Component disposition

| Component | Integrity | Scientific status |
| --- | --- | --- |
| Frozen protocol and receipts | Verified | Prospectively frozen before spend |
| Spend receipt | Verified and byte-identical in both locations | Bank permanently spent |
| Synthetic exact control | Verified PASS | Plumbing control only |
| Primary learned bundle | Verified incomplete | `ABORTED_INVALID_NO_COMMIT`; not evaluable |
| Independent cross-check | Verified complete | Posthoc finite-bank sensitivity |
| Projector diagnostic | Verified complete | Post-spend parameter-only forensics |

## Frozen trust roots

| File or external source | SHA-256 |
| --- | --- |
| `ANALYSIS_PROTOCOL.md` | `d55c7b180e8d8661f9da75ace95af179e274e2ad0faeebae51ae3e86eacf6e56` |
| `THEORETICAL_FRAMEWORK.md` | `a8686cec2d4b7769475f6ee118731530f12abe87bd433fb654d6cc4098bc1f6c` |
| `PROTOCOL_RECEIPT.json` | `b8bc2b969d5e378ef9dd5f98f46e4884aaad67669d9f55e8d369e4fd074dbaf2` |
| `primary_probe/run_semantic_retraction_probe.py` | `6bef14a6b7b0db72752f8467e41b9f144af9766d40d5cd739733a6315c8b0cdf` |
| `primary_probe/test_semantic_retraction_probe.py` | `9dcaed3f9fedb5b483a39c795fbcabc0cd58ceb7201348a27218d15908ff4bac` |
| `primary_probe/PROTOCOL.json` | `24a1abdf3a6898cad75a62cd7ebf18a5456a9913e1802037236a165ae4d959c2` |
| `primary_probe/MANIFEST_DRY_RUN.json` | `5feaba6abc4ba70f44e027f4f8675f81726e24b5ae96b41f7fb6ce35752d20e8` |
| `primary_probe/STATIC_REVIEW_PASS.json` | `c574604cb01cd6838264a3edb16ffdaddb3428040fd614a7d985bc76ed7c8def` |
| Independent protocol | `e53cf8a4e1e5c300b43b91b01c86c81910c176550dfdda7c487cb79e7f9bdd72` |
| Independent implementation | `90d21fc67d93841f2cfb26f03cd6789f1d838b277705755e6b0b51098d549daf` |
| Independent tests | `44546dfc5c303c8a10e4a39c00298d9e047596c7dccdb8c5d9271358c837dfae` |
| Independent freeze receipt file | `e007119aa5f2d4aa280670216d420be951fe9b40febcb842e0760cf0ac2528ad` |
| External sealed v0.4.0 archive | `4132faa934e94647ec267c0140240397b459c68b6770e95edc30144c39f3662d` |
| Extracted source `MANIFEST.json` | `10f9b59dc7a233dbccad772fa223cd51a8866c18e799c9227c7c3d1a2b5dab8a` |

The root protocol receipt's internal canonical digest is `9bd160d29275a5fb7a304c1c8c05f28b86a3c9c312b88b1c78b6db194edd5442`. The dry-run manifest's internal freeze digest is `0d61dda294dd53f54832f3fddf5efd941ffc0cfd79a109a4dce7618a946cee1f`.

## Primary execution audit

The authoritative spend marker and bundle copy are byte-identical, 2,259 bytes each, SHA-256 `65b399852d338569e4775bbbe7177a94094619d8acd70f8c72017e79843f9c01`. Their canonical internal receipt digest recomputes to `2b184f45835a8c4833490ec537599be780aa1438a6efc327a89d24249e9b6d07`. Every bound protocol, implementation, test, source, and receipt hash matches the frozen files.

`EXACT_CONTROL.json` is valid JSON, contains no learned-checkpoint source, reports `audit.pass=true`, and has SHA-256 `2d19c60abd07f12cce7a96bfd768c9b246794413b34eb6d995d6c1a24c84d993`.

The result directory has zero learned shards, an empty real `checkpoints/` directory, no symbolic links, and no temporary remnants. `RUN.json`, `MANIFEST.json`, and `COMMIT.json` are absent. The production verifier rejects it with:

```text
RuntimeError: result bundle has missing or extra root entries
```

That rejection is the correct fail-closed outcome. It is not an overall verification failure and does not imply a negative scientific result.

## Independent cross-check audit

`independent_crosscheck/RESULTS.json` is 22,021,536 bytes with SHA-256 `c2363561e845cdfe43e9302558f934065623fb246b68d28e3ec35ae4338c9faf`.

The read-only audit rehashed the archive, seal, null bank, all 12 checkpoint files, payload identities, source and contract digests, state dictionaries, normalized anchors, and decoders. It validated:

- the exact 4-by-3 checkpoint census;
- 216 condition blocks;
- 6,696 condition-by-suffix cells;
- 846 tensor receipt objects;
- 44,892 exact fractions and 29,748 numeric summaries;
- zero nonfinite numbers and zero undefined scored diagnostics.

The 324 JSON null values occur only in declared not-applicable raw-arm orthogonality fields or denominator-zero conditional rates. All files were unchanged, and no learned evaluation was rerun during validation.

## Post-spend projector diagnostic

`postspend_diagnostics/POSTSPEND_PROJECTOR_DIAGNOSTIC.json` is 68,054 bytes with SHA-256 `6d25f0bd44fae2d4bf61cd7ad40d4ed1a8dae83e7b32aa2747b76968a3192ddd`. Its generating script has SHA-256 `01d00bf6a7492642408b72209fbd02add2f16bf25cab8b8b8b024bc4d7217893` and is bound inside the result.

The script loaded sealed checkpoint parameters and inspected only anchors, metrics, and projector geometry. It did not construct or use evaluation contexts, paths, continuations, rollouts, logits, or behavioral outputs. Its 12-cell result reports:

- frozen widened default rank 12 in every cell;
- native or explicit float32-aware rank 8 in every cell;
- every non-rank audit conjunct passing in every cell;
- classification `DTYPE_TOLERANCE_FALSE_REJECTION`.

This diagnosis was designed and executed after spend. It cannot rehabilitate the primary run.

## Test execution

Final checkpoint-free test results:

- Primary suite: 55/55 passed in 87.872 seconds.
- Independent suite: 18/18 passed in 4.990 seconds.
- Independent `--validate-only`: `valid=true` with matching frozen receipt.
- JSON parsing and diagnostic-script compilation: passed.
- Primary incomplete-bundle verification: rejected as expected.

See `TEST_RESULTS.txt` for commands and boundary notes.

## Pre-spend freeze correction

Before bank spend, an initial candidate terminal manifest/receipt set was rejected because Markdown trailing-space bytes did not match its candidate hash declarations. Those invalid candidate artifacts were removed before any learned evaluation-bank access. The final hashes listed above were regenerated from the exact bytes, passed the static/root receipt gates, and are the ones bound into the durable spend receipt. This pre-spend correction has no learned-outcome dependence.

## Reproduction boundary

The source archive is intentionally referenced by hash rather than duplicated. Checkpoint-free unit tests and static validation may be rerun. The partial primary bundle may be verified only to confirm its expected rejection. Do not rerun or resume the primary learned command; the bank is spent. Any future learned analysis using the same bank must be labeled posthoc.
