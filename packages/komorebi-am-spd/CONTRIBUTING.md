# Contributing

Issue reports, reproducibility findings, and narrowly scoped technical discussions are welcome.

The repository currently uses a restrictive license and does not yet define contribution licensing terms. Do not submit substantial code or manuscript pull requests until those terms are selected. Small diagnostic pull requests may be considered after prior discussion in an issue.

## Development setup

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev,research]"
python -m pytest
python -m am_spd verify --full
```

## Change boundaries

- Keep the supported interface under `src/am_spd`.
- Preserve `research/original` as an auditable recovered snapshot.
- Do not silently change theorem statements, benchmark data, or verification totals.
- Separate proved statements, computed finite results, and heuristic claims.
- Add tests for every public API change.
- Keep image normalization and residual-archive semantics backward compatible unless the change is explicitly documented.
- Do not change `.amspd` schema semantics without a versioned migration path.
- Keep exact paper replay differences visible in the comparison ledger.

## Pull request checklist

- The package test suite passes.
- `am-spd verify --full` passes.
- Public behavior is documented.
- New numerical tolerances are justified.
- Generated files are not mixed with source changes without a reproducibility note.
