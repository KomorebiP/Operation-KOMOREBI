# Final release review

The canonical theorem is `notes/mod7_good_reduction_irreducibility.md`:
absolute irreducibility of the attached residual RM representation for
14 not dividing C. It was checked in a fresh isolated audit, which read
the raw proof and primary theorem statements, and in a separate overlapping
review. Their agreement is supporting review evidence, not a substitute
for the written proof or a claim of formal Galois verification.

The local stratification theorem and exact scaling equivalence received
separate written reviews. Independent implementations checked all 42
smooth characteristic-seven fibers and all 452 smooth residue pairs at 11
and 19. Those bounded computations are not represented as a universal
integer-solution search.

The source and log hashes for 21 Lean theorems, five bounded experiments,
the modular-data computation, the canonical review and unchanged
predecessor copies were checked by `verify_artifacts.py`. Result:
`verification/VERIFICATION_SUMMARY.json`.

Proofreading coverage: final report, continuation guide, canonical joined
proof and the parent's new notes; component notes also have their authors'
and reviewers' checks. Routine final edits corrected prose spacing and
cross-reference clarity. No mathematical-token change was made during this
final proofreading pass. The canonical theorem's reviewed hash remains
unchanged. Historical component notes retain intermediate scopes; the
canonical theorem and final report state the final scope.

Material limitations: no completed exclusion of a primitive (3,5,7)
solution, no indexed modular-form elimination, no fresh Hilbert-space Magma
replay, no Beal theorem, and no global novelty claim. The remaining
irreducibility branch is 14 dividing C. Full level-lowering applicability
and correlated modular elimination are separate unfinished obligations.
