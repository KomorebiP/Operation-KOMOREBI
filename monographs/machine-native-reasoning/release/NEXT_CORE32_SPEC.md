# Exact restart: Core 3.2, partition correction memory

This is a specification and proof plan, not a completed Lean result. The unchanged
source is `source/core_v0.2.tex`, label `r:occupancy`, lines 335–340, with the
partition-evidence setup immediately before it. The existing `Correction.lean`
proves general correction-signature congruence, realizability and minimality.

## Keep the source contract

Use a finite world set Ω and a partition into nonempty cells, equivalently a
surjective cell map c : Ω → I. The target t : Ω → Y need not be onto, and the
ambient target type need not be finite. Use the actually attained pair type
D = range (fun ω => (c ω, t ω)) so its finiteness follows from finite Ω. Empty
candidate subsets are legitimate and represent contradiction.

Admitted evidence is exactly the preimages c⁻¹(J) of cell subsets J. Construct an
actual `EvidenceAlgebra Ω` with this event collection and prove the univ and
intersection laws. Do not silently admit an event that splits one cell or remove
single-cell events. The counting theorem is relative to this exact evidence family.

## Required endpoints

1. Define occupancy of V ⊆ Ω as the subset of attained pairs D met by V.
2. Prove signature equality iff occupancy equality. To recover occupancy, query
   the single-cell evidence and inspect each attained target. Conversely, show
   that union-of-cells filtering and the target image are determined by occupancy.
3. Exhibit every occupancy subset. A convenient witness is the full preimage of
   that subset under Ω → D. Surjectivity supplies its occupied pairs; disjointness
   of pair fibres prevents extra pairs. This is an alternative to the prose's
   one-representative-per-pair construction and must be identified as such.
4. Construct an actual equivalence between attained correction signatures and
   the powerset of D, not only two unrelated cardinal inequalities.
5. Prove the number of attained signatures is 2^(card D). Retain unused target
   values outside D and permit cells with multiple attainable target values.
6. Construct the exact r-bit occupancy encoding, readout and evidence update.
   Then use the inherited minimality theorem or the signature equivalence to
   prove every exact fixed-width b-bit memory requires r ≤ b. Do not promote
   this to a variable-length, average-bit, or runtime lower bound.
7. Connect the endpoint to the raw source partition and target data and prove the
   four-cell/eight-world example. Source theorem count increases by one only after
   all required clauses are mapped and accepted.

## Boundary and rejection controls

Preserve the empty candidate set and contradictory filtered result. Include a
cell intersecting two target fibres, duplicate target values across different
cells, a target value never attained, and the one-cell constant-target case.
Show that retaining only the current target set can lose a later correction.
Show that adding an event inside a cell invalidates old occupancy sufficiency.
Show that dropping individual-cell events can destroy the occupancy lower bound.
Reject a claimed r-1 fixed-bit encoding when D has r attainable pairs.

## Verification

Start from the accepted Core 2.5 receipt. Authenticate its full source pins and
preserve every accepted substantive module and source-book file. Add actual
source-facing API checks, transitive axiom auditing, own-kernel replays, expected
negative diagnostics and a finite exact enumerator independent of the Lean proof.
Run two sequential cold gates, one from an independently extracted frozen source
snapshot, and compare all production objects. Keep every failure or interruption
as a failure. Do not label the selected correspondence 27/27 before acceptance.
