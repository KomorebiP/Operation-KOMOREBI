import PaperIRelease.PacketTopologyGeneral
import Mathlib.Analysis.Normed.Field.WithAbs
import Mathlib.Algebra.Field.ZMod

/-! Boundary checks over an actually trivially valued complete field. -/

noncomputable section
set_option autoImplicit false

namespace Komorebi.PaperIRelease.GeneralPacketTopologyBoundary

open Komorebi.Foundation Komorebi.Foundation.LinearProjectorFamily
open GeneralPacketTopology

instance : Fact (Nat.Prime 2) := ⟨Nat.prime_two⟩

abbrev TrivialField := WithAbs (AbsoluteValue.trivial : AbsoluteValue (ZMod 2) ℝ)

instance : Fintype TrivialField :=
  Fintype.ofEquiv (ZMod 2) (WithAbs.equiv _).toEquiv.symm

example : NormedField TrivialField := inferInstance
example : CompleteSpace TrivialField := inferInstance

instance : IsClosed ((⊥ : Submodule TrivialField TrivialField) : Set TrivialField) := by
  simp

theorem nonzero_norm_one (x : TrivialField) (hx : x ≠ 0) : ‖x‖ = 1 := by
  rw [WithAbs.norm_eq_apply_ofAbs]
  apply AbsoluteValue.trivial_apply
  intro h
  exact hx ((WithAbs.equiv _).injective (by simpa using h))

def identityPacket : LinearProjectorFamily TrivialField TrivialField Unit where
  proj _ := LinearMap.id
  idempotent _ _ := rfl
  orthogonal hij := (hij (Subsingleton.elim _ _)).elim
  complete x := by simp

theorem identity_bounded (i : Unit) :
    IsBoundedLinearMap TrivialField (identityPacket.proj i) :=
  (identityPacket.proj i).isLinear.with_bound 1 (fun _ ↦ by simp [identityPacket])

theorem preserves_bot : identityPacket.Preserves (⊥ : Submodule TrivialField TrivialField) := by
  intro i x hx
  simpa [identityPacket] using hx

theorem preserves_top : identityPacket.Preserves (⊤ : Submodule TrivialField TrivialField) := by
  intro i x hx
  trivial

/-- This instantiates the full theorem with a trivially valued scalar field,
and therefore cannot accidentally require a nontrivial valuation. -/
theorem trivial_field_exact :
    CompleteSpace (LinearMap.range ((identityPacket.restrictTo ⊥ preserves_bot).proj ())) ∧
      CompleteSpace (LinearMap.range (identityPacket.proj ())) ∧
      CompleteSpace (LinearMap.range ((identityPacket.descendTo ⊥ preserves_bot).proj ())) ∧
      IsBoundedLinearMap TrivialField (identityPacket.packetInclusion ⊥ preserves_bot ()) ∧
      IsBoundedLinearMap TrivialField (identityPacket.packetQuotientMap ⊥ preserves_bot ()) ∧
      Function.Injective (identityPacket.packetInclusion ⊥ preserves_bot ()) ∧
      LinearMap.range (identityPacket.packetInclusion ⊥ preserves_bot ()) =
        LinearMap.ker (identityPacket.packetQuotientMap ⊥ preserves_bot ()) ∧
      Function.Surjective (identityPacket.packetQuotientMap ⊥ preserves_bot ()) ∧
      IsBoundedLinearMap TrivialField ((identityPacket.descendTo ⊥ preserves_bot).proj ()) :=
  banach_packet_shortExact identityPacket identity_bounded ⊥ preserves_bot ()

theorem trivial_field_quotient_bound (z : TrivialField ⧸ (⊥ : Submodule TrivialField TrivialField)) :
    ‖quotientProjectorCLM identityPacket identity_bounded ⊥ preserves_bot () z‖ ≤ ‖z‖ := by
  simpa using quotient_bound identityPacket identity_bounded ⊥ preserves_bot () 1
    (by norm_num) (fun x ↦ by simp [identityPacket]) z

theorem trivial_field_whole_quotient_zero
    (z : TrivialField ⧸ (⊤ : Submodule TrivialField TrivialField)) :
    quotientProjectorCLM identityPacket identity_bounded ⊤ preserves_top () z = 0 :=
  Subsingleton.elim _ _

end Komorebi.PaperIRelease.GeneralPacketTopologyBoundary

#print axioms Komorebi.PaperIRelease.GeneralPacketTopologyBoundary.trivial_field_exact
#print axioms Komorebi.PaperIRelease.GeneralPacketTopologyBoundary.nonzero_norm_one
