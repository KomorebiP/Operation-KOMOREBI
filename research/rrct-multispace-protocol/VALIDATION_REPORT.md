# Validation Report

Status: `V061_ESTIMATORS_VALIDATED`

The package is designed to validate:

- exact manifest coverage and SHA-256 hashes
- Python syntax for every tool
- JSON and TOML parsing
- eight candidate objects with explicit information boundaries
- exclusion of V from independent consensus fitting
- two diagnostic estimator families in smoke and three required families in primary
- sparse nonnegative cone construction required in primary
- nine task families and 720 primary holdout cases
- ten conjunctive primary gates plus one replication gate
- local frozen models, serialized GPU use, and hard safety boundaries
- planted-positive recovery and independent-null rejection in the numerical estimator smoke

## Numerical checks completed

- Python syntax compilation passed for every tool.
- Planted shared geometry was recovered.
- Planted verbal-to-independent-consensus overlap: `0.971290`.
- Independent-null verbal-to-consensus overlap: `0.057474`.
- Shuffling future rows broke predictive recovery under the frozen threshold.
- The numerical result file was successfully written outside the package tree.

The local environment does not contain PyTorch and therefore cannot execute the Qwen runner. That runner was syntax checked here and is intended for the user's existing Windows `komorebi-full` environment, where Torch, Transformers, jlens, CUDA, the frozen Qwen model, and the locally fitted lens have already passed their individual smoke tests.

Final manifest and archive extraction verification are recorded by the validator output and archive hashes distributed with this report.
