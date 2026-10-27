Komorebi ARC-AGI-2 Block 17 public-evaluation results
2026-10-09 UTC

Completed fresh full-bank compiler scan: 120 public tasks, 172 test outputs.
Both policies were predetermined and authenticated before separate scoring.

RESULTS
  typed_recent (primary): pass@1 1/172; pass@2 2/172 (1.1628%); task-mean pass@2 1.6667%; whole tasks 2/120.
  typed_supported (secondary control): pass@1 1/172; pass@2 2/172 (1.1628%); task-mean pass@2 1.6667%; whole tasks 2/120.

Verified public-training cached-record dispatcher replay:
typed_recent primary: 790/1076 exact pass@2 outputs (73.4201%).
typed_supported secondary control: 846/1076 exact pass@2 outputs (78.6245%).
These separately verified training results replay authenticated historical candidate records.
They are not a fresh compiler search or hidden-test results.

Retained compiler error receipts: 37. Authentication passed independently of these errors.
The dispatch audits retain every compiler receipt and the complete error array.

SCOPE
This run freshly compiled all banks from demonstrations and test inputs.
The external adapter then called the unchanged dispatcher per authenticated task.
Both predictions were sealed and authenticated before target opening and scoring.
No correctness-filtered champion was used. Frozen source bytes, size and mtime were verified.
The public evaluation set was historically inspected in this project. These results
are fresh frozen public-data execution, not a hidden competition score or a never-inspected holdout.

SOURCE RESTORATION
The source archive is already included in ARC_AGI2_Block17_verified_training_replay_2026-10-09.zip.
Training snapshot SHA-256: 4d44f937e2edafdb1b3327d1e6e0f5084a5592eed4431db16cc27c578da8dad4
Training snapshot reference: libfile_b4a96cf6d8008191b1b7b251e68cbd88
Extract that snapshot, then restore its nested source with:
  python -m zipfile -e arc-later-download/Komorebi_PR_LASM_Block17_Full_Bank_Integration.zip arc-fullbank
Nested source archive SHA-256: 457d66c2a45e729a3b4db9bae55a19d4f016f4a602090b82cb9e3380be3cd1b0
This result ZIP references the verified source archive rather than duplicating it.

REPRODUCTION
After restoring the source, run from the extraction directory:
  PYTHONDONTWRITEBYTECODE=1 python arc-evidence/later-source-audit/stream_fresh_block17_dispatch.py --root arc-fullbank/block17 --challenges arc-offline-data/arc-agi_evaluation_challenges.json --census arc-evidence/fullbank-public-evaluation/census.json --output-dir fresh-replay --policy typed_recent
Repeat sequentially with --policy typed_supported. Authenticate both outputs before any new scoring.

For a new full compiler scan, use a new output directory from the extraction root:
  PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python arc-fullbank/block17/run_scan.py --challenges arc-offline-data/arc-agi_evaluation_challenges.json --include-new --workers 4 --output fresh-scan/census.json
After that scan exits, dispatch its census with the adapter above, replacing the census path
with fresh-scan/census.json. Preserve and authenticate both predictions before target opening.

To independently rescore the existing frozen primary submission without importing the solver:
  PYTHONDONTWRITEBYTECODE=1 python arc-evidence/scripts/score_arc_submission.py --challenges arc-offline-data/arc-agi_evaluation_challenges.json --solutions arc-offline-data/arc-agi_evaluation_solutions.json --submission arc-evidence/fullbank-public-evaluation/typed_recent_submission.json --output fresh-score/typed_recent_score.json --ledger fresh-score/typed_recent_ledger.csv --label "Verified frozen Block17 public evaluation primary" --split evaluation
For the separately frozen control:
  PYTHONDONTWRITEBYTECODE=1 python arc-evidence/scripts/score_arc_submission.py --challenges arc-offline-data/arc-agi_evaluation_challenges.json --solutions arc-offline-data/arc-agi_evaluation_solutions.json --submission arc-evidence/fullbank-public-evaluation/typed_supported_submission.json --output fresh-score/typed_supported_score.json --ledger fresh-score/typed_supported_ledger.csv --label "Verified frozen Block17 public evaluation secondary control" --split evaluation

PACKAGE
SHA256SUMS.txt covers every payload file. The detached package audit gives ZIP SHA-256,
CRC verification, and per-member hash verification. The complete census replaces duplicate checkpoints.
Scan logs, monitor observations, compiler audits, freeze, source snapshot and verification,
provenance audits, streaming adapter, independent review, test and equivalence evidence are included.
