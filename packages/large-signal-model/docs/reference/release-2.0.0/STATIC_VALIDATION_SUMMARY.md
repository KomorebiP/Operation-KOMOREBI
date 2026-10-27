# Static validation summary

The user-supplied `tests.zip` contained 25 versioned ARC-AGI-3 environment trees.

Packaging validation found:

```text
metadata files:             25
Python game sources:        25
unique game IDs:            25
syntax failures:             0
missing expected classes:    0
forbidden imports:           0
```

The complete machine-readable report is `validation/suite_static_audit.json`. Exact source and metadata checksums are recorded in `25_TESTS_MANIFEST.json`.

The static audit does not execute game logic. Runtime compatibility with the official toolkit is checked separately by `3_Official_Smoke_All_25.ps1` on the target Conda installation.
