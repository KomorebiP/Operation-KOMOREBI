# Paper I completion Block 02 · v0.2.0

**Verified extensions to the frozen Paper I formal component. The expanded monograph is not yet fully formalized.**

Start with `REPORT.md` for the results, `PROOF_GUIDE.md` for the proofs and `CONTRACT_DELTA.md` for exactly which earlier inputs remain. `VERIFICATION.json` summarizes the executed receipts. `PROGRESS_LEDGER.md` and `CONTINUE_HERE.md` specify the next mathematical restart.

## Package contents

- `baseline/`: the complete unchanged prior audit payload, including all original sources, normative contract, evidence and license-status record.
- `source/extension/`: three new Lean modules plus the import-only root.
- `coverage/` and `publication_snapshot/`: all 108 current records with exact source statements, proofs, anchors, hashes and semantic coverage status.
- `tests/`, `scripts/` and `evidence/`: runnable verifiers, positive/negative controls, complete current receipts, objects and retained unsuccessful development attempts.

There are 24 baseline-plus-extension source files. All were freshly compiled and exactly replayed through the same Lean kernel. The complete source-owned inventory contains 1223 declarations. New public source declarations: 32 theorems, 12 definitions and 1 instance. Declaration counts include supporting results and are not novelty counts.

## Run from Linux or WSL

The external kit must be the authenticated `Komorebi_Portable_Lean_4.34.0-rc2`, with the pinned dependency cache. Python 3 is needed. Every new output directory must not already exist.

```bash
bash baseline/scripts/run_audit.sh /absolute/path/to/pinned-kit /absolute/path/to/new-baseline-run
bash scripts/run_extension.sh /absolute/path/to/pinned-kit /absolute/path/to/new-baseline-run /absolute/path/to/new-extension-run
```

Both shell launchers were actually executed successfully in this block. Do not run `lake update`. Compiled upstream imports are reused, not independently rebuilt. Both replay and original checking use Lean's kernel.

To regenerate the source inventory and semantic map without Lean:

```bash
python3 scripts/extract_publication.py --publication publication_snapshot --out /absolute/path/to/coverage-work
python3 scripts/build_coverage.py --publication publication_snapshot --work /absolute/path/to/coverage-work
```

Those commands reproduce the maps, not a proof that TeX and Lean are semantically identical. The packaged source anchors are not a stand-alone typesetting release.

No compiler or audit process continues after the handoff. The inherited license status is preserved in `baseline/LICENSE_STATUS_INHERITED.md`.

## Integrity check

```bash
python3 scripts/verify_bundle.py /absolute/path/to/unpacked-package
```

The manifest validator checks every payload file and rejects altered or unlisted files. Its deliberately corrupted-payload negative control is preserved. This is an integrity check, not a substitute for Lean verification.
