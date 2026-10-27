# Komorebi Sufficient Resolution — v0.11.0

**Komorebi P.**

This cumulative source package adds strong regularization convergence, noisy-data
and solver consistency, the closed-range criterion for uniform convergence, and
convergence of predicted data to the closure of the realized range.

Read BLOCK_11_THEOREMS.md, PROGRESS.md, AUDIT.json and VERIFICATION_SUMMARY.md.
Inherited verification records are historical. The current block's verification
scope is recorded explicitly; it is not a fresh replay of all inherited modules.

## Verify this block and its dependencies

    python scripts/verify_block11.py --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2

The default serially rebuilds this block's project dependency closure. The optional
--reuse-project-dependencies reuses exact recorded compiled objects for inherited
modules and freshly compiles the five new modules. Both modes reuse pinned Mathlib.

## Full-corpus verification command

    python scripts/verify.py --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2

This is a reproduction command, not a statement that the complete current corpus
was freshly replayed in this release. Consult the actual scope in the summary.

## Finite rational checks

    python scripts/check_regularization_limits.py

Runtime: Lean 4.34.0-rc2, Mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06.
The portable runtime is not bundled. Kernel replays use Lean's own kernel, not an
independently implemented verifier. Python algorithms are tested, not formally
verified or extracted from Lean. Counts include helpers and classical results.
