# Bounded recording tools

`run_experiment.py` and `validate_manifest.py` are unmodified copies of the mathematical computation-audit skill's recording and validation tools, read on 9 October 2026 from the installed package `mathbox:computation-audit`.

Their upstream resource identifiers are:

- `skill://plugins_6a9174204a0481918ca3798d69d2e227/computation-audit/scripts/run_experiment.py`
- `skill://plugins_6a9174204a0481918ca3798d69d2e227/computation-audit/scripts/validate_manifest.py`

The release includes these copies so that a reader can replay and validate without a skill installation. They record explicit argv, bounded execution, pinned inputs and declared outputs. A successful recording is evidence about that execution and does not by itself verify a universal mathematical theorem.
