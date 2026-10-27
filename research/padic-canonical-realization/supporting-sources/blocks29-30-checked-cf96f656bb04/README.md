# Komorebi p-adic program: Blocks 29–30

Start with REPORT.md and RESULTS.json. RESULTS.json is the authoritative status
of this release. It is generated only after the final compiler phases. Historical
candidate and development records are not alternative success claims.

The active project contains all 75 production Lean modules through Blocks29–30.
The seven new modules construct least invariant products of coordinate p-power
ideals and normalize them to heterogeneous cyclic coordinates. The resulting
machine retains the canonical all-coefficient output theorem.

Run `python verify_release.py` for read-only artifact/evidence replay. It checks
hashes, source preservation, all theorem axiom coverage, final command exits and
expected negative-control diagnostics. It does not re-run the Lean compiler.
`REPRODUCE.sh` performs a fresh project-only build and all recorded verification
phases using an explicitly supplied exact-pinned offline runtime. Reproduction
changes receipts; re-seal a new artifact rather than treating old file hashes as
unchanged. No runtime or font files are included.

`history/Block28/` retains the focused verified predecessor unchanged. The incoming
unverified Blocks29–30 candidate is retained byte-for-byte in `history/` and its
unsuccessful logs are separate. `REPAIR.diff` changes only proof fragments in the
example module. `CANDIDATE_STATEMENT_PRESERVATION.json` records all 78 unchanged
candidate theorem statements. `PREDECESSOR_SOURCE_PRESERVATION.json` checks all
67 inherited mathematical source files and 800 inherited theorem declarations.

Generic and mask-specific Python audits are exact independent-route finite checks,
not a formally verified executable refinement. Read PROOF_BOUNDARY.md before
interpreting minimality, cardinality, runtime, or cross-precision claims.
