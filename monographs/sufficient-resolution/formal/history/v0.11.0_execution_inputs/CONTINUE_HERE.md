# Continue — Sufficient Resolution v0.11.0

Read README.md, BLOCK_11_THEOREMS.md, PROGRESS.md, AUDIT.json and
VERIFICATION_SUMMARY.md. All 60 inherited production sources must remain intact.

## State

764 theorem declarations in 65 production modules, with 901 named declarations.
The 36 added theorems are in five modules. Counts include helpers and classical
specializations. The current verification is block-scoped, NOT a new full-corpus
replay. Preserve that distinction and the incomplete predecessor-run evidence.

## New mathematics

For fixed bounded real Hilbert A and positive lambda tending to zero:

    B_lambda A g -> P_ker(A)^perp g,
    ||B_lambda A g-g|| -> ||P_ker(A)g||.

No closed range is needed. The proof uses actual density of range(A* A), not a
source-condition assumption on every g. For noise, require ||e||/sqrt(lambda)->0.
For inexact solvers, also require the actual normal residual divided by lambda to
vanish. These are sufficient conditions, not claimed necessary in every case.

Uniform source-filter convergence holds iff range(A) is closed. When it is not
closed, ||B_lambda A-P||=1 at every lambda>0. Predicted data still converge to the
projection on CLOSURE(range A). If v is in closure(range A) but not range(A), its
reconstructed sources cannot have a norm limit. Do not claim norm divergence from
that theorem, and do not replace approximate realization by actual realization.

## Verify

    python scripts/verify_block11.py --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2

This default rebuilds the block's project dependency closure. The documented
--reuse-project-dependencies mode records reused object hashes and rebuilds all
five new modules. Full-corpus command remains scripts/verify.py with the same
runtime argument, but no full fresh v0.11.0 run is claimed by this release.

## Next target

Discrepancy-based parameter selection: convert an explicit noise allowance into
an actual positive regularization parameter and prove convergence under the
appropriate range/normalization hypotheses. Keep the current asymptotic-parameter
results distinct from an algorithm that discovers the parameter. An independent
branch is a concrete infinite-dimensional dense nonclosed-range operator.
