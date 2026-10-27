import PaperIRelease.PacketExactSequence
import Mathlib.Analysis.Normed.Operator.BoundedLinearMaps
import Mathlib.Analysis.Normed.Group.Quotient
import Mathlib.Topology.Algebra.Module.ContinuousLinearMap.Quotient

/-!
# Banach packet exact sequences over arbitrary normed fields

This includes trivially valued fields. Boundedness is an explicit hypothesis;
continuity alone is not substituted for boundedness. Every map is the actual
map from the algebraic packet exact sequence.
-/

noncomputable section
set_option autoImplicit false
set_option linter.style.haveILetI false

namespace Komorebi.PaperIRelease.GeneralPacketTopology

open Komorebi.Foundation Komorebi.Foundation.LinearProjectorFamily

universe u v w
variable {𝕜 : Type u} {X : Type v} {ι : Type w}
variable [NormedField 𝕜] [NormedAddCommGroup X] [NormedSpace 𝕜 X] [Fintype ι]

variable (P : LinearProjectorFamily 𝕜 X ι)
variable (hP : ∀ i, IsBoundedLinearMap 𝕜 (P.proj i))
variable (K : Submodule 𝕜 X) (hK : P.Preserves K)

def projectorCLM (i : ι) : X →L[𝕜] X :=
  { toLinearMap := P.proj i
    cont := ((hP i).toContinuousLinearMap (P.proj i)).continuous }

def restrictionCLM (i : ι) : K →L[𝕜] K where
  toLinearMap := (P.restrictTo K hK).proj i
  cont := ((projectorCLM P hP i).continuous.comp continuous_subtype_val).subtype_mk _

def quotientProjectorCLM (i : ι) : (X ⧸ K) →L[𝕜] (X ⧸ K) :=
  K.liftQL (K.mkQL.comp (projectorCLM P hP i)) (by
    intro x hx
    change K.mkQ (P.proj i x) = 0
    exact (Submodule.Quotient.mk_eq_zero K).mpr (hK i x hx))

@[simp] theorem quotientProjectorCLM_toLinearMap (i : ι) :
    (quotientProjectorCLM P hP K hK i).toLinearMap = (P.descendTo K hK).proj i := rfl

/-- Every original norm bound passes to the actual quotient norm. -/
theorem quotient_bound (i : ι) (C : ℝ) (hC : 0 ≤ C)
    (hbound : ∀ x : X, ‖P.proj i x‖ ≤ C * ‖x‖) (z : X ⧸ K) :
    ‖quotientProjectorCLM P hP K hK i z‖ ≤ C * ‖z‖ := by
  apply le_of_forall_pos_le_add
  intro ε hε
  obtain ⟨x, hx, hnorm⟩ := Submodule.Quotient.norm_mk_lt z
    (show 0 < ε / (C + 1) by positivity)
  have hbase : ‖quotientProjectorCLM P hP K hK i z‖ ≤ C * ‖x‖ := by
    rw [← hx]
    exact (Submodule.Quotient.norm_mk_le K (P.proj i x)).trans (hbound x)
  have hmul : C * ‖x‖ ≤ C * (‖z‖ + ε / (C + 1)) :=
    mul_le_mul_of_nonneg_left hnorm.le hC
  have hsmall : C * (ε / (C + 1)) ≤ ε := by
    rw [← mul_div_assoc]
    apply (div_le_iff₀ (show 0 < C + 1 by positivity)).mpr
    nlinarith
  exact hbase.trans (hmul.trans (by nlinarith))

include hP in
theorem quotientProjector_bounded (i : ι) :
    IsBoundedLinearMap 𝕜 ((P.descendTo K hK).proj i) := by
  obtain ⟨C, hC, hbound⟩ := (hP i).bound
  exact ((P.descendTo K hK).proj i).isLinear.with_bound C
    (quotient_bound P hP K hK i C hC.le hbound)

include hP in
theorem restrictedProjector_bounded (i : ι) :
    IsBoundedLinearMap 𝕜 ((P.restrictTo K hK).proj i) := by
  obtain ⟨C, _, hbound⟩ := (hP i).bound
  exact ((P.restrictTo K hK).proj i).isLinear.with_bound C
    (fun x ↦ hbound (x : X))

/-- The bounded additive operator norm is available even over a trivially
valued scalar field and equals the usual infimum of valid operator bounds. -/
def projectorNormedHom (i : ι) : NormedAddGroupHom X X :=
  (P.proj i).toAddMonoidHom.mkNormedAddGroupHom
    (Classical.choose (hP i).bound) (Classical.choose_spec (hP i).bound).2

theorem quotient_bound_operatorNorm (i : ι) (z : X ⧸ K) :
    ‖quotientProjectorCLM P hP K hK i z‖ ≤ ‖projectorNormedHom P hP i‖ * ‖z‖ :=
  quotient_bound P hP K hK i _ (norm_nonneg _) (fun x ↦ (projectorNormedHom P hP i).le_opNorm x) z

