# Reproduce AVOC v0.23.0

Linux x86-64/WSL, Python 3.10+, Lean 4.34.0-rc2 commit
`6a10ac8c22beadecabdbb0919c2b50214762f91d`, mathlib
`aeb72f1e9981b6d35b426b16dca7759be3e7ba06`, and the nine dependency pins
in `lake-manifest.json`. The source ZIP excludes runtime and binary caches.

## Original integrity, then local rebuild

```bash
export AVOC_LEAN_KIT=/absolute/path/Komorebi_Portable_Lean_4.34.0-rc2
python tools/check_manifest.py
python tools/inventory_v023.py
python tools/verify_release.py --prepare
python tools/build_parallel.py --seconds 12 --workers 4
```

Repeat the bounded build command until all 123 targets have passed. Do not prepare
again between slices. Preparation deletes only the local build, not the external
cache. The updated helper records direct-import hashes and invalidates descendants
of changed sources; old logs are not valid evidence for new compiled dependencies.

```bash
python tools/verify_release.py --audit
python tools/verify_release.py --negative
```

There are 55 deliberate negative files. On capped hosts use --start/--count slices.
A timeout or missing import is not a mathematical negative result.

## Run the protected, read-only upgrade campaign

```bash
python tools/run_upgrade_campaign.py examples/upgrades/promote.json
python tools/run_upgrade_campaign.py examples/upgrades/costly_search.json
python tools/run_upgrade_campaign.py examples/upgrades/hostile_requests.json
python tools/run_upgrade_campaign.py examples/upgrades/no_switch_credit.json
```

The wrapper invokes actual Lean `UpgradeRuntime.execute`, checks protected source
pins and current compiled-target hashes before and after, and never edits the live
research store. Source pins are already included. Do NOT regenerate them to bless
an unproved edit. `pin_upgrade_sources.py` is a release-preparation command, to be
used only after new proofs and the current audit.

The fixed catalogue accepts names, not source paths. Candidate input cannot supply
utility bounds, evaluation prices, switching charges, or self-approval flags. The
objective and core strings can be overridden only to demonstrate a rejected request.
A supplied log is replayed from the baseline; there is no durable cross-invocation
campaign state and no live self-modification.

## Current independent regressions

```bash
python checks/test_upgrade_campaign.py --start 0 --count 200
```

Repeat for starts 200,400,600,800,1000,1200,1400. The last slice has 42 cases.

```bash
python checks/test_upgrade_campaign.py --defenses
python tools/summarize_v023.py --baseline /path/to/AVOC_Formal_v0.22.0.zip
```

The defense test temporarily appends a comment to the NEW local specialization
source, expects the wrapper to reject it, and restores exact bytes in `finally`.
It does not touch user stores or the original release. Do not run it concurrently
with a build or another use of the same checkout.

The oracle independently evaluates 1,442 finite campaigns and compares the actual
Lean output, event charges, protected identities, final active decisions and visit
counts. It uses seed 230023 for 300 additional bounded sequences. It is software
regression, not an empirical LLM benchmark or a substitute for the generic proofs.

## Evidence and packaging

Current records are under `results/v0.23.0`. Older live recovery/filesystem suites
remain historical; this block does not claim they were rerun. The complete theorem
inventory includes helpers and examples. Compiler/kernel, cache, Python and protected
host integrity remain trust assumptions.

After successful collection:

```bash
python tools/package_v023.py --output /chosen/AVOC_Formal_v0.23.0.zip
python tools/check_manifest.py
```

Check the delivered manifest before regenerating evidence. Regenerated logs change
manifest-covered bytes. Manifests do not hash themselves or their own check output.
