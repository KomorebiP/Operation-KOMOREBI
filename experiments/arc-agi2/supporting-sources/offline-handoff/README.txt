Komorebi ARC-AGI-2 Block17
Complete offline source and evaluation handoff
2026-10-09
Author: Komorebi P.

This handoff closes the recovered Block17 evaluation and preserves everything
needed to inspect its source, independently check the saved score, and prepare
a separate compiler run. The solver, banks, budgets and policies are unchanged.

VERIFIED RESULT

Policy             Cached public training replay   Fresh public evaluation
typed_recent       790/1076 outputs, 73.4201%        2/172 outputs, 1.1628%
typed_supported    846/1076 outputs, 78.6245%        2/172 outputs, 1.1628%

The evaluation uses two attempts per output. Both policies solved 2/120 whole
tasks, or 1.6667%. The equal-task mean output accuracy is also 1.6667%. Pass@1
was 1/172. All 120 tasks and 172 output positions remain in the denominator.

Both policies were fixed and their complete prediction files were sealed before
this evaluation workflow opened solutions. Independent score and ledger reviews
agree. Public evaluation was already inspected earlier in this project. This is
a fresh execution on public data, not an official private competition result.

The 70%+ figures describe selection from cached public-training compiler records.
They do not establish 70% accuracy from fresh search on new tasks. Current public
evaluation is the relevant generalization evidence for this version.

WHAT IS FINISHED

The original source is preserved. The complete fresh compiler census, both
fixed-policy predictions, scoring ledgers, original failures, process receipts,
source checks and independent reviews are preserved in the results archive.
The offline verifier and rerun preparation script live outside frozen source.
The release handoff is complete. Improving the solver's generalization remains
future work. No performance improvement is claimed by repackaging these files.

QUICK OFFLINE CHECK

Extract this handoff ZIP into a folder. Python 3.12 is the tested baseline. The
score verifier uses only Python's standard library. It does not need NumPy,
credentials, internet access, source extraction or another compiler run.

Windows PowerShell, from the extracted handoff folder:

  python .\verify_release.py

Or use the wrapper, choosing your existing Python executable:

  .\RUN_OFFLINE_CHECK.ps1 -PythonExecutable python

Linux or WSL, from the extracted handoff folder:

  python3 verify_release.py

Successful output is JSON with integrity_pass:true and the independently
recomputed metrics for both policies. Invalid hashes, membership, predictions,
score totals or ledger rows cause a nonzero exit code. No files are written.

For an additional streaming CRC check of every archive member:

  python3 verify_release.py --check-all-member-crcs

The verifier authenticates input archives and both saved prediction files before
opening evaluation solutions. It checks saved outputs. It does not rerun the
compiler, dispatcher or serialized programs, and it does not parse the474MB
census or expand the 2.6GB cached training JSON into memory.

FILES

Komorebi_PR_LASM_Block17_Full_Bank_Integration.zip
  The exact original solver source archive. Contains 388 source/evidence files.

ARC_AGI2_Block17_public_evaluation_results_2026-10-09.zip
  The exact final evaluation artifact. Contains the full census, predictions,
  datasets, ledgers, provenance, reproduction helpers and independent reviews.

HISTORICAL_TRAINING_REPLAY_EVIDENCE.zip
  Preserved training replay payloads from the verified historical snapshot.
  Only the duplicated source archive is omitted and supplied separately above.
  PROVENANCE.json records that derivation and the original snapshot SHA256.
  Historical README and summary files inside it describe their original date.
  This root README and ARC_AGI2_offline_summary.json give the completed status.

verify_release.py
  Independent standard-library integrity and exact-score verifier.

prepare_rerun.py
  Restores the source and minimal helpers into a new external workspace. It
  authenticates the handoff first and captures a separate source baseline.
  Existing destinations are rejected. No compiler or runtime tests are started.

package_handoff.py
  Rebuilds a ZIP from the verified handoff inputs and writes a detached audit.
  It is a packaging utility; it does not compile or modify the solver.

ARC_AGI2_offline_summary.json, RELEASE_STATUS.json, KNOWN_ISSUES.txt
  Current scores, completion scope, limitations and remaining work.

INPUTS_SHA256SUMS.txt
  SHA256 for every other root input. All checks are integrity evidence for this
  handoff, not a cryptographic identity or authenticity signature.

PREPARE AN OPTIONAL NEW SOLVER RUN

