import PaperIRelease.PacketSourceLower
import PaperIRelease.PacketSourceUpper
import PaperIRelease.GraphSourceProjection

set_option autoImplicit false
noncomputable section

namespace Komorebi.PaperIRelease

open Cardinal Set Komorebi.Foundation Komorebi.SeedRankBasics
open Komorebi.PacketNaturalityCompletion.Reachability
open PacketAggregation FiniteDigraph

universe u
variable {𝕜 X I : Type u} [Field 𝕜] [AddCommGroup X] [Module 𝕜 X]
variable [Fintype I] [DecidableEq I]

/-- The exact cardinal formula for packet-pure seed rank. The components are
the actual quotient by mutual reachability of the actual generator transfer
graph. Their source property, existence, no-incoming action, and propagation
are proved by the imported graph theorems. Local ranks are genuine minima
under the actual compressed corner algebras. -/
theorem source_component_pureSeedRank
    (P : LinearProjectorFamily 𝕜 X I) (ops : Set (Module.End 𝕜 X))
    (hedges : EdgeSurjective P ops) :
    packetPureSeedRank (packetGeneratedAlgebra P ops) P =
      Cardinal.sum (fun C : Sources (TransferEdge P ops) ↦
        localPureSeedRank (packetGeneratedAlgebra P ops) P
          (projector_mem_generatedAlgebra P ops)
          (component (TransferEdge P ops)) C.val) := by
  apply le_antisymm
  · apply packetPureSeedRank_le_sum_local_of_generation
      (packetGeneratedAlgebra P ops) P (projector_mem_generatedAlgebra P ops)
      (component (TransferEdge P ops)) {C | Source (TransferEdge P ops) C}
    intro H hsource
    have hH : AlgebraInvariant (packetGeneratedAlgebra P ops) (H.restrictScalars 𝕜) := by
      intro T hT x hx
      exact H.smul_mem (⟨T, hT⟩ : packetGeneratedAlgebra P ops) hx
    have htop : H.restrictScalars 𝕜 = ⊤ :=
      submodule_eq_top_of_sources P ops hedges (H.restrictScalars 𝕜) hH (by
        intro C a ha x hx
        apply hsource C.val C.property
        have h := original_mem_grouped P (component (TransferEdge P ops)) a ⟨x, hx⟩
        simpa only [ha] using h)
    apply top_unique
    intro x _
    change x ∈ H.restrictScalars 𝕜
    rw [htop]
    trivial
  · apply sum_localPureSeedRank_le_of_compression
      (packetGeneratedAlgebra P ops) P (projector_mem_generatedAlgebra P ops)
      (component (TransferEdge P ops)) {C | Source (TransferEdge P ops) C}
    intro C hC a ha x
    exact sourceProjection_compression P ops ⟨C, hC⟩ ha x

end Komorebi.PaperIRelease

#print axioms Komorebi.PaperIRelease.source_component_pureSeedRank
