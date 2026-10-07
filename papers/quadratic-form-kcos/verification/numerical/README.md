# Numerical replay and recorded evidence

Read FRESH_NUMERICAL_VALIDATION.md for the contract, fresh outcomes, repairs, and limitations. The final source hashes and the nonfinite guard amendment are in FINAL_SOURCE_PROVENANCE.json.

From the extracted release root:

```bash
python -m pip install -r verification/numerical/requirements.txt
python verification/numerical/replay.py --include-controls
```

The replay writes a new timestamped directory containing logs, numerical results, actual commands, statuses and source hashes. Recorded historical execution paths in recorded_runs refer to the original workspace. Installed scratch dependencies are deliberately excluded from this deliverable.
