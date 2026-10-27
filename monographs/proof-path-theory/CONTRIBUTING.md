# Contributing to Proof Path Theory

Contributions should preserve the distinction between formal proof, exact finite computation, numerical evidence, conjecture, interpretation, and historical commentary.

## Development setup

```powershell
python -m pip install -e ".[dev,docs]"
python -m pytest
```

For an offline environment with the required packages already installed:

```powershell
python -m pip install -e . --no-build-isolation
```

## Claim discipline

Every proposed mathematical result should state:

- its hypotheses and domain
- whether it is proved, computationally certified, numerically supported, conjectural, or interpretive
- the proof-field objects it depends on
- the tests or examples that exercise the implementation
- any historical-priority claim separately from the mathematical statement

New canonical results use the next available `PPT-###` identifier in `data/claim_ledger.csv`.

## Code changes

- Add or update tests for every public behavior change.
- Keep the package import path `proof_path_theory` free of optional plotting dependencies.
- Reject malformed or nonfinite inputs rather than propagating silent `NaN` values.
- Preserve deterministic ordering in serialized files and CLI output.
- Do not place a top-level package named `code`, `types`, `math`, `statistics`, or another standard-library module.

## Document changes

- Generate every figure through Python.
- Commit both vector PDF and PNG figure outputs.
- Do not edit generated figures manually.
- Compile the paper in three LaTeX passes after cross-reference changes.
- Render the final PDF and inspect it for clipped text, overlaps, missing glyphs, and blank pages.
- Keep theorem claims synchronized with `data/claim_ledger.csv` and executable support.

## Pull-request checklist

- [ ] The claim status is explicit.
- [ ] New hypotheses and scope restrictions are stated.
- [ ] Tests pass from the section root.
- [ ] JSON examples remain valid and acyclic.
- [ ] Generated data and figures are reproducible.
- [ ] The theorem ledger is synchronized.
- [ ] The paper compiles without LaTeX errors or unresolved references.
- [ ] No private paths, prompt text, credentials, or temporary build files are included.
