# Block17 Limitfix Diagnostic v0.1.0

Komorebi P. — 2026-10-09

The disabled extraction compiler is corrected in a separate source version. Ten regression checks and the existing thirteen integration tests pass. Six fresh original full-bank training compilations exactly reproduce342 cached candidates, all base outputs and462 provider receipts. The corrected bank preserves these342 candidates and adds one extraction candidate, whose output is already present. This sample gains no distinct prediction coverage.

The original public evaluation remains **2/172 output pass@2 (1.1628%)**, with2/120 whole tasks (1.6667%). This update has **no new full evaluation score**. The earlier70%+scores are cached training replay. Fresh compiler equivalence for all1,000 training tasks and the cause of the evaluation gap remain unresolved. Extraction had zero cached training candidates, so its defect cannot explain that gap.

## Contents

- The original authenticated source ZIP and original public-evaluation result ZIP, preserved byte for byte.
- Two replacement files under patches/ plus the minimal extraction_limitfix.patch. Only the shared compatibility-key allowance and its registry pin change. Local search budgets stay fixed.
- selected_challenges.json, expected_records.json and selection_audit.json: six training inputs and authenticated cached references selected without consulting query answers.
- fresh_original_training/: completed records and process/comparison receipts. fresh_patched_training.json: the corrected six-task full-bank census.
- Regression, integration, runner-control, source-restoration and independent-audit reports. DIAGNOSTIC_SUMMARY.json records the exact interpretation and limitations.
- prepare_limitfix.py, test_extraction_limitfix.py and compare_fresh_training.py for offline restoration and reruns. The selection_provenance/ scripts document how the reference was selected; they retain their original workspace layout assumptions.

## Restore source

The restorer uses only Python's standard library. Extract this package first. The destination must be new and outside the extracted package. It verifies every declared package member, the original source ZIP, all388 original source files and the exact two tested patches. It runs no compilers. Have at least2GB of free space for each restored tree.

```powershell
python prepare_limitfix.py --verify-only
python prepare_limitfix.py --destination ..\Block17Original --original-only
python prepare_limitfix.py --destination ..\Block17Limitfix
```

## Repeat the bounded checks

Compiler checks were run on Linux, Python3.12.14 and NumPy2.3.5. Use Linux or WSL with an existing compatible NumPy installation for the following commands. The process watchdog uses Linux APIs. Native Windows compiler execution and other dependency versions have not been validated. The restorer itself uses portable standard-library APIs.

```bash
python -B test_extraction_limitfix.py --original-root ../Block17Original/block17 --patched-root ../Block17Limitfix/block17 --baseline original_source_identity.json --output regression_rerun.json
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python -B compare_fresh_training.py --source ../Block17Original/block17 --timeout 90 --workers 1 --output-dir ./fresh_original_rerun
```

The comparison writes to a new direct subdirectory beside the script. Each task runs in a fresh process and saves its record before comparison. A timeout/error is incomplete, never a record-equivalence verdict. The six-task check is not a full-corpus benchmark.

A corrected six-task scan can also be run on a new output:

```bash
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python -B ../Block17Limitfix/block17/run_scan.py --challenges selected_challenges.json --include-new --workers 1 --output corrected_sample_rerun.json
```

## Evidence boundaries

The original and corrected source versions are distinct. Restored results/ files belong to the historical original release. The original validate.py checks archived source/freeze bindings and will reject the changed bank; do not treat those archived validations as validation of this correction. No full validator or full1,000-task compiler scan is claimed here.

Query answers were not consulted for task selection, generation or correctness scoring in this diagnostic. Full-source authentication hashes bundled solution files as opaque bytes. The query_targets_opened=false fields in historical run receipts describe no semantic use, not a literal absence of all file opens or operating-system isolation. The inherited banks and training schemas have disclosed training-solution development exposure.

Extraction has no production replay_program hook. Its new program was independently re-executed with the existing native interpreter on synthetic and selected-task inputs; this is separately reported, not a production hook or a fresh held-out accuracy result.

The original full evaluation retains37 compiler errors. Their diagnosis and the broader generalization problem remain open. This is a tested integration correction and diagnostic handoff, not a declaration that the ARC solver is finished.
