# Kaggle submission procedure

## Browser workflow

1. Create a Kaggle notebook from `kaggle/PR_LASM_ARC2_Kaggle_Entry.ipynb`.
2. Attach the ARC-AGI-2 competition data.
3. Keep internet access disabled.
4. Run every cell.
5. Confirm that the final cell reports `"valid": true` and the expected task
   count.
6. Save a notebook version with outputs.
7. Select that version through the competition submission interface.

## Embedded runtime

The notebook contains compressed, hash-verified copies of:

```text
arc2_entry.py
atlas.py
lasm_bayesian.py
bayesian_lasm_calibration.json
run_submission.py
```

They are written to:

```text
/kaggle/working/pr_lasm_arc2/
```

The final submission and runtime record are:

```text
/kaggle/working/submission.json
/kaggle/working/pr_lasm_arc2_runtime_report.json
```

## Runtime controls

Default settings are:

```text
soft candidate-generation budget: 8 seconds per task
hard subprocess budget: 20 seconds per task
parallel workers: min(4, available CPUs)
```

Override them before the runner cell when required:

```python
import os
os.environ["ARC2_SOFT_LIMIT"] = "8"
os.environ["ARC2_HARD_LIMIT"] = "20"
os.environ["ARC2_WORKERS"] = "4"
```

Every task runs in a separate process. OpenBLAS, OpenMP, MKL, and NumExpr are
limited to one thread per worker. A hard timeout produces a deterministic
schema-valid fallback and is recorded in the runtime report.

## Local notebook validation

The repository test suite decodes every notebook payload, checks its hash, and
compares it byte-for-byte with the canonical Kaggle runtime files. The notebook
can also be executed against the included synthetic ARC-shaped fixture without
network access.
