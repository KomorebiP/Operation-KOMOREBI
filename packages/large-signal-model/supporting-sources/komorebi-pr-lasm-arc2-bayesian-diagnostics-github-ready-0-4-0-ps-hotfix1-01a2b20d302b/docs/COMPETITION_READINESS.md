# Competition readiness

| Requirement | Status | Evidence |
|---|---|---|
| Self-contained Kaggle notebook | Complete | `kaggle/PR_LASM_ARC2_Kaggle_Entry.ipynb` |
| No internet during execution | Complete | Standard library and NumPy only |
| Open-source release | Complete | MIT License |
| Exactly two attempts per test input | Complete | Validator and automated tests |
| Exact grid schema validation | Complete | `validate_submission` |
| Test-file auto-discovery | Complete | Hyphenated and underscored ARC file names |
| Bayesian calibration embedded | Complete | Hash-verified calibration JSON |
| Exact multi-atlas reconstruction | Complete | Spatial, color, Fourier, Haar, and polyphase tests |
| Parameter-holdout audit | Complete | `benchmarks/bayesian_calibration_report.json` |
| Per-task hard isolation | Complete | `kaggle/run_submission.py` |
| Full competition test-file dry run | Complete | 240 tasks, valid schema; aggressive 0.05/5-second audit produced 48 deterministic fallbacks |
| Private Kaggle score | Not performed | Requires the user’s Kaggle account |
| Competitive performance | Not claimed | See measured release results |

## Current conclusion

Version 0.3.0 is mechanically ready for an offline Kaggle run and contains a
real fitted Bayesian PR-LASM inference layer. The main remaining limitation is
operator-language coverage. Bayesian selection improves the handling of
ambiguous exact fits, but it cannot assign probability to a transformation the
typed grammar cannot express.


## Runtime note

The 240-task infrastructure dry run deliberately used a 0.05-second soft search
budget and a 5-second hard process budget. It is a stress test, not the default
competition policy. Forty-eight tasks used deterministic fallbacks under that
aggressive setting. The default notebook policy is 8 seconds soft and 20 seconds
hard per task. A private competition score has not been measured.
