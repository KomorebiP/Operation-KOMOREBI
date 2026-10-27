# AVOC v0.24.0 — verification record

Recorded UTC: 2026-09-13T17:09:00.480986+00:00

## Actual result

- 52 new theorem/lemma declarations in four modules.
- 1236 complete exact-name axiom reports, all passing.
- 129/129 current local targets passed with warnings as errors.
- 59/59 deliberately invalid proof files substantively rejected.
- 113/113 inherited non-audit modules are byte-identical to v0.23.
- Positive-source shortcut/custom-axiom/native/unsafe scan: zero hits.
- Allowed axiom union: propext, Classical.choice, Quot.sound.

The input source ZIP SHA-256 is `6ab183f088c8dca7bed64e79e067511a59d73bf45c1ab43ba8ff9d3d8e90a694`. Its original 5,050 payload
hashes matched before development. No inherited positive theorem source was changed.
The aggregate and complete audit were regenerated to include the new modules.

## Build scope

The local .lake/build directory began empty. All inherited targets were compiled
and every final new target plus aggregate was checked after its source was final.
The collector compares current source, output, direct-import and log hashes.
Nine external dependency pins matched. The runtime assembly checked all seven
parts and the combined compressed archive SHA-256. Cached external dependencies
were retained. This is not a fresh source rebuild of mathlib, independent kernel,
or proof of the OS/compiler/runtime implementation.

Lean: 4.34.0-rc2, commit 6a10ac8c22beadecabdbb0919c2b50214762f91d.
mathlib: aeb72f1e9981b6d35b426b16dca7759be3e7ba06.
Python: 3.13.5. SQLite: 3.46.1.

## Independent oracle

The actual Lean batch entrypoint was compared against an independently written
Python reserve/settle/abandon state machine on 1404 requests.
There were 519 accepted cases and 885
expected rejections. Generation used Python Random seed 240024 across nine credit
settings and twelve bounded trajectories per setting, including corrupted final
checkpoints. The collector independently rechecks every retained request/output
against the oracle rather than only trusting a PASS flag.

Requests hash: `5e837b95f6e0c3c1cbb1647434547ff4ba2b80ee40842f9596943cc941088da4`.
Outputs hash: `23fb881cc7ce651a8a205169e4464bd310a417496d1276b2c6c6bfcfa3351753`.

## Real protected-store tests

All 23 scenarios passed. 9 inject actual
process exit with os._exit(97), bypassing ordinary cleanup, during reservation,
evaluation, transaction writes, commit, acknowledgement/response and abandonment.
Interrupted transactions are reopened through the delivered adapter. These are
process-exit tests, not electrical power-loss experiments or arbitrary schedules.

Other scenarios check repeat keys, stale complete parent epochs, paid rejection,
abandoned reservations, switch-credit exhaustion, unfunded requests, omitted
canonical events, forged dispatch and snapshots, altered frozen authority,
request/event mismatch, changed objectives and cooperative writer exclusion.

The normal run retains the paid bad candidate, promotes threshold, persists one
revision and one switching tariff, and actually invokes threshold on reopen.
After a crash immediately after promotion commit, inspection finds the promotion;
repeated finish changes neither journal nor charges. Pure replay validation still
runs and is not claimed free or exactly-once physical work.

## Non-claims

The concrete catalogue and tariffs are inherited symbolic objects. No autonomous
candidate generation, general source installation, empirical LLM improvement,
physical speedup or net-optimal improvement search is demonstrated. SQLite/host
atomicity and faithful Python projection remain trusted implementation boundaries.
The old artifact-file and retry/crash suites were not rerun and remain historical.

## Evidence locations

`summary.json`, `source_counts.json`, `full_axiom_audit.log`, current `clean_*.json`,
`negative_*.log`, `tests/*.json`, `demo_durable_promotion.json`, and the source-pinned
runtime/environment records contain the actual current evidence. Counts include
helper lemmas and concrete examples rather than independent discoveries.
