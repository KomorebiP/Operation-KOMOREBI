# Development

Use Python 3.12 or 3.13 in a dedicated environment. This handoff was executed on
Linux/Python 3.13.5. The CI matrix is supplied but has not been run remotely here.

```bash
python -m pip install -e ".[test]"
python -m pytest -q -W error -m "not local_suite"
python scripts/check_repository.py
komorebi-pr-lasm self-check
python scripts/stress_release.py --output results/stress
```

Before packaging, remove build output, results, bytecode and optional local fixture
sources from the distributable copy. Then run `python scripts/check_repository.py
--distribution` and the installed-backend build in [REPRODUCIBILITY](../REPRODUCIBILITY.md).

Tests marked `local_suite` require the separate local archive. They statically inspect
fixture trees and do not execute or score official ARC games. The small mock trees in
`test_environment_files` are regression fixtures, not the 25 official environment trees.

Keep raw failures and corrected reruns in separate logs. Every report must specify
which data split and model configuration produced it. Do not compare old and new
prediction numbers without accounting for the changed refit protocol.
