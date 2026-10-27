# Paper I completion, Block 04 v0.4.0

Start with REPORT.md, VERIFICATION.json and PROGRESS_LEDGER.md. The mathematical guide is docs/PROOF_GUIDE.md. CONTINUE_HERE.md gives the next exact restart. The 108-record correspondence is coverage/COVERAGE_108.md and .json.

The complete unchanged Block 03 predecessor is under predecessor/. New mathematical sources are under source/extension/PaperICompletion4/. Both accepted fresh-stage receipts, logs and objects are in evidence/baseline_fresh/ and evidence/extension_fresh/. Failed development snapshots are separate under evidence/development/.

Run `python3 scripts/verify_bundle.py` to verify the extracted package payload hashes. Run `bash scripts/run_block04.sh RUNTIME NEW_OUTPUT` to reproduce the full two-stage audit with the external pinned portable runtime. Do not run lake update.

The current 33-module closure passes. This does not assert complete formalization of the expanded monograph, rebuild Mathlib, or use an independently implemented verifier. License-status records are inherited unchanged. No new publication license is selected.
