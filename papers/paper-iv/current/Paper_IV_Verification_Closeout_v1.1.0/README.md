# Paper IV — verification closeout v1.1.0

19 October 2026 (UTC) · Operation Komorebi · Komorebi P.

## Result

The existing **68-result reviewed formal core** passed a fresh pinned-source replay,
exact target-kind resolution, a transitive namespace axiom audit and real compiler
controls. All 119 mathematical Lean sources are unchanged. This is a verification
closeout, not a new or strengthened mathematical theorem.

Start with `readers/Paper_IV_Verification_Closeout_v1.1.0.pdf` or `REPORT.md`.
`verification/CLOSEOUT_REPORT.json` contains the structured summary.

## Contents

- `readers/`: the latest recovered 77-page monograph, 28-page visual guide,
  140-page Lean guide, and new five-page verification report.
- `formalization/lean/`: the complete active formal source, exact dependency pins,
  and the corrected warning policy. No external runtime or dependency cache.
- `publication_baseline/`: the intact recovered 836-file publication/source tree.
  Its old reports and stale font-bearing manifest remain historical evidence.
- `verification/`: source preservation, current compiler logs and objects, axiom
  reports, compiler controls, finite computations, test suites and failed attempts.
- `scripts/`: portable verification, replay, reporting and test programs.
- `PROGRESS_LEDGER.md`, `PROGRESS_LEDGER.json`, `CONTINUE_HERE.md`: versioned status
  and the next restart point.

## Reproduce the checks

Use Python 3.11 or newer on Linux/WSL. Commands write new evidence outside the
frozen package. They do not install software, fetch dependencies, or edit the
accepted mathematical sources.

```bash
python3 -B scripts/verify_release.py
python3 -B scripts/run_checks.py --mode records --work /tmp/paper-iv-records
python3 -B scripts/run_checks.py --mode finite --work /tmp/paper-iv-finite
bash Run-Replay.sh /path/to/Komorebi_Portable_Lean_4.34.0-rc2 /tmp/paper-iv-full
```

Every output directory must be new. Full mode requires the matching external
Lean runtime and all cached packages specified in `formalization/lean/lake-manifest.json`.
Finite mode additionally requires the Python packages recorded in the finite receipt.
The report builder uses ReportLab. Native Windows execution was not tested.

`verify_release.py` checks stored evidence and hashes; it is not a new compiler
run. Full mode performs fresh source compilation, kind and axiom checks, and
compiler controls. Its 300-second per-command timeout and one-worker configuration
retain the accepted production settings.

## Reader versions and exact scope

The older monograph and Lean reader correctly describe their own earlier edition
and its historical formal evidence. The new closeout report is the authority for
this execution. The October 16 standalone visual PDF is preserved, including its
branch-sensitive correction. The exact updated editable source for that standalone
PDF was not recovered; the October 8 editable baseline and a three-page PDF text
difference record are included. No byte-identical regeneration of that later PDF
is claimed.

The reviewed 68-result contract, hypotheses, branch choices and explicit research
boundaries are unchanged. Imported standard fact 11.1 is outside that count.
No new independent semantic reproof of all 68 statements, cold Mathlib build,
independent proof kernel, external referee review, or licence decision is claimed.

The separate `Paper_IV_Delivery_Verification_v1.1.0.json` records the final ZIP
hash, fresh extraction and post-extraction tests. It is external to the archive
to avoid circular self-hashing.
