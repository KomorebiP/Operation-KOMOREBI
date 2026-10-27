# Bayesian calibration summary

The calibration uses only the public ARC-AGI-2 training corpus. A deterministic task-ID hash assigns 799 tasks to parameter fitting and 201 tasks to a locked machine-level holdout.

| Partition | Whole tasks | Exact outputs | Output rate |
|---|---:|---:|---:|
| Calibration | 77/799 | 86/857 | 10.0350% |
| Parameter holdout | 30/201 | 32/219 | 14.6119% |
| Partition combined | 107/1000 | 118/1076 | 10.9665% |
| Independent full rerun | 108/1,000 | 119/1076 | 11.0595% |

The independent rerun differs from the partition-combined ledger by one exact output because program enumeration still has a small wall-clock cutoff.
