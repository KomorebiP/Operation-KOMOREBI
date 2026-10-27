# Paper III checked continuation v0.2.0

**Section 16 checked. Paper III remains in progress.**

Start with `REPORT.md` or `readers/Packet_Coordinate_Continuation_v0.2.0.pdf`.
The complete restart record is `CONTINUE_HERE.md` and the versioned progress ledger.

## Layout

- `formal/current`: active proof sources and the preserved finite project.
- `formal/audit`: whole-owner axiom audit and upstream-only kernel replay.
- `formal/controls`: external consumers and intentionally bad control sources,
  outside the production import graph. Expected failures here are not admissions
  in the production mathematics.
- `checked_objects`: exact accepted production objects for continuity, not an
  independent replacement for source compilation.
- `coverage`: source-bound Section16 map, exact declaration inventory and separately
  classified generated runtime helpers.
- `verification`: actual compiler, replay, computation and failure receipts.
- `baseline`: recovered October8 sources and traditional, visual and Lean readers.
  These remain historical. Font exclusions are explicitly recorded.
- `docs`: proof-guide source and failure analysis. `tools`: executable verifiers.

## Integrity and reproduction

First, on a pristine extraction:

```sh
python tools/verify_manifest.py
```

The tested formal route uses Python3 and the separate Linux portable kit:

```sh
KIT=/path/to/Komorebi_Portable_Lean_4.34.0-rc2
python tools/check_runtime.py --kit "$KIT"
python tools/rebuild_production.py --kit "$KIT" --run-name local_replay
python tools/run_lean.py OwnedAudit --kit "$KIT" --source-root formal/audit --objects build/local_replay_objects --tag local_audit --timeout 420
python tools/run_lean.py ReplayClosure --kit "$KIT" --source-root formal/audit --objects build/local_replay_objects --tag local_audit --timeout 420
python tools/run_controls.py --kit "$KIT"
python tools/run_replay_negative.py --kit "$KIT" --objects build/local_replay_objects
```

Do not reuse an existing `build/local_replay_objects` directory for the cold build.
The tools save new receipts under `verification`. Newly generated local receipts
are extra files relative to the original distribution manifest. Use a clean copy
when repeating the pristine package check.

`python tools/exact_packet_checks.py --output /tmp/paperIII_exact_check.json`
reruns the independent exact rational examples. The original companion runner and
its exact input roots are recorded in `verification/companion_replay/verification.json`.

On Windows, run the shell commands in WSL with the kit's Linux path. Native Windows
compilation and the user's WSL environment were not exercised here. The external
compiler/mathlib cache is not bundled. The old default Lake root verifies the old
finite contract only and must not be mistaken for this continuation's active scope.

The PDF guide has its own self-contained TeX source in `docs`. The original readers
remain in `baseline/publication/pdfs`. Font binaries are not included. Original
baseline manifests are preserved as historical evidence and are not active
inventories of the font-excluded copy. The fresh root manifest is authoritative
for delivered bytes. Existing project licensing status has not been changed.

## v0.3.0 continuation status

`REPORT_v0.3.0.md` supersedes the technical work-status discussion here.
Section 17 has a new rigorously described mathematical argument, 2622 exact
finite checks and two uncompiled Lean candidate modules under `formal/drafts/`.
There are **zero newly accepted kernel-checked declarations** in v0.3.0.
Section 16 production proofs and their recorded evidence remain untouched.
