# Paper I formal component v1.0.2

For the journal manuscript v1.3.0. See the package-root README and
`scripts/verify_lean.py` for the executed verification method. The exact
35-row scope is in `LEAN_THEOREM_MAP_v1.0.2.md`.

## Changes from v1.0.1

Eight blanket `import Mathlib` lines were replaced by one focused import
module. All other content of the nineteen existing Lean source files is
unchanged. The added twentieth file contains only imports. No mathematical
statement, hypothesis, or proof body was edited. The row-29 exclusion prose
was corrected: surjectivity is sufficient; dense range suffices for the
density conclusion alone. See `review/lean_source_preservation.json`.

Lean: `leanprover/lean4:v4.34.0-rc2`.
Mathlib: `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.
All package pins are retained in `lake-manifest.json`.

From a compatible local Lake environment, ordinary checking is possible with
`lake --wfail build` and `lake env lean -DwarningAsError=true
KomorebiVerification/KernelAudit.lean`. The root verifier additionally uses a
fresh local object directory, resolves all mapped declarations, compares the
complete audit inventory, records commands and hashes, and runs negative
controls. These additional stages are not implied by a bare build command.

The cached dependencies are trusted inputs in the journal verification, not
newly rebuilt dependencies. The full-paper scope is certificate-explicit.
