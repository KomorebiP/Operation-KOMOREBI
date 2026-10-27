import KomorebiVerification.TopologicalCompletion
import Mathlib.Analysis.Normed.Operator.NormedSpace

/-!
# Conditioned packet coordinates

This constructs the condition-number definition and proves the two-sided
operator norm comparison.  The general statement applies to any chosen
bounded coordinate isomorphism, so it is not restricted to a particular
finite product norm.  Only the lower bound by one requires a nonzero space.
-/

set_option autoImplicit false
noncomputable section

namespace Komorebi.PaperICompletion.ConditionedCoordinates

universe u v w
variable {𝕜 : Type u} [NontriviallyNormedField 𝕜]
variable {X : Type v} [NormedAddCommGroup X] [NormedSpace 𝕜 X]
variable {Y : Type w} [NormedAddCommGroup Y] [NormedSpace 𝕜 Y]

/-- Product of the genuine operator norms of a coordinate map and its inverse. -/
def conditionNumber (e : X ≃L[𝕜] Y) : ℝ :=
  ‖e.toContinuousLinearMap‖ * ‖e.symm.toContinuousLinearMap‖

theorem conditionNumber_nonneg (e : X ≃L[𝕜] Y) : 0 ≤ conditionNumber e :=
  mul_nonneg (norm_nonneg _) (norm_nonneg _)

theorem conditionNumber_symm (e : X ≃L[𝕜] Y) :
    conditionNumber e.symm = conditionNumber e := by
  simp only [conditionNumber, ContinuousLinearEquiv.symm_symm, mul_comm]

/-- A coordinate condition number is at least one on a nonzero space. -/
theorem one_le_conditionNumber [Nontrivial X] (e : X ≃L[𝕜] Y) :
    1 ≤ conditionNumber e := e.one_le_norm_mul_norm_symm

/-- Bounded coordinate conjugation of the actual operator. -/
def coordinateOperator (e : X ≃L[𝕜] Y) (T : X →L[𝕜] X) : Y →L[𝕜] Y :=
  e.toContinuousLinearMap.comp (T.comp e.symm.toContinuousLinearMap)

theorem coordinateOperator_inverse (e : X ≃L[𝕜] Y) (T : X →L[𝕜] X) :
    coordinateOperator e.symm (coordinateOperator e T) = T := by
  ext x
  simp [coordinateOperator]

/-- Forward condition-number bound. -/
theorem norm_coordinateOperator_le (e : X ≃L[𝕜] Y) (T : X →L[𝕜] X) :
    ‖coordinateOperator e T‖ ≤ conditionNumber e * ‖T‖ := by
  calc
    ‖coordinateOperator e T‖ ≤ ‖e.toContinuousLinearMap‖ *
        ‖T.comp e.symm.toContinuousLinearMap‖ :=
      ContinuousLinearMap.opNorm_comp_le _ _
    _ ≤ ‖e.toContinuousLinearMap‖ * (‖T‖ * ‖e.symm.toContinuousLinearMap‖) :=
      mul_le_mul_of_nonneg_left (ContinuousLinearMap.opNorm_comp_le _ _) (norm_nonneg _)
    _ = conditionNumber e * ‖T‖ := by unfold conditionNumber; ring

/-- Reverse condition-number bound. -/
theorem norm_le_conditionNumber_mul_coordinateOperator
    (e : X ≃L[𝕜] Y) (T : X →L[𝕜] X) :
    ‖T‖ ≤ conditionNumber e * ‖coordinateOperator e T‖ := by
  simpa only [coordinateOperator_inverse, conditionNumber_symm] using
    norm_coordinateOperator_le e.symm (coordinateOperator e T)

/-- On the zero space the condition number is zero, not at least one. -/
theorem conditionNumber_eq_zero_of_subsingleton [Subsingleton X]
    (e : X ≃L[𝕜] Y) : conditionNumber e = 0 := by
  have he : e.toContinuousLinearMap = 0 := by
    ext x
    rw [Subsingleton.elim x 0, map_zero]
    rfl
  simp [conditionNumber, he]

section Packets
open KomorebiVerification.TopologicalCompletion
variable {ι : Type*} [Fintype ι]

/-- Packet-coordinate condition number in the canonical product norm. -/
def packetConditionNumber (P : BoundedProjectorFamily 𝕜 X ι) : ℝ :=
  conditionNumber P.packetEquiv

theorem packetConditionNumber_eq (P : BoundedProjectorFamily 𝕜 X ι) :
    packetConditionNumber P = ‖P.analysis‖ * ‖P.synthesis‖ := rfl

/-- Both bounds of the publication proposition, with literal packet analysis and synthesis. -/
theorem packet_conditioned_coordinate_bounds
    (P : BoundedProjectorFamily 𝕜 X ι) (T : X →L[𝕜] X) :
    ‖P.analysis.comp (T.comp P.synthesis)‖ ≤ packetConditionNumber P * ‖T‖ ∧
      ‖T‖ ≤ packetConditionNumber P * ‖P.analysis.comp (T.comp P.synthesis)‖ :=
  ⟨norm_coordinateOperator_le P.packetEquiv T,
    norm_le_conditionNumber_mul_coordinateOperator P.packetEquiv T⟩

end Packets
end Komorebi.PaperICompletion.ConditionedCoordinates
