# Independent pytest verification

Generated: 2026-10-07T16:36:52.177568+00:00

Each canonical source directory was copied to a fresh temporary directory. Only pytest was run. No build, table-generation, or figure-generation command was invoked. Original-file SHA256 manifests were compared before and after each run.

| Paper | Pytest passed / collected | Failed / errors | Time, seconds | Archived built-in passed / total | Built-in batch rerun by pytest |
|---|---:|---:|---:|---:|---|
| I | 13 / 13 | 0 / 0 | 11.56 | 51 / 51 | Yes |
| II | 18 / 18 | 0 / 0 | 9.14 | 61 / 61 | No |
| III | 19 / 19 | 0 / 0 | 6.94 | 34 / 34 | No |
| IV | 18 / 18 | 0 / 0 | 7.80 | 18 / 18 | No |
| V | 19 / 19 | 0 / 0 | 9.26 | 19 / 19 | No |
| VI | 21 / 21 | 0 / 0 | 3.49 | 24 / 24 | No |
| VII | 20 / 20 | 0 / 0 | 3.39 | 13 / 13 | Yes |
| VIII | 20 / 20 | 0 / 0 | 2.12 | 23 / 23 | No |

Fresh pytest total: 148 / 148. Archived built-in ledgers: 243 / 243. Built-in checks actually recomputed through pytest: 64 (Papers I and VII).

## Environment

Python: `/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python` (3.12.14).

pytest 9.1.1, numpy 2.3.5, scipy 1.17.0, matplotlib 3.10.8, mpmath 1.3.0, sympy 1.14.0, Pillow 12.3.0.

Dependencies missing from the runtime were installed only in `verification_dependencies`. No source changes were made.

## Scope

- Pytest includes both recomputed numerical/symbolic assertions and checks of archived ledgers, figure files, and manuscript references.
- Archived built-in result counts are distinct from pytest case counts. Only Papers I and VII invoke their built-in batch from pytest.
- These tests do not provide a formal proof or establish universal numerical claims.

Exact commands, paths, environment overrides, per-case timing, source manifest hashes, and logs are recorded in `independent_pytest_verification.json` and `verification_logs/`.
