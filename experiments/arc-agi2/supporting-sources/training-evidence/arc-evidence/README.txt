Komorebi ARC-AGI-2 verified training replay snapshot
2026-10-09 UTC

This snapshot contains the verified Block 17 training replay. The separate
complete-bank public-evaluation scan is pending, and its unfinished checkpoints
are excluded. No final public-evaluation score is claimed by this snapshot.

To use this snapshot in another location, extract this outer ZIP, then extract
arc-later-download/Komorebi_PR_LASM_Block17_Full_Bank_Integration.zip into
arc-fullbank/. The inner archive creates block17/ beneath that directory.
From the outer snapshot's extraction directory, the restore command is:
  python -m zipfile -e arc-later-download/Komorebi_PR_LASM_Block17_Full_Bank_Integration.zip arc-fullbank
Adjust the workspace prefix in the commands below to your extraction location.
The included SHA256SUMS.txt covers every payload file in this outer snapshot.

The integrated Block 17 runtime reproduces its frozen public-training results:
  typed_recent primary:   790/1076 exact outputs (73.4201%), 734/1000 whole tasks
  typed_supported control: 846/1076 exact outputs (78.6245%), 786/1000 whole tasks
  Both policies:          267/1076 exact outputs in Attempt 1

These are exposed public-training results. They are fresh dispatcher replays of
authenticated, previously compiled candidate records. They are not a new
1000-task compiler search or an unseen-evaluation score. The control remains a
separately frozen control, rather than a replacement for the primary policy.

SOURCE

Archive:
  /workspace/scratch/40dd7e475149/arc-later-download/Komorebi_PR_LASM_Block17_Full_Bank_Integration.zip
SHA-256:
  457d66c2a45e729a3b4db9bae55a19d4f016f4a602090b82cb9e3380be3cd1b0
Extracted runtime:
  /workspace/scratch/40dd7e475149/arc-fullbank/block17

Archive inventory and all 387 manifest-listed files passed independent checks.
There are 388 files including the manifest. Runtime source authentication passed.
All 388 files retained identical contents, size and modification time after the
replay. The exact-string AST scan found no training task-ID literals across
209 runtime Python files. These checks have the finite scopes stated in their
reports; they do not turn public training into an unseen benchmark.

Paths below refer to this workspace. Adjust them after moving the extracted
source and evidence. Python 3.12.14 and NumPy 2.3.5 were used. The runtime needs
no network connection. Disable bytecode writes when checking frozen source.

INTEGRATED TESTS

From the extracted runtime directory:
  PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -p 'test_*.py' -v

Fresh result: 13/13 passed, with zero failures, errors or skips.

The original validate.py attempt passed those tests, then was killed with
exit 137 during full-census loading/replay. Its full validation did not finish.
The census expands from 48.6 MiB compressed to 2600599269 bytes of JSON
(approximately 2.42 GiB or 2480 MiB);
the shared runtime has an 8 GiB memory limit and recorded out-of-memory kills.
The successful replacement below streams records without changing frozen code.

MEMORY-SAFE TRAINING REPLAY

Run from any directory:
  PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 python /workspace/scratch/40dd7e475149/arc-evidence/later-source-audit/stream_block17_dispatch.py --root /workspace/scratch/40dd7e475149/arc-fullbank/block17 --challenges /workspace/scratch/40dd7e475149/arc-fullbank/block17/data/challenges.json --census /workspace/scratch/40dd7e475149/arc-fullbank/block17/results/census.json.gz --output-dir /workspace/scratch/40dd7e475149/arc-evidence/fullbank-training-stream-replay --compare-dir /workspace/scratch/40dd7e475149/arc-fullbank/block17/results --solutions /workspace/scratch/40dd7e475149/arc-fullbank/block17/evidence/solutions.json

The helper verifies compressed and decompressed bytes, the complete semantic
census hash, all record hashes, input bindings and runtime source bindings.
It calls the unchanged dispatcher on each complete task record for both frozen
policies, rebuilds the full outputs and requires archived byte identity.
Targets are opened only after both prediction files have been written.

Fresh result: 1000 records, 12391 candidates, 2000 frozen-dispatcher calls.
Both policy outputs were byte-identical to their archived versions. All 243
compiler-error receipts were retained: 237 micro_schemas and 6 feature_induction.
Elapsed time was 563.27 seconds; peak resident memory was 530 MiB.

Main result:
  fullbank-training-stream-replay/replay_report.json
Supporting checks:
  later-source-audit/block17_source_audit.json
  later-source-audit/block17_integrity.json
  later-source-audit/block17_unit_tests.log
  later-source-audit/block17_source_unchanged_after_replay.json

FRESH COMPLETE-BANK PUBLIC-EVALUATION SCAN

STATUS: IN PROGRESS. No final integrated public-evaluation score is available.
FINAL PRIMARY SCORE: [PENDING] /172 exact outputs; [PENDING] /120 whole tasks
FINAL CONTROL SCORE: [PENDING] /172 exact outputs; [PENDING] /120 whole tasks
FINAL ERROR RECEIPTS AND SOURCE-UNCHANGED CHECK: [PENDING]

This scan recompiles all banks on 120 tasks with 172 test outputs. It
does not reuse a training census or a correctness-filtered champion. Attached
test outputs are rejected by the runtime. Source, budgets and both policies
remain frozen. The completed checkpoints are bound to the source and inputs.

From the extracted runtime directory, using a new external output path or the
same authenticated checkpoint path when resuming:
  PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 python run_scan.py --challenges /workspace/scratch/40dd7e475149/arc-offline-data/arc-agi_evaluation_challenges.json --include-new --workers 6 --output /workspace/scratch/40dd7e475149/arc-evidence/fullbank-public-evaluation/census.json

After the full census exists, dispatch both policies without changing them:
  PYTHONDONTWRITEBYTECODE=1 python solver.py --challenges /workspace/scratch/40dd7e475149/arc-offline-data/arc-agi_evaluation_challenges.json --census /workspace/scratch/40dd7e475149/arc-evidence/fullbank-public-evaluation/census.json --policy typed_recent --output /workspace/scratch/40dd7e475149/arc-evidence/fullbank-public-evaluation/typed_recent_dispatch.json
  PYTHONDONTWRITEBYTECODE=1 python solver.py --challenges /workspace/scratch/40dd7e475149/arc-offline-data/arc-agi_evaluation_challenges.json --census /workspace/scratch/40dd7e475149/arc-evidence/fullbank-public-evaluation/census.json --policy typed_supported --output /workspace/scratch/40dd7e475149/arc-evidence/fullbank-public-evaluation/typed_supported_dispatch.json

Seal both predictions before separate scoring. The bundled evaluate.py is
specific to the recorded training freeze; it is not a generic public-evaluation
CLI. Final public-evaluation scoring commands and receipts will be added when
the current scan is complete. Do not treat partial-task results as a full score.

To check source state again after the scan:
  PYTHONDONTWRITEBYTECODE=1 python /workspace/scratch/40dd7e475149/arc-evidence/later-source-audit/verify_block17_unchanged.py --root /workspace/scratch/40dd7e475149/arc-fullbank/block17 --snapshot /workspace/scratch/40dd7e475149/arc-evidence/later-source-audit/block17_source_before.json --output /workspace/scratch/40dd7e475149/arc-evidence/later-source-audit/block17_source_unchanged_final.json
