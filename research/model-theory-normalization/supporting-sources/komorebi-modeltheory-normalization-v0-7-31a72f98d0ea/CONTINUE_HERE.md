# Continue from Model-Theory Normalization v0.7

Read NORMALIZED_CORE.md, FORMALIZATION_COVERAGE.md, RESULTS.md, PROOF_AUDIT_v07.md,
DEVELOPMENT_FAILURES.md and the current v07 manifests. Check distribution integrity
before a replay that rewrites results. Preserve the frozen v0.6 archive unchanged.

## Achieved mathematical endpoint

The exact modular integer-preimage basis now has an executable canonical triangular
normalizer. It preserves the integer lattice and is idempotent. Two normalized
bases are equal iff their lattices are equal in the fixed ambient coordinates.
Every pivot divides m; all persistent normalized entries are in [0,m]. The cached
normalized discovery loop preserves its exact preimage invariant and has the same
ordered output as the previously proved reference at every fuel budget. Its actual
outputs still compile to the original-language first-order defining formula.

## Next precise obligation

The stored-growth problem is closed. The end-to-end bit-cost problem is not.
Prove bounds for extended-gcd coefficients and temporary insertion/residue vectors
starting from a reduced cache and canonical residue row. Then compose with the
proved candidate and acceptance bounds. Distinguish arithmetic-operation counts,
integer bit lengths, and formal runtime cost. A post-normalization bound alone
must not be advertised as a bound on all temporary operands.

Optional independent next targets: optimized interleaved insertion/reduction,
canonical residue-submodule cache reuse, modular minimum-generator extraction,
minimum raw observation test selection, and stronger relational discovery.

## Reproduction

README.md gives full cold Lean and exact Python commands with pinned runtime.
The runtime and Mathlib cache are not bundled. No process in a saved state is
promised to still be running. A previous .olean path is execution history, not an
available dependency unless checked in the new runtime.
