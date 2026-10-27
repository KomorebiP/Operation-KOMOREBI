# Paper III inherited Lean dependency manifest — Papers I–II v1.2.1

Paper III cites the following twelve unique declarations from the separately verified Papers I–II v1.2.1 release. They occur in fourteen manuscript references because `refineCoordinates_self` and `refineCoordinates_comp` each support two distinct claims.

- Bundle: `Projector_Resolved_Seed_Calculus_Papers_I_II_v1.2.1_Complete_Bundle.zip`
- SHA-256: `a20cf9353f0e882834d31e665dfd819a04e43fa606d402309be63e3b94447052`
- Boundary: these declarations are not imported or recompiled by the standalone Paper III Lean project; Paper III's parity checker validates its inherited status annotations against this frozen manifest and rejects Paper III namespace targets in inherited annotations.

| ID | Inherited Lean declaration | Role in Paper III |
| ---: | --- | --- |
| 1 | `Komorebi.PacketNaturalityCompletion.Reachability.algebraicOrbitHull_le_reachable_support` | Reachability support hull |
| 2 | `Komorebi.PacketNaturalityCompletion.Reachability.unreachable_nonzero_packet_obstruction` | Unreachable-packet obstruction |
| 3 | `Komorebi.PaperII.NestedRefinement.refineCoordinates` | Nested coordinate refinement |
| 4 | `Komorebi.PaperII.NestedRefinement.coordinateRefinementEquiv` | Refinement equivalence |
| 5 | `Komorebi.PaperII.NestedRefinement.refineCoordinates_self` | Identity refinement |
| 6 | `Komorebi.PaperII.NestedRefinement.coarsenCoordinates_refineCoordinates` | Coarsen-after-refine identity |
| 7 | `Komorebi.PaperII.NestedRefinement.refineCoordinates_coarsenCoordinates` | Refine-after-coarsen identity |
| 8 | `Komorebi.PaperII.NestedRefinement.refineCoordinates_comp` | Refinement cocycle and functoriality |
| 9 | `Komorebi.PaperII.NestedRefinement.coordinateRefinementEquiv_trans` | Transitivity of refinement equivalences |
| 10 | `Komorebi.PaperII.NestedRefinement.coordinateOperator_comp` | Coordinate-operator composition |
| 11 | `Komorebi.PaperII.NestedRefinement.coordinateOperator_naturality` | Coordinate-operator naturality |
| 12 | `Komorebi.PacketNaturalityCompletion.Packets.transferBlock_pow_eq_packetPathSum` | Prior packet-path power identity |
