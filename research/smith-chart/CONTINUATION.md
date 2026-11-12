# Smith chart continuation checkpoint

The maintained continuation and gap-closure record is now
[unified/README.md](unified/README.md), with one canonical research reader and a
single current source/check download. This file preserves the earlier checkpoints.

**Superseded target status, 12 November 2026.** The new supplied
[exact-six checkpoint](continuation/README.md) gives a positive transformer-free
witness and matching degree lower bound for the original target. The remaining
open-status statements here describe earlier work. The class-142 search remains
unresolved in its own topology, but is unnecessary for the achieved global minimum.

**Base:** repository revision `b1546c80c88640f7dad5fe4300c1739523fa1b4b`,
with the 172-file archive SHA-256
`39fd0d659ef6c006eebb129e08a9b2ced72ce5b857ba846d6481711c951c371e`.
This checkpoint records the 11 November 2026 continuation; the original
archive and its historical audit files remain unchanged.

## Target and distinction

The larger unresolved question is whether the particular degree-six target
in the archive has an exact finite, passive, transformer-free RLC one-port
with six reactive elements. A valid construction requires a topology,
strictly positive component values, and an exact rational identity. An
impossibility result must cover every admissible topology and node count.
Finite searches, small residuals, or failures of one topology do not decide
that question. The archive's seven-reactive construction and ideal-transformer
six-reactive construction have different allowed component classes.

## Routes checked in this continuation

1. **One-state approximation, completed in the stated scope.** The archive
   asserts that the affine limit is realizable by a positive one-inductor RL
   network. The [supplement](../../docs/demonstrations/SMITH_FIRST_ORDER_RL.md)
   gives explicit component formulas for its whole parameter range. The
   [separate Lean companion](formal/README.md) checks their algebra and
   positivity with explicit hypotheses; its source mapping and review are
   self-review. This is an auxiliary result, not a solution of the six-element
   problem or a formalization of the full arbitrary-order theorem.
2. **Five-node graph obstruction, finite check only.** A separate
   breadth-first [recount](computations/README.md) confirms the archived
   14,400 placements, 1,934 filter survivors, 168 symmetry classes and their
   orbit sizes. It does not audit the electrical necessity of every filter or
   solve component feasibility. Larger-node graphs are outside this recount.
3. **Five-node construction, unresolved.** A bounded numerical restart of
   archived candidate 142 did not produce an exact identity. The
   [run record](computations/verification/five-node-fit-003.json) contains
   50 starts on one reactive placement, the training and holdout grids, and
   the log-parameter bounds. An [exact rational follow-up](computations/verification/candidate-142-exact-001.json)
   rules out the recorded decimal values themselves at three real frequencies.
   Neither check rules out that placement, nearby real values, or other node
   counts.

## Next useful work

For class 142, derive the exact nodal numerator and denominator, clear
denominators, and retain the positive-component conditions. A possible
constructive continuation is to fix enough free parameters to obtain a
square system and seek a rational interval certificate for a positive root;
verify the resulting transfer identity separately. A failed choice of fixed
parameters would not exclude the topology. Alternatively, an exact
elimination certificate for a specified class would rule out only the class
and hypotheses it covers. A full
impossibility proof must also justify the graph reductions and cover the
remaining admissible node counts. Separately, the archive's full
arbitrary-order and degree claims require their own proof/source audit and
formal mapping; the first-order RL lemmas do not supply those results.

## Presentation and completion continuation, base f8dbf83b

The next continuation starts from
`f8dbf83bb2a67139be7800768ce9a8be2109b28a`. The
[edition record](edition/README.md) preserves its graphics, language,
proof-review, and computation evidence.

- **Singular prediction and a real-packet boundary, completed in scope.** The
  [new note](../../docs/demonstrations/SMITH_SINGULAR_COMPLETION.md) proves the
  nullspace/range test, an exact missing complex value, and the full feasible
  region for two real scalar packets at radius one half. Six selected real
  algebraic declarations pass the pinned Lean replay, axiom audit, and two
  rejected negative controls. The general Hermitian and interpolation arguments
  remain written proofs with a checked classical source and symbolic examples.
- **Class 142 exact encoding, completed; construction remains open.** A
  [symbolic derivation](computations/derive_candidate_142.py) gives the seven
  numerator and denominator coefficients and thirteen cross-product equations
  of degree at most four. Its spanning-tree/forest calculation agrees with a
  direct determinant expansion. Nonnegative conductances and strictly positive
  reactive parameters remain constraints. No positive solution or exclusion
  has been certified.
- **Arbitrary-order route, reviewed.** The displayed geometric series, equality
  point for both signs of the parameter, strict boundary average, distinct-pole
  degree argument, and normalized uniform bounds survived self-review. No
  general-order Lean theorem was added.

The next useful synthesis step is an exact positive-root or exclusion
certificate for the explicit class-142 equations, or a different topology with
a changed structural premise. The global six-reactive transformer-free
question still requires all admissible classes and node counts. Another
unchanged finite-grid fit would not close that question.

## Structural diagram redesign, base b1a3dc4d

The next presentation pass starts from `b1a3dc4d25820c028d37257a00963fe4988d1f93`.
Eight schematic figures (8, 11, 18, 26, 27, 30, 31 and 37) receive new geometry,
readable labels and phone layouts. The page now has twelve mobile variants;
the expanded view uses the same selected source. Circuit connections, original
artwork, all mathematical expressions and existing proof receipts are retained.
The figure-8 label check is a completed exact finite computation for the
all-positive coupling branch, not a new interpolation or synthesis theorem.
