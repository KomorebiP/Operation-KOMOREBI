# Reproduce Block34

## Read-only evidence replay

    PYTHONDONTWRITEBYTECODE=1 python verify_release.py
    python validate_manifest.py COMPUTATION_MANIFEST.json --root .

The first command checks all retained exits, frozen input hashes, both complete
axiom inventories, original predecessor identity, compiled artifact presence and
archive checksums. It does not execute Lean. The second command is the retained
project-local schema1 validator, not the installed plugin's full schema2 validator.

## Fresh formal verification

Use a disposable extracted copy, because the runner intentionally replaces the
published receipts and removes only its project-local .lake/build directory.
Keep the published ZIP unchanged.

    export RUNTIME=/absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2
    export PATH="$RUNTIME/toolchain/bin:$PATH"
    python verification/prepare_offline.py "$RUNTIME"
    lean --version
    lake --version
    PYTHONDONTWRITEBYTECODE=1 python verification/run_final.py

Exact Lean: 4.34.0-rc2, commit 6a10ac8c22beadecabdbb0919c2b50214762f91d.
Exact mathlib: aeb72f1e9981b6d35b426b16dca7759be3e7ba06. Other package revisions are
in lake-manifest.json. The preparation script checks every cached git revision.
The portable runtime SHA256 is
f7548038f94ea30789ce28fc2ff769c40e9c37d8879ea133e9bea821056342c7.

The runner checks clean root build, axiom audits, new concrete/universal examples,
immediate predecessor examples, positive and negative controls, leanchecker, and
exact integer computation. Each subprocess has a 600-second timeout. All
registered source/configuration/verification input hashes must remain unchanged.
No hard memory or elapsed-time theorem is inferred from this operational timeout.
The resource profiles and actual runtime are recorded per phase.

To run only the finite reference experiment:

    PYTHONDONTWRITEBYTECODE=1 python verification/audit_residual.py

This produces a new results/audit_residual.json. It does not prove Lean theorems.
The theorem/example inventory generator is portable and reads the exact embedded
predecessor archive:

    python verification/generate_block34.py

Do not run generators while the frozen verification runner is active. Generated
project constants in the environment audit are separate from source-declared
theorem counts. This release does not claim an independent dependency rebuild or
independently implemented kernel audit.
