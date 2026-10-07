# Known limitations

The flagship covers the stated rational-mask Mahler class at each fixed prime-power
precision. It does not prove a theorem about every arithmetic seed or all Komorebi
branches. It does not prove analytic convergence at numerical p-adic arguments.

The canonicality/minimum result compares linear realizations over a fixed ring and
alphabet, with equality on every digit word. It is not a minimum-DFA theorem, a
minimum-generator-rank theorem, or a claim that chosen matrices are literally unique.
A linear reachable span may contain vectors outside the deterministic initial orbit.

The efficient formally refined executable compiler remains open. The reference Python
programs are exact finite implementations with audits, not proof-producing substitutes
for Lean or formally verified compiled implementations of its noncomputable interfaces.
Mathematical state-count reductions are not elapsed-time or memory benchmarks.

State-level reduction maps across precisions, a single profinite/p-adic machine, and
the general filtered obstruction-resolution compiler theorem are later research.
Output compatibility across precisions is a different, already stated theorem.

The retained build uses Lean 4.34.0-rc2 and the dependency revisions in the manifest.
The project sources were built against cached dependencies. Independent dependency
rebuilding, a stable-Lean migration, independent kernel implementation, and independent
human review are not asserted. A public bootstrap of this repackaged candidate remains
a release gate, not an accomplished result.

The source contains intentionally invalid negative-control files under verification/.
Those are required to fail and are separate from the production source under lean/.
No release should infer proof success merely from absence of placeholder text.

No first-ever, historical-priority, universal-breakthrough, or full-project completion
claim is made. The point of release is to make stated results inspectable and usable,
while preserving a clear correction process.

For the separate proposed agenda, see [FUTURE_RESEARCH.md](FUTURE_RESEARCH.md). For the remaining publication checks, see [PUBLICATION_STATUS.md](PUBLICATION_STATUS.md).
