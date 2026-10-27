import KomorebiLSM.BaseNormTopology
import Mathlib.Analysis.Convex.Integral
import Mathlib.Analysis.LocallyConvex.WithSeminorms

/-! Measurability and integration of the actual positive-decomposition infimum. -/
set_option autoImplicit false
namespace Komorebi.LSM.BaseNorm.ProbabilityCone
open MeasureTheory
open scoped BigOperators NNReal
variable {E X : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E]
variable [FiniteDimensional ℝ E] (C : ProbabilityCone E)

/-- Finite coordinates bound the actual infimum by the ambient norm. -/
theorem value_le_const_mul_norm : ∃ K > 0,∀ x : E,C.value x≤K*‖x‖ := by
  let b := Module.finBasis ℝ E
  let K := ∑ i,‖(b.coord i).toContinuousLinearMap‖ * C.value (b i)
  have hK : 0≤K := Finset.sum_nonneg (fun i _ => mul_nonneg (norm_nonneg _) (C.value_nonneg _))
  refine ⟨K+1,by linarith,?_⟩
  intro x
  have hsum : C.value x≤∑ i,|(b.repr x) i| * C.value (b i) := by
    convert C.value_sum_le Finset.univ (fun i => (b.repr x) i • b i) using 1
    · rw [b.sum_repr]
    · simp only [C.value_smul]
  calc C.value x ≤ ∑ i,|(b.repr x) i| * C.value (b i) := hsum
    _ ≤ ∑ i,(‖(b.coord i).toContinuousLinearMap‖ * ‖x‖) * C.value (b i) := by
      apply Finset.sum_le_sum
      intro i _
      apply mul_le_mul_of_nonneg_right _ (C.value_nonneg _)
      exact (b.coord i).toContinuousLinearMap.le_opNorm x
    _ = K*‖x‖ := by simp only [K,Finset.sum_mul]; apply Finset.sum_congr rfl; intro i _; ring
    _ ≤ (K+1)*‖x‖ := by nlinarith [norm_nonneg x]

theorem value_continuous : Continuous C.value := by
  obtain ⟨K,hK,hbound⟩ := C.value_le_const_mul_norm
  let q : Seminorm ℝ E := K.toNNReal • normSeminorm ℝ E
  have hq : Continuous (q : E → ℝ) := by
    change Continuous (fun x : E => (K.toNNReal : ℝ)*‖x‖)
    exact continuous_const.mul continuous_norm
  change Continuous (C.seminorm : E → ℝ)
  apply Seminorm.continuous_of_le hq
  intro x
  change C.value x≤(K.toNNReal : ℝ)*‖x‖
  simpa only [Real.coe_toNNReal K hK.le] using hbound x

variable [MeasurableSpace X] {μ : Measure X}

theorem integrable_value {f : X → E} (hf : Integrable f μ) :
    Integrable (fun x => C.value (f x)) μ := by
  obtain ⟨K,_,hK⟩ := C.value_le_const_mul_norm
  apply (hf.norm.const_mul K).mono' (C.value_continuous.comp_aestronglyMeasurable hf.aestronglyMeasurable)
  filter_upwards [] with x
  rw [Real.norm_eq_abs,abs_of_nonneg (C.value_nonneg _)]
  exact hK (f x)

theorem value_integral_le_integral_value_probability [IsProbabilityMeasure μ] {f : X → E}
    (hf : Integrable f μ) : C.value (∫ x,f x∂μ)≤∫ x,C.value (f x)∂μ := by
  exact C.seminorm.convexOn.map_integral_le C.value_continuous.continuousOn isClosed_univ
    (Filter.Eventually.of_forall (fun _ => Set.mem_univ _)) hf (C.integrable_value hf)


/-- The same integral inequality holds on finite restrictions and weighted cells. -/
theorem value_integral_le_integral_value [IsFiniteMeasure μ] {f : X → E}
    (hf : Integrable f μ) : C.value (∫ x,f x∂μ)≤∫ x,C.value (f x)∂μ := by
  by_cases hμ : μ=0
  · simp [hμ]
  · have : NeZero μ := ⟨hμ⟩
    have h := C.seminorm.convexOn.map_average_le C.value_continuous.continuousOn isClosed_univ
      (Filter.Eventually.of_forall (fun _ => Set.mem_univ _)) hf (C.integrable_value hf)
    change C.value (average μ f)≤average μ (fun x => C.value (f x)) at h
    rw [average_eq,average_eq,C.value_smul,abs_of_nonneg (inv_nonneg.mpr (measureReal_nonneg)),
      smul_eq_mul] at h
    exact (mul_le_mul_iff_right₀ (inv_pos.mpr measureReal_univ_pos)).mp h

end Komorebi.LSM.BaseNorm.ProbabilityCone
