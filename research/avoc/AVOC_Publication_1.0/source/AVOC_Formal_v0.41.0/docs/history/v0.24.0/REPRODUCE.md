# Reproduce AVOC v0.24.0

Linux x86-64/WSL, Python 3.10+ with SQLite and fcntl, and the pinned portable kit:
Lean 4.34.0-rc2 commit 6a10ac8c22beadecabdbb0919c2b50214762f91d;
mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06. The nine external revisions
are in lake-manifest.json. This source ZIP does not include runtime/cache binaries.

## Check original bytes before regeneration

```bash
export AVOC_LEAN_KIT=/absolute/path/Komorebi_Portable_Lean_4.34.0-rc2
python tools/check_manifest.py
python tools/inventory_v024.py
python tools/verify_release.py --prepare
python tools/build_parallel.py --seconds 20 --workers 3
```

Repeat bounded build slices to 129/129 current targets. Do not repeat preparation
between slices. It removes only local outputs and verifies external revision pins.
The local compilation records include direct-import output hashes. Interrupted
checks and descendants must be recompiled rather than credited as successful.

```bash
python tools/verify_release.py --audit
python tools/verify_release.py --negative
```

There are 59 deliberate negative files. Use --start/--count slices when required.
Missing imports, timeouts or a missing diagnostic do not count as negative evidence.

The source pins delivered in durable_upgrade_source_pins.json protect the new
runtime's transitive local source closure and wrapper. The wrapper also checks
current compiled records. Do not run pin_durable_upgrade.py to bless arbitrary
edits. That is a release-preparation tool to use only after proof and build review.

## New durable component campaign

The run directory must be new, writable and protected. No old proof-store or
campaign database is migrated or overwritten.

```bash
python tools/durable_upgrade_campaign.py start --run-dir /tmp/avoc-upgrade-new --credits 100
python tools/durable_upgrade_campaign.py begin examples/durable_upgrade/bad.json --run-dir /tmp/avoc-upgrade-new --key bad-001 --expected-epoch 0
python tools/durable_upgrade_campaign.py finish --run-dir /tmp/avoc-upgrade-new --key bad-001
python tools/durable_upgrade_campaign.py begin examples/durable_upgrade/good.json --run-dir /tmp/avoc-upgrade-new --key good-001 --expected-epoch 2
python tools/durable_upgrade_campaign.py finish --run-dir /tmp/avoc-upgrade-new --key good-001
python tools/durable_upgrade_campaign.py invoke --run-dir /tmp/avoc-upgrade-new
```

The first candidate is rejected and retains its 3-unit fee. The second promotes
the threshold component with another 3-unit evaluation fee and 1-unit switching
fee. The fixed-workload endpoint net is 56. Invoke executes the persisted version.

Inspect and reconcile without changing campaign state:

```bash
python tools/durable_upgrade_campaign.py inspect --run-dir /tmp/avoc-upgrade-new
```

A committed finish whose response was lost may be repeated using the same key.
It returns the existing disposition without another reservation or switch. A
pending prepaid evaluation may instead be abandoned:

```bash
python tools/durable_upgrade_campaign.py abandon --run-dir /tmp/avoc-upgrade-new --key some-pending-key
```

Abandonment refunds nothing. A new evaluation needs a fresh key and the current
expected epoch from inspect. Same-key replay needs the SAME original request and
expected epoch. An evaluated result cannot be abandoned after promotion.

The authoritative database is campaign.sqlite3. authority.json is the frozen
configuration/environment descriptor. Logs under diagnostics are nonauthoritative.
Do not edit either authority or database to erase charges or change the component.
Inspection and replay still cost physical computation.

## Bounded independent regressions

The test suite creates fresh directories under results/v0.24.0/tests and refuses
to overwrite existing ones. To rerun the packaged tests, first preserve/rename that
recorded tests directory, then create fresh runs. Do not resume copied historical
SQLite test databases on a different host.

```bash
python checks/test_durable_upgrade.py --differential
python checks/test_durable_upgrade.py --start 0 --count 23
```

The differential test sends requests to the actual Lean batch entrypoint and
compares with an independently implemented Python state machine. Live tests invoke
actual Lean processes and SQLite writes, with test-only os._exit(97) hooks at
reservation/settlement/abandonment crash points. No crash hook is a deployment CLI
option. Tests also cover omitted history, forged dispatch, stale epochs, same-key
conflicts, tariffs, credit, abandoned charges and cooperative writer exclusion.

## Collection and packaging

```bash
python tools/summarize_v024.py --baseline /path/to/AVOC_Formal_v0.23.0.zip
python tools/record_v024_audit.py --baseline /path/to/AVOC_Formal_v0.23.0.zip
python tools/audit/validate_computation_manifest.py results/v0.24.0/computation_manifest.json --root .
python tools/package_v024.py --output /chosen/AVOC_Formal_v0.24.0.zip
```

The inherited manifest validator is a v1-only local adaptation, not the full
installed v2 audit runner. Its metadata verification does not prove interpretation.
Current per-file compilation logs and exact-name axiom reports supply proof-run
provenance. The final source ZIP excludes runtimes, local .olean outputs, and caches.
