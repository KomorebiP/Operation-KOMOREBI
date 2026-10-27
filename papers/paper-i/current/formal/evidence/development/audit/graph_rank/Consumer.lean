import PaperIRelease.BoundedStar
import PaperIRelease.PacketSourceRank
import PaperIRelease.GraphSourceCount
import PaperIRelease.GraphSourceBoundary
import PaperIRelease.PacketPureBoundaryTests

set_option autoImplicit false
noncomputable section

open Komorebi.Foundation Komorebi.PaperIRelease
open Komorebi.PaperIRelease.FiniteDigraph
open Komorebi.PacketNaturalityCompletion.Reachability

namespace IndependentGraphRankAudit

def emptyPacket : LinearProjectorFamily ℚ (Fin 0 → ℚ) Empty where
  proj i := isEmptyElim i
  idempotent i := isEmptyElim i
  orthogonal {i} := isEmptyElim i
  complete x := by ext i; exact Fin.elim0 i

theorem empty_source_count_rank :
    packetPureSeedRank (packetGeneratedAlgebra emptyPacket ∅) emptyPacket = 0 := by
  let : ∀ i : Empty, Nontrivial (LinearMap.range (emptyPacket.proj i)) := fun i => isEmptyElim i
  have hp : PacketPropagating emptyPacket ∅ :=
    ⟨fun {a} => isEmptyElim a, fun i => isEmptyElim i⟩
  have h := packetPureSeedRank_eq_source_count emptyPacket ∅ hp
  let : IsEmpty (Sources (TransferEdge emptyPacket ∅)) := ⟨fun C => by
    obtain ⟨i, _⟩ := component_surjective (TransferEdge emptyPacket ∅) C.val
    exact isEmptyElim i⟩
  simpa only [Cardinal.mk_eq_zero] using h

end IndependentGraphRankAudit

#check Komorebi.PaperIRelease.packetPureSeedRank_bounds
#check Komorebi.PaperIRelease.source_component_pureSeedRank
#check Komorebi.PaperIRelease.packetPureSeedRank_eq_source_card
#check Komorebi.PaperIRelease.local_proj_zero_iff
#check Komorebi.PaperIRelease.packetPureSeedRank_discardZeros
#print axioms Komorebi.PaperIRelease.BoundedSupport.adjoint_closed_iff_symmetric
#print axioms Komorebi.PaperIRelease.BoundedSupport.star_subalgebra_iff_equivalence
#print axioms Komorebi.PaperIRelease.packetPureSeedRank_bounds
#print axioms Komorebi.PaperIRelease.source_component_pureSeedRank
#print axioms Komorebi.PaperIRelease.packetPureSeedRank_eq_source_card
#print axioms IndependentGraphRankAudit.empty_source_count_rank
