# v0.3.1 global freeze-test draft

Author: Komorebi P.

This directory contains two integration candidates:

- `execution_freeze.py`: a fail-closed, no-overwrite execution-freeze creator
  and runtime validator;
- `test_v031_contract.py`: global learned-output-free tests covering frozen
  episode serialization, exact D4 base-transversal coverage, matched-bank
  integrity, a synthetic exact representation, and tamper rejection.

Both files are designed to be copied into the package's `v031/` directory.
The explicit `REQUIRED_ROOT_RELATIVE_FILES` tuple in `execution_freeze.py` must
be reconciled with the final runner and test filenames before the freeze is
created.  Once `V031_EXECUTION_FREEZE.json` exists, neither that tuple nor any
listed scientific file may be edited without opening a disclosed new revision.

The matched-control validator accepts either the primary 48-control bank or a
fully materialized 144-control bank.  An unmaterialized parity-sandwich panel
must contain no hidden words and is not counted as an executed control set.

