import PaperIRelease.PacketSourceRank

set_option autoImplicit false
noncomputable section

namespace Komorebi.PaperIRelease.PureBoundaryTests

open Cardinal Set Komorebi.Foundation Komorebi.SeedRankBasics
open Komorebi.PacketNaturalityCompletion.Reachability
open FiniteDigraph

universe u
variable {𝕜 X I : Type u} [Field 𝕜] [AddCommGroup X] [Module 𝕜 X] [Fintype I]

/-- With at most one packet all vectors are pure, so the constrained minimum
is exactly the original cardinal-valued seed rank. -/
theorem singleton_packet_rank [Subsingleton I]
    (A : Subalgebra 𝕜 (Module.End 𝕜 X)) (P : LinearProjectorFamily 𝕜 X I) :
    packetPureSeedRank A P = seedRank A X := by
  apply le_antisymm
  · obtain ⟨S, hS, hc⟩ := exists_generating_set_card_eq_seedRank A X
    rw [← hc]
    exact packetPureSeedRank_le_card ⟨hS, fun _ _ _ _ _ _ ↦ Subsingleton.elim _ _⟩
  · exact seedRank_le_packetPureSeedRank A P

/-- On the zero module the minimum is zero, even when indices exist and
every projector is zero. -/
theorem zero_module_rank [Subsingleton X]
    (A : Subalgebra 𝕜 (Module.End 𝕜 X)) (P : LinearProjectorFamily 𝕜 X I) :
    packetPureSeedRank A P = 0 := by
  apply le_antisymm
  · have hgen : PureGenerates A P (∅ : Set X) := by
      refine ⟨?_, ?_⟩
      · rw [Generates, Submodule.span_empty]
        exact Subsingleton.elim _ _
      · simp
    simpa using packetPureSeedRank_le_card hgen
  · exact zero_le

/-- The identity projector on a countably infinite-dimensional rational
space. There is deliberately no finite generation hypothesis. -/
def infiniteSinglePacket : LinearProjectorFamily ℚ (ℕ →₀ ℚ) Unit where
  proj _ := LinearMap.id
  idempotent _ _ := rfl
  orthogonal hij := (hij (Subsingleton.elim _ _)).elim
  complete x := by simp

theorem infinite_single_packet_rank :
    packetPureSeedRank (packetGeneratedAlgebra infiniteSinglePacket ∅) infiniteSinglePacket =
      seedRank (packetGeneratedAlgebra infiniteSinglePacket ∅) (ℕ →₀ ℚ) :=
  singleton_packet_rank _ _

/-- The exact weighted source formula applies unchanged to infinite packet
dimensions, and the no-generator edge condition is discharged, not supplied. -/
theorem infinite_single_source_formula :
    packetPureSeedRank (packetGeneratedAlgebra infiniteSinglePacket ∅) infiniteSinglePacket =
      Cardinal.sum (fun C : Sources (TransferEdge infiniteSinglePacket ∅) ↦
        localPureSeedRank (packetGeneratedAlgebra infiniteSinglePacket ∅) infiniteSinglePacket
          (projector_mem_generatedAlgebra infiniteSinglePacket ∅)
          (component (TransferEdge infiniteSinglePacket ∅)) C.val) := by
  apply source_component_pureSeedRank
  rintro a b ⟨T, hT, _⟩
  exact hT.elim

/-- Zero deletion preserves the constrained cardinal minimum, including the
case of an entirely zero local packet system. -/
theorem deleted_zero_rank
    (A : Subalgebra 𝕜 (Module.End 𝕜 X)) (P : LinearProjectorFamily 𝕜 X I) :
    packetPureSeedRank A P.discardZeros = packetPureSeedRank A P :=
  packetPureSeedRank_discardZeros A P

end Komorebi.PaperIRelease.PureBoundaryTests

#print axioms Komorebi.PaperIRelease.PureBoundaryTests.singleton_packet_rank
#print axioms Komorebi.PaperIRelease.PureBoundaryTests.zero_module_rank
#print axioms Komorebi.PaperIRelease.PureBoundaryTests.infinite_single_source_formula