def packetInclusionCLM (i : ι) :
    LinearMap.range ((P.restrictTo K hK).proj i) →L[𝕜] LinearMap.range (P.proj i) :=
  (K.subtypeL.comp (LinearMap.range ((P.restrictTo K hK).proj i)).subtypeL).codRestrict
    (LinearMap.range (P.proj i)) (fun x ↦ (P.packetInclusion K hK i x).property)

def packetQuotientCLM (i : ι) :
    LinearMap.range (P.proj i) →L[𝕜] LinearMap.range ((P.descendTo K hK).proj i) :=
  (K.mkQL.comp (LinearMap.range (P.proj i)).subtypeL).codRestrict
    (LinearMap.range ((P.descendTo K hK).proj i))
    (fun x ↦ (P.packetQuotientMap K hK i x).property)

theorem packetInclusion_bounded (i : ι) :
    IsBoundedLinearMap 𝕜 (P.packetInclusion K hK i) :=
  (P.packetInclusion K hK i).isLinear.with_bound 1 (fun x ↦ by
    change ‖((x : LinearMap.range ((P.restrictTo K hK).proj i)) : K)‖ ≤ 1 * ‖x‖
    simp)

theorem packetQuotient_bounded (i : ι) :
    IsBoundedLinearMap 𝕜 (P.packetQuotientMap K hK i) :=
  (P.packetQuotientMap K hK i).isLinear.with_bound 1 (fun x ↦ by
    change ‖(Submodule.Quotient.mk (x : X) : X ⧸ K)‖ ≤ 1 * ‖x‖
    simpa using Submodule.Quotient.norm_mk_le K (x : X))

include hP in
theorem isClosed_packet (i : ι) : IsClosed (LinearMap.range (P.proj i) : Set X) := by
  apply ContinuousLinearMap.IsIdempotentElem.isClosed_range (p := projectorCLM P hP i)
  apply ContinuousLinearMap.ext
  intro x
  exact P.idempotent i x

variable [hclosed : IsClosed (K : Set X)] [CompleteSpace X]

include hP in
theorem packet_spaces_complete (i : ι) :
    CompleteSpace (LinearMap.range ((P.restrictTo K hK).proj i)) ∧
      CompleteSpace (LinearMap.range (P.proj i)) ∧
      CompleteSpace (LinearMap.range ((P.descendTo K hK).proj i)) := by
  letI : IsClosed (LinearMap.range ((P.restrictTo K hK).proj i) : Set K) :=
    isClosed_packet (P.restrictTo K hK) (restrictedProjector_bounded P hP K hK) i
  letI : IsClosed (LinearMap.range (P.proj i) : Set X) := isClosed_packet P hP i
  letI : IsClosed (LinearMap.range ((P.descendTo K hK).proj i) : Set (X ⧸ K)) :=
    isClosed_packet (P.descendTo K hK) (quotientProjector_bounded P hP K hK) i
  exact ⟨inferInstance, inferInstance, inferInstance⟩

include hP in
/-- The complete printed Banach packet exact sequence over an arbitrary
normed field, including a trivially valued field. -/
theorem banach_packet_shortExact (i : ι) :
    CompleteSpace (LinearMap.range ((P.restrictTo K hK).proj i)) ∧
      CompleteSpace (LinearMap.range (P.proj i)) ∧
      CompleteSpace (LinearMap.range ((P.descendTo K hK).proj i)) ∧
      IsBoundedLinearMap 𝕜 (P.packetInclusion K hK i) ∧
      IsBoundedLinearMap 𝕜 (P.packetQuotientMap K hK i) ∧
      Function.Injective (P.packetInclusion K hK i) ∧
      LinearMap.range (P.packetInclusion K hK i) = LinearMap.ker (P.packetQuotientMap K hK i) ∧
      Function.Surjective (P.packetQuotientMap K hK i) ∧
      IsBoundedLinearMap 𝕜 ((P.descendTo K hK).proj i) := by
  obtain ⟨hc1, hc2, hc3⟩ := packet_spaces_complete P hP K hK i
  obtain ⟨hinj, hexact, hsurj⟩ := P.packet_shortExact K hK i
  exact ⟨hc1, hc2, hc3, packetInclusion_bounded P K hK i, packetQuotient_bounded P K hK i,
    hinj, hexact, hsurj, quotientProjector_bounded P hP K hK i⟩

end Komorebi.PaperIRelease.GeneralPacketTopology

#print axioms Komorebi.PaperIRelease.GeneralPacketTopology.banach_packet_shortExact
#print axioms Komorebi.PaperIRelease.GeneralPacketTopology.quotient_bound_operatorNorm
