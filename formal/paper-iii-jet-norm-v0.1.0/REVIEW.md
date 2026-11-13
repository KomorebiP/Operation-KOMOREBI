# Focused Paper III jet norm review

Audited source revision: `f49e00d6088bbc8dca4f8a3a70b232db1eea085b`.
The exact chapter, original Proposition 17.3 row, and four retained source
identities are recorded in [CLAIM_MAP.json](CLAIM_MAP.json).

## Normalized claim and verdict

For finite complete idempotent packet systems with bounded projectors and an
order-`n` continuous multilinear map, the literal range jet obeys both the
sharper output-projector bound and the projector-product bound. Zero packets
remain admissible. If the output is an actual Hilbert orthogonal projection,
the range jet's norm is at most the full multilinear map's norm. A projection
onto a nonzero subspace has norm one.

**Verdict: proved as written**, with the orthogonal projection and nonzero
hypotheses explicitly retained in the named Lean clauses. The actual
iterated-derivative specializations add no differentiability assertion for an
arbitrary function. They inherit the chosen derivative and agree with the
manuscript under its stated differentiability assumptions.

## Dependency graph and obligations

| Implication | Source and check | Result |
|---|---|---|
| A projector fixes every vector in its actual range | Retained `System.projector_range_self` | Passed |
| Each input range vector satisfies `norm x <= norm P * norm x`, including zero projectors | Apply the bounded projector to that fixed vector | Passed |
| The finite product of those estimates bounds the product of input norms | Nonnegative product monotonicity; no division by a vector or projector norm | Passed |
| The projected multilinear evaluation obeys the full projector-product bound | New `continuousPacketJet_norm_le_prod` on the existing range-jet definition | Passed |
| Contractive output implies the unit-factor bound | Retained sharper range estimate and scalar multiplication monotonicity | Passed |
| Actual Hilbert orthogonal output is contractive | Pinned Mathlib `Submodule.starProjection_norm_le`, with `HasOrthogonalProjection` and explicit equality to the output projector | Passed |
| A projection onto a nonzero subspace has norm one | Pinned Mathlib `Submodule.norm_starProjection`; nonzero hypothesis retained | Passed |
| Zero input or output packets give zero jets | New literal range-map equalities; an actual input slot is required for the input law | Passed |
| Algebraic packet annihilation alone implies norm at most one | Explicit oblique complete-system counterexample has a projector norm at least three | Refuted; not a premise of the positive results |
| The packet Taylor remainder or entire expanded monograph is certified | Not asserted | Out of scope |

The retained modules are `PacketCoordinates`, `MultilinearPacketJets`,
`BoundedPacketJetNorm` and `ContinuousPacketJets`. They are copied without
changes, cold rebuilt, audited by module ownership and replayed with the new
module. The remaining twelve modules of the original sixteen-module closure
are not newly replayed by this companion.

The new product proof follows the manuscript's fixed-vector argument in a
form that handles zero projectors directly. The sharper range estimate does
not require input orthogonality. Norm one is not substituted for a zero
projector. The Hilbert results use `V.starProjection`, rather than treating
the algebraic `System.orthogonal` field as an inner-product hypothesis.

## Proofreading

Scope: the packet-jet section from its heading through the end of the proof
of Proposition 17.3, before the packet Taylor corollary. The record includes
the exact line interval, excerpt identity and local reference checks.

- Routine edits: none; no objective prose or LaTeX correction was needed.
- Mathematical-token changes: none.
- Unresolved proofreading findings: none in this scope.
- Validation: source identity, uniquely resolved references, balanced
  environments and display delimiters. No TeX build or PDF rendering was
  required because the manuscript was not edited.
- Coverage limit: this pass does not proofread the Taylor corollary or later
  sections.

## Controls, remaining work and provenance

The positive fixtures cover a redundant zero input packet, zero output,
the nonzero value of an order-zero range jet, the actual orthogonal-output
estimate, and a complete oblique projector system. Negative controls attempt
to infer general contractivity, give a unit nullary map norm zero, give the
zero orthogonal projection norm one, erase a nonzero nullary jet, admit an
unfinished proof, and introduce an extra owned axiom. Only the declared
mathematical or audit failure qualifies as an accepted rejection.

The new results complete the missing norm clauses of Proposition 17.3.
The packet Taylor formula and integral error estimate remain separate next
targets. All original artifact identities and evidence remain accessible.
This is same-assistant mathematical and editorial self-review, paired with
execution of the same official Lean kernel. No independent peer review or
separate-kernel result is claimed.

The earlier verification attempt is preserved under `evidence/attempt-001`.
It failed on an incorrectly typed negative fixture and was not accepted as a
rejection pass. The final evidence records the corrected fixture and complete
cold verification.