Saved-score verification is separate from fresh compiler reproduction. Run the
compiler and authenticated dispatcher helpers in Linux or WSL. Their Unix
resource measurement and /proc checks are not native Windows facilities.
Native Windows compiler execution is untested. The PowerShell verifier wrapper
was inspected here; PowerShell itself was not installed in the test environment.

Tested solver environment: Linux, Python 3.12.14, NumPy 2.3.5. NumPy must already
be installed for an entirely offline solver run. No other external runtime
dependency was found. The standalone verifier does not require NumPy.

Choose a NEW workspace outside the extracted handoff folder. In Linux/WSL:

  python3 prepare_rerun.py --destination ../block17-rerun

The script creates the workspace, extracts the source, copies only the needed
datasets/helpers, verifies all 388 restored files against the original snapshot,
and records fresh extraction mtimes. Archived fresh-evaluation census files,
checkpoints and scanner ownership receipts are not copied into the new run
outputs. Historical training censuses inside the original source archive remain
preserved for the separate cached-training replay. The original evidence is preserved.

Then, from the new workspace:

  cd ../block17-rerun
  arc_root="$(pwd -P)"
  export PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1
  export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
  cd "$arc_root/arc-fullbank/block17"

Run the integrated source tests:

  python3 -m unittest discover -s tests -p 'test_*.py' -v

Run fresh public-evaluation compilation, preserving all source budgets:

  python3 run_scan.py \
    --challenges "$arc_root/arc-offline-data/arc-agi_evaluation_challenges.json" \
    --include-new --workers 1 \
    --output "$arc_root/arc-evidence/fullbank-public-evaluation/census.json"

One worker reduces concurrency; it does not establish a hard memory bound or
a runtime deadline.

After the scanner exits successfully, check restored source contents and mtimes:

  python3 "$arc_root/arc-evidence/later-source-audit/verify_block17_unchanged.py" \
    --root "$arc_root/arc-fullbank/block17" \
    --snapshot "$arc_root/arc-offline-runs/restored_block17_source_before.json" \
    --output "$arc_root/arc-offline-runs/restored_block17_source_after.json"

Only after the complete 120-task census AND its 120 checkpoints exist, run the
two frozen policies and independent scoring in that same NEW workspace:

  python3 "$arc_root/arc-evidence/scripts/finalize_block17_public_evaluation.py" \
    --workspace "$arc_root" \
    --source-snapshot "$arc_root/arc-offline-runs/restored_block17_source_before.json"

The finalizer writes to fixed filenames within the new workspace. Do not run it
over the archived original evidence. It saves and authenticates both policies
before reading query targets. It does not select a policy after scoring.

Optional cached TRAINING dispatch reproduction in the restored workspace:

  python3 "$arc_root/arc-evidence/later-source-audit/stream_block17_dispatch.py" \
    --root "$arc_root/arc-fullbank/block17" \
    --challenges "$arc_root/arc-fullbank/block17/data/challenges.json" \
    --census "$arc_root/arc-fullbank/block17/results/census.json.gz" \
    --compare-dir "$arc_root/arc-fullbank/block17/results" \
    --output-dir "$arc_root/arc-offline-runs/training-replay" \
    --solutions "$arc_root/arc-fullbank/block17/evidence/solutions.json"

RESOURCE AND COMPLETION LIMITS

Source extraction occupies 778,549,294 bytes. Fresh outputs need additional disk.
The preparation script reserves 1GiB beyond extraction, which is only an initial
reserve and does not guarantee sufficient disk for the complete compiler run.
Keep several additional GiB available for checkpoints and the aggregate census.

The original full validate.py exited 137 unfinished while loading the large
cached training census. All 13 integrated runtime tests passed. A separate
streaming training replay completed with about 530MiB peak RSS. The fresh census
assembler used about 162MiB. These are observed peaks for those paths, not a
guarantee for a new full solver run. The frozen engine aggregates its census in
memory. Preserve checkpoints if aggregation or a write fails.

Compilation can take hours. Nominal tier 2.0 is a search budget, not a wall-clock
cutoff. No complete-stage termination bound or completion time is established.
Run one scanner per output/checkpoint directory. Never reuse checkpoints with
changed challenges, source, limits, policies or include-new settings.

37 compiler errors remain in the evaluation evidence. Read KNOWN_ISSUES.txt for
the exact scope and the difference between an integrity pass and error-free
compilation. Source-level fixes require a new version and a separate evaluation.
