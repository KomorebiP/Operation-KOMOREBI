import KomorebiLSM.ConditionalHoeffding
import KomorebiLSM.CountableConfidence

/-! P66 without a topological assumption on the sample space. Conditional
exponentials and their filtration iteration are derived from actual bounded
adapted tests and ordinary conditional expectation. -/
set_option autoImplicit false
namespace Komorebi.LSM.PredictableResidualGeneral
open MeasureTheory ProbabilityTheory Real PredictableResidual
open scoped BigOperators NNReal ENNReal
variable {Ω : Type*} [mΩ : MeasurableSpace Ω]
variable {μ : Measure Ω} [IsProbabilityMeasure μ]

/-- A unit-range test minus its actual conditional mean lies in [-1,1]. -/
theorem increment_mem_Icc (ℱ : Filtration ℕ mΩ) (X : ℕ → Ω → ℝ)
    (hX : ∀ i,Measurable[ℱ (i+1)] (X i))
    (hb : ∀ i,∀ᵐ ω∂μ,X i ω∈Set.Icc (0:ℝ) 1) (i : ℕ) :
    ∀ᵐ ω∂μ,X i ω-(μ[X i|ℱ i]) ω∈Set.Icc (-1:ℝ) 1 := by
  have hm := conditional_mean_mem_Icc (ℱ.le i) (X i)
    ((hX i).mono (ℱ.le (i+1)) le_rfl) (hb i)
  filter_upwards [hb i,hm] with ω h h' using ⟨by linarith [h.1,h'.2],by linarith [h.2,h'.1]⟩

/-- Every finite centered sum has an actual bounded range. -/
theorem sum_mem_Icc (ℱ : Filtration ℕ mΩ) (X : ℕ → Ω → ℝ)
    (hX : ∀ i,Measurable[ℱ (i+1)] (X i))
    (hb : ∀ i,∀ᵐ ω∂μ,X i ω∈Set.Icc (0:ℝ) 1) : (n : ℕ) →
    ∀ᵐ ω∂μ,centeredSum (μ:=μ) ℱ X n ω∈Set.Icc (-(n:ℝ)) n
  | 0 => by simp [centeredSum]
  | n+1 => by
    filter_upwards [sum_mem_Icc ℱ X hX hb n,increment_mem_Icc ℱ X hX hb n] with ω hs hi
    have he : centeredSum (μ:=μ) ℱ X (n+1) ω=
        centeredSum (μ:=μ) ℱ X n ω+(X n ω-(μ[X n|ℱ n]) ω) := by
      simp only [centeredSum,Finset.sum_range_succ]
    rw [he]
    constructor <;> push_cast <;> linarith [hs.1,hs.2,hi.1,hi.2]

omit [IsProbabilityMeasure μ] in
/-- The previous centered sum is measurable before the next test. -/
theorem sum_adapted (ℱ : Filtration ℕ mΩ) (X : ℕ → Ω → ℝ)
    (hX : ∀ i,Measurable[ℱ (i+1)] (X i)) (n : ℕ) :
    Measurable[ℱ n] (centeredSum (μ:=μ) ℱ X n) := by
  apply Finset.measurable_fun_sum
  intro i hi
  have hin : i+1≤n := by simpa using Finset.mem_range.mp hi
  exact ((hX i).mono (ℱ.mono hin) le_rfl).sub
    (stronglyMeasurable_condExp.measurable.mono (ℱ.mono (by omega)) le_rfl)

theorem sum_exp_integrable (ℱ : Filtration ℕ mΩ) (X : ℕ → Ω → ℝ)
    (hX : ∀ i,Measurable[ℱ (i+1)] (X i))
    (hb : ∀ i,∀ᵐ ω∂μ,X i ω∈Set.Icc (0:ℝ) 1) (n : ℕ) (θ : ℝ) :
    Integrable (fun ω => exp (θ*centeredSum (μ:=μ) ℱ X n ω)) μ :=
  integrable_exp_mul_of_mem_Icc (centeredSum_measurable ℱ X hX n).aemeasurable
    (sum_mem_Icc ℱ X hX hb n)

/-- Direct total-expectation iteration of the true conditional exponential
bound, with no independence or conditional-distribution construction. -/
theorem sum_exp_bound (ℱ : Filtration ℕ mΩ) (X : ℕ → Ω → ℝ)
    (hX : ∀ i,Measurable[ℱ (i+1)] (X i))
    (hb : ∀ i,∀ᵐ ω∂μ,X i ω∈Set.Icc (0:ℝ) 1) (θ : ℝ) : (n : ℕ) →
    (∫ ω,exp (θ*centeredSum (μ:=μ) ℱ X n ω)∂μ)≤exp ((n:ℝ)*θ^2/8)
  | 0 => by simp [centeredSum]
  | n+1 => by
    let S : Ω → ℝ := centeredSum (μ:=μ) ℱ X n
    let Y : Ω → ℝ := fun ω => X n ω-(μ[X n|ℱ n]) ω
    have hF : StronglyMeasurable[ℱ n] (fun ω => exp (θ*S ω)) :=
      continuous_exp.comp_stronglyMeasurable
        (stronglyMeasurable_const.mul (sum_adapted ℱ X hX n).stronglyMeasurable)
    have hFbound : ∀ᵐ ω∂μ,‖exp (θ*S ω)‖≤exp (|θ| *(n:ℝ)) := by
      filter_upwards [sum_mem_Icc ℱ X hX hb n] with ω hs
      rw [Real.norm_eq_abs,abs_of_pos (exp_pos _)]
      apply exp_le_exp.mpr
      calc
        θ*S ω ≤ |θ*S ω| := le_abs_self _
        _ = |θ| * |S ω| := abs_mul _ _
        _ ≤ |θ| *(n:ℝ) := mul_le_mul_of_nonneg_left (abs_le.mpr hs) (abs_nonneg _)
    have hYint : Integrable (fun ω => exp (θ*Y ω)) μ :=
      ConditionalHoeffding.centered_exp_integrable (ℱ.le n) (X n)
        ((hX n).mono (ℱ.le (n+1)) le_rfl) (hb n) θ
    have hYmgf := ConditionalHoeffding.centered_condExp_le (ℱ.le n) (X n)
      ((hX n).mono (ℱ.le (n+1)) le_rfl) (hb n) θ
    have hpull := condExp_stronglyMeasurable_mul_of_bound (ℱ.le n) hF hYint
      (exp (|θ| *(n:ℝ))) hFbound
    have hstep : μ[(fun ω => exp (θ*S ω))*(fun ω => exp (θ*Y ω))|ℱ n]≤ᵐ[μ]
        fun ω => exp (θ*S ω)*exp (θ^2/8) := by
      filter_upwards [hpull,hYmgf] with ω hp hy
      simp only [Pi.mul_apply] at hp
      exact hp.le.trans (mul_le_mul_of_nonneg_left hy (exp_pos _).le)
    have hi := integral_mono_ae (integrable_condExp :
        Integrable (μ[(fun ω => exp (θ*S ω))*(fun ω => exp (θ*Y ω))|ℱ n]) μ)
      ((sum_exp_integrable ℱ X hX hb n θ).mul_const (exp (θ^2/8))) hstep
    rw [integral_condExp (ℱ.le n)] at hi
    have heq : (fun ω => exp (θ*centeredSum (μ:=μ) ℱ X (n+1) ω))=
        (fun ω => exp (θ*S ω))*(fun ω => exp (θ*Y ω)) := by
      funext ω
      simp only [S,Y,centeredSum,Finset.sum_range_succ,Pi.mul_apply,mul_add,exp_add]
    calc
      _ = ∫ ω,((fun ω => exp (θ*S ω))*(fun ω => exp (θ*Y ω))) ω∂μ := by rw [heq]
      _ ≤ (∫ ω,exp (θ*S ω)∂μ)*exp (θ^2/8) := by simpa only [integral_mul_const] using hi
      _ ≤ exp ((n:ℝ)*θ^2/8)*exp (θ^2/8) :=
        mul_le_mul_of_nonneg_right (sum_exp_bound ℱ X hX hb θ n) (exp_pos _).le
      _ = _ := by rw [← exp_add];congr 1;push_cast;ring

/-- The usual ordinary subgaussian MGF is derived from the direct filtration
proof and is available on every probability sample space. -/
theorem predictable_sum_subgaussian (ℱ : Filtration ℕ mΩ) (X : ℕ → Ω → ℝ)
    (hX : ∀ i,Measurable[ℱ (i+1)] (X i))
    (hb : ∀ i,∀ᵐ ω∂μ,X i ω∈Set.Icc (0:ℝ) 1) (n : ℕ) :
    HasSubgaussianMGF (centeredSum (μ:=μ) ℱ X n) ((n:NNReal)/4) μ where
  integrable_exp_mul := sum_exp_integrable ℱ X hX hb n
  mgf_le θ := by
    have he : (((n:NNReal)/4:NNReal):ℝ)*θ^2/2=(n:ℝ)*θ^2/8 := by
      push_cast
      ring
    change (∫ ω,exp (θ*centeredSum (μ:=μ) ℱ X n ω)∂μ)≤
      exp ((((n:NNReal)/4:NNReal):ℝ)*θ^2/2)
    rw [he]
    exact sum_exp_bound ℱ X hX hb θ n

/-- The sharp fixed-time two-sided bound now has no Standard Borel hypothesis. -/
theorem predictable_sum_tail (ℱ : Filtration ℕ mΩ) (X : ℕ → Ω → ℝ)
    (hX : ∀ i,Measurable[ℱ (i+1)] (X i))
    (hb : ∀ i,∀ᵐ ω∂μ,X i ω∈Set.Icc (0:ℝ) 1)
    {n : ℕ} (hn : 0<n) (b : ℝ) (hbn : 0≤b) :
    μ.real {ω | b≤|centeredSum (μ:=μ) ℱ X n ω|}≤2*exp (-2*b^2/n) := by
  have hs := predictable_sum_subgaussian ℱ X hX hb n
  have hu := hs.measure_ge_le hbn
  have hl := hs.neg.measure_ge_le hbn
  have hexp : exp (-b^2/(2*((n:NNReal)/4:NNReal)))=exp (-2*b^2/n) := by
    congr 1
    push_cast
    field_simp
    ring
  rw [hexp] at hu hl
  have hevent : {ω | b≤|centeredSum (μ:=μ) ℱ X n ω|}=
      {ω | b≤centeredSum (μ:=μ) ℱ X n ω}∪{ω | b≤ -centeredSum (μ:=μ) ℱ X n ω} := by
    ext ω
    simp only [Set.mem_ofPred_eq,Set.mem_union,le_abs]
  rw [hevent]
  exact (measureReal_union_le _ _).trans
    (by simpa only [Pi.neg_apply,two_mul] using add_le_add hu hl)

end Komorebi.LSM.PredictableResidualGeneral
