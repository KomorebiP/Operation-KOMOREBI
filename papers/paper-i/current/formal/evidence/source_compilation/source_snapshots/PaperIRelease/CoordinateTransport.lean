import PaperIRelease.AlgebraSupport
import KomorebiVerification.PaperITransport
set_option autoImplicit false
noncomputable section
namespace Komorebi.PaperIRelease.CoordinateTransport
open Komorebi.Foundation
universe u v w x
variable {K : Type u} [Field K]
variable {X : Type v} [AddCommGroup X] [Module K X]
variable {Y : Type w} [AddCommGroup Y] [Module K Y]
variable {I : Type x} [Fintype I]

/-- Conjugation restricts to an actual linear equivalence of each packet range. -/
def packetRangeEquiv (P : LinearProjectorFamily K X I) (U : X ≃ₗ[K] Y) (i : I) :
    (P.proj i).range ≃ₗ[K] ((P.conjugate U).proj i).range where
  toFun x := ⟨U x, by
    obtain ⟨z, hz⟩ := x.property
    exact ⟨U z, by simp [← hz]⟩⟩
  invFun y := ⟨U.symm y, by
    obtain ⟨z, hz⟩ := y.property
    exact ⟨U.symm z, by simp [← hz]⟩⟩
  left_inv _ := by apply Subtype.ext; exact U.symm_apply_apply _
  right_inv _ := by apply Subtype.ext; exact U.apply_symm_apply _
  map_add' _ _ := by apply Subtype.ext; exact U.map_add _ _
  map_smul' _ _ := by apply Subtype.ext; exact U.map_smul _ _

/-- Packet dimension is invariant, with explicit lifts for different universes. -/
theorem packet_rank_invariant (P : LinearProjectorFamily K X I) (U : X ≃ₗ[K] Y) (i : I) :
    Cardinal.lift.{w} (Module.rank K (P.proj i).range) =
      Cardinal.lift.{v} (Module.rank K ((P.conjugate U).proj i).range) :=
  (packetRangeEquiv P U i).lift_rank_eq

/-- Every support relation, in particular a support preorder, is preserved literally. -/
theorem support_pattern_invariant (P : LinearProjectorFamily K X I) (U : X ≃ₗ[K] Y)
    (rel : I → I → Prop) (T : Module.End K X) :
    OperatorSupported (P.conjugate U) rel (conjugateEnd U T) ↔ OperatorSupported P rel T := by
  rw [operatorSupported_iff_ambient, operatorSupported_iff_ambient]
  constructor
  · intro h b a hab
    have hz := h b a hab
    rw [conjugate_transferBlock] at hz
    exact Komorebi.PacketNaturalityCompletion.Reachability.conjugateEnd_eq_zero_iff U _ |>.mp hz
  · intro h b a hab
    rw [conjugate_transferBlock, h b a hab]
    ext y
    simp [conjugateEnd]

end Komorebi.PaperIRelease.CoordinateTransport
