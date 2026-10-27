# Block 29 proof guide

1. `StraightCompatibleX/Y/Z` state the exact ordered two-half-edge
   reconstruction contract for arbitrary fine links.
2. `StraightCompatible*.gauge` prove that these contracts are invariant under
   simultaneous coarse and fine gauge transformations.
3. `two_halfShift*_frameEmbed_of_straightCompatible` prove exact directional
   Clifford intertwining without assuming canonical fine links.
4. `arbitraryRefinedSevenFactorWalk_frameEmbed` composes the three contracts
   through the complete factorwise `M-X-Y-Z-Y-X-M` walk.
5. `finePathXXYY_frame`, `finePathYYXX_frame`, and
   `fineLargePlaquetteXY_frame` prove that canonical refinement transports the
   coarse plaquette exactly to the two-by-two fine Wilson loop.
6. `exact_refinement_can_preserve_nonflat_plaquette` proves that exact walk
   refinement and nontrivial curvature can coexist.
7. `FineEdgePair.two_halfSteps_embed_product` identifies the coarse link
   actually reconstructed by an arbitrary ordered half-link pair.
8. `FineEdgePair.fineIntertwiningDefect_eq_embed` and
   `fineIntertwiningDefect_eq_zero_iff` isolate the exact adjacent-scale
   obstruction.
9. `directionalShift_sub_ip`, `directionalShift_sub_stateIP`, and
   `FineEdgePair.fineIntertwiningDefect_energy` give the exact Hilbert mismatch
   formula in the orthogonal Clifford channels.
10. `flatQuarterCube_flat` and `quarterPair_fineDefect_nonzero` provide the
    flat-but-incompatible counterexample.
11. `no_universal_flatness_implies_refinement` formally rejects the original
    unconditional curvature-only zero-defect rule.
