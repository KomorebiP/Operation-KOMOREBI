# Komorebi H12 phase-functional continuation v0.5.0

Read PROOF.md for the results and the still-open arithmetic identity.
FORMALIZATION_SCOPE.md distinguishes the 154 checked Lean theorem constants from
the gamma application and interval computations outside Lean.

## Reproduce

Python dependencies in the shipped environment are SymPy and mpmath; exact
versions are recorded in MANIFEST.json. No network is required for the checks.

    python checks/validate_manifest.py MANIFEST.json --root .
    python checks/exact_checks.py
    python checks/interval_checks.py --digits 90
    python checks/interval_checks.py --digits 120

Use the user's pinned portable Lean 4.34.0-rc2 runtime with Mathlib revision
aeb72f1e9981b6d35b426b16dca7759be3e7ba06. The runtime is external, not included.
Run each part synchronously; each authenticates the previous stage's outputs:

    python checks/run_lean.py --runtime PATH_TO_PINNED_KIT --part 1
    python checks/run_lean.py --runtime PATH_TO_PINNED_KIT --part 2
    python checks/run_lean.py --runtime PATH_TO_PINNED_KIT --part 3
    python checks/run_lean.py --runtime PATH_TO_PINNED_KIT --part 4

Verification writes evidence files, so validate the shipped manifest BEFORE
rerunning. A rerun has different timings and needs a newly generated manifest.
The prior source-and-evidence ZIP is preserved, but its computations are not
silently counted as new numerical runs in this release.

The interval evidence covers rounding through mpmath.iv and the explicit tail.
It is not a proof that the enclosed near-zero arithmetic discrepancy is zero.
