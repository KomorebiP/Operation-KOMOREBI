import Komorebi.Multiverse.HigherObstructionExample
import Komorebi.Multiverse.ResidualDescent

/-!
# A higher data obstruction forced purely by world geometry

The coefficient system is deliberately trivial (`Unit`).  Thus every pairwise
mathematical residual vanishes whenever the corresponding two worlds can
amalgamate.  The triple still cannot glue because the world geometry itself has
no common upper world.  This separates geometric obstruction from coefficient
complexity.
-/

namespace Komorebi.Multiverse

abbrev UnitTransport := TransportSystem.constant TN Unit

def unitBoundaryData : UnitTransport.LocalFamily boundaryTriple where
  value := fun _ _ => ()

theorem unitBoundaryData_pairwise :
    UnitTransport.PairwiseCompatible unitBoundaryData := by
  intro i hi j hj
  obtain ⟨u, hui, huj⟩ := boundaryTriple_pairwise i hi j hj
  exact ⟨u, hui, huj, rfl⟩

theorem unitBoundaryData_not_joint :
    ¬ UnitTransport.JointCompatible unitBoundaryData :=
  UnitTransport.not_jointCompatible_of_world_obstructed boundaryTriple_not_joint unitBoundaryData

/-- All pair residuals vanish, yet the triple has no joint realization. -/
theorem unitBoundaryData_higherObstruction :
    UnitTransport.HigherDataObstruction unitBoundaryData :=
  ⟨unitBoundaryData_pairwise, unitBoundaryData_not_joint⟩

end Komorebi.Multiverse

namespace Komorebi.Multiverse

/-- The explicit boundary example is detected by the nontrivial degree-one theory. -/
theorem unitBoundaryData_detected_at_degree_one :
    UnitTransport.pairwiseBoundaryTheory.Obstruction 1 unitBoundaryData := by
  exact (UnitTransport.pairwiseBoundaryTheory_degree_one unitBoundaryData).2
    unitBoundaryData_higherObstruction

end Komorebi.Multiverse
