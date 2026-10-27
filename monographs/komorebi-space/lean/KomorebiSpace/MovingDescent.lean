import KomorebiSpace.MovingKernelBounds
import KomorebiSpace.DescentClosedRange

set_option autoImplicit false

/-!
# Perturbing the actual quantitative-descent projector

The raw local candidate space and its Hilbert norm are fixed. Both the local
and overlap operators may change. Each system must carry its own local and
restricted-matching stability evidence. The new theorem compares the actual
v0.30 two-stage repairs, not newly substituted projection definitions.
-/
universe u v w
noncomputable section
namespace KomorebiSpace
namespace MovingDescent
open HilbertKernelProjection QuantitativeDescent
variable {E : Type u} {R : Type v} {Y : Type w}
variable [NormedAddCommGroup E] [InnerProductSpace ℝ E] [CompleteSpace E]
variable [NormedAddCommGroup R] [NormedSpace ℝ R] [CompleteSpace R]
variable [NormedAddCommGroup Y] [NormedSpace ℝ Y] [CompleteSpace Y]
variable (D : E →L[ℝ] R) (C : E →L[ℝ] Y)

/-- The old two-stage theorem supplies a bound on its unchanged joint residual. -/
def bound (hD : IsClosed (Set.range D)) (hB : IsClosed (Set.range (matching D C))) :
    ResidualRobustness.Bound (joint D C) where
  constant := stabilityGain D C hD hB
  nonneg := stabilityGain_nonneg D C hD hB
  estimate x := by
    rw [← repair_eq_projection]
    exact stable_repair D C hD hB x

omit [CompleteSpace E] [CompleteSpace R] [CompleteSpace Y] in
/-- The product residual uses max: local and overlap uncertainties are not added. -/
theorem joint_operator_error (D' : E →L[ℝ] R) (C' : E →L[ℝ] Y)
    {εD εC : ℝ} (hD : ‖D-D'‖ ≤ εD) (hC : ‖C-C'‖ ≤ εC) :
    ‖joint D C-joint D' C'‖ ≤ max εD εC := by
  have hεD : 0 ≤ εD := (norm_nonneg _).trans hD
  have hεC : 0 ≤ εC := (norm_nonneg _).trans hC
  apply ContinuousLinearMap.opNorm_le_bound _ (hεD.trans (le_max_left _ _))
  intro x
  change ‖(D x-D' x,C x-C' x)‖ ≤ _
  rw [Prod.norm_def]
  apply max_le
  · exact ((D-D').le_opNorm x).trans
      (mul_le_mul_of_nonneg_right (hD.trans (le_max_left _ _)) (norm_nonneg x))
  · exact ((C-C').le_opNorm x).trans
      (mul_le_mul_of_nonneg_right (hC.trans (le_max_right _ _)) (norm_nonneg x))

/-- Motion of the actual global two-stage repairs. -/
theorem repair_motion (D' : E →L[ℝ] R) (C' : E →L[ℝ] Y)
    (hD : IsClosed (Set.range D)) (hB : IsClosed (Set.range (matching D C)))
    (hD' : IsClosed (Set.range D')) (hB' : IsClosed (Set.range (matching D' C')))
    {εD εC : ℝ} (heD : ‖D-D'‖ ≤ εD) (heC : ‖C-C'‖ ≤ εC) :
    ‖repair D C-repair D' C'‖ ≤
      max (stabilityGain D C hD hB) (stabilityGain D' C' hD' hB') * max εD εC := by
  have hid : repair D C=projection (joint D C) := by ext x; exact repair_eq_projection D C x
  have hid' : repair D' C'=projection (joint D' C') := by ext x; exact repair_eq_projection D' C' x
  rw [hid,hid']
  exact MovingKernel.projection_opNorm _ _ (bound D C hD hB) (bound D' C' hD' hB')
    (joint_operator_error D C D' C' heD heC)

/-- Simultaneous change of local observations and reference model. -/
theorem repaired_data_motion (D' : E →L[ℝ] R) (C' : E →L[ℝ] Y)
    (hD : IsClosed (Set.range D)) (hB : IsClosed (Set.range (matching D C)))
    (hD' : IsClosed (Set.range D')) (hB' : IsClosed (Set.range (matching D' C')))
    {εD εC : ℝ} (heD : ‖D-D'‖ ≤ εD) (heC : ‖C-C'‖ ≤ εC) (x y : E) :
    ‖repair D C x-repair D' C' y‖ ≤ ‖x-y‖ +
      (max (stabilityGain D C hD hB) (stabilityGain D' C' hD' hB') * max εD εC)*‖y‖ := by
  rw [repair_eq_projection,repair_eq_projection]
  exact MovingKernel.repaired_input_motion _ _ (bound D C hD hB) (bound D' C' hD' hB')
    (joint_operator_error D C D' C' heD heC) x y

end MovingDescent
end KomorebiSpace
end
