import KomorebiLSM.MeasureTVCalculus
import Mathlib.Probability.Kernel.Composition.MeasureComp

/-! Actual Markov-kernel minorization implies Dobrushin contraction. The
normalized pullback of each bounded test is derived from the measure inequality;
no contraction coefficient is supplied as a field. -/
set_option autoImplicit false
namespace Komorebi.LSM.MarkovStability
open MeasureTheory ProbabilityTheory SequentialLowerCertificate MeasureTVCalculus
open scoped ENNReal
variable {X Y : Type*} [MeasurableSpace X] [MeasurableSpace Y]

/-- Integrating a bounded test against an actual kernel-composed measure. -/
theorem integral_comp_measure (ν : Measure X) [IsProbabilityMeasure ν]
    (K : Kernel X Y) [IsMarkovKernel K] (f : Y → ℝ) (hf : Measurable f)
    (h0 : ∀ y,0≤f y) (h1 : ∀ y,f y≤1) :
    (∫ y,f y∂K ∘ₘ ν)=∫ x,∫ y,f y∂K x∂ν := by
  rw [← Measure.snd_compProd]
  change (∫ y,f y∂(ν ⊗ₘ K).map Prod.snd)=_
  rw [integral_map measurable_snd.aemeasurable hf.aestronglyMeasurable]
  exact Measure.integral_compProd (bounded_test_integrable (ν ⊗ₘ K) _
    (hf.comp measurable_snd) (fun p => h0 p.2) (fun p => h1 p.2))

/-- A probability reference occurs with at least this real mass in every row. -/
def Minorized (P : Kernel X Y) (ρ : ℝ) (reference : Measure Y) : Prop :=
  ∀ x,ENNReal.ofReal ρ • reference≤P x

/-- Minorization bounds the oscillation of the actual pulled-back test. -/
theorem pullback_interval (P : Kernel X Y) [IsMarkovKernel P]
    (reference : Measure Y) [IsProbabilityMeasure reference] (ρ : ℝ) (hρ : 0≤ρ)
    (hmin : Minorized P ρ reference) (f : Y → ℝ) (hf : Measurable f)
    (h0 : ∀ y,0≤f y) (h1 : ∀ y,f y≤1) (x : X) :
    ρ*(∫ y,f y∂reference)≤∫ y,f y∂P x ∧
      (∫ y,f y∂P x)≤ρ*(∫ y,f y∂reference)+(1-ρ) := by
  have hl : ρ*(∫ y,f y∂reference)≤∫ y,f y∂P x := by
    have h := integral_mono_measure (hmin x) (ae_of_all _ h0)
      (bounded_test_integrable (P x) f hf h0 h1)
    simpa only [integral_smul_measure,ENNReal.toReal_ofReal hρ,smul_eq_mul] using h
  have hc : ρ*(∫ y,(1-f y)∂reference)≤∫ y,(1-f y)∂P x := by
    have h := integral_mono_measure (hmin x) (ae_of_all _ (fun y => sub_nonneg.mpr (h1 y)))
      ((integrable_const (1:ℝ)).sub (bounded_test_integrable (P x) f hf h0 h1))
    simpa only [integral_smul_measure,ENNReal.toReal_ofReal hρ,smul_eq_mul] using h
  rw [integral_sub (integrable_const _) (bounded_test_integrable reference f hf h0 h1),
    integral_sub (integrable_const _) (bounded_test_integrable (P x) f hf h0 h1)] at hc
  simp only [integral_const,measureReal_def,measure_univ,ENNReal.toReal_one,one_smul] at hc
  exact ⟨hl,by linarith⟩

/-- Dobrushin contraction is derived on actual output measures from the common
minorization, including the complete-refresh endpoint rho=1. -/
theorem minorization_contraction (P : Kernel X Y) [IsMarkovKernel P]
    (reference : Measure Y) [IsProbabilityMeasure reference] (ρ : ℝ)
    (hρ0 : 0≤ρ) (hρ1 : ρ≤1) (hmin : Minorized P ρ reference)
    (ν η : Measure X) [IsProbabilityMeasure ν] [IsProbabilityMeasure η] :
    lawTV (P ∘ₘ ν) (P ∘ₘ η)≤(1-ρ)*lawTV ν η := by
  apply lawTV_le_of_bounded_tests
  intro f hf h0 h1
  rw [integral_comp_measure ν P f hf h0 h1,integral_comp_measure η P f hf h0 h1]
  let F : X → ℝ := fun x => ∫ y,f y∂P x
  let c : ℝ := ρ*(∫ y,f y∂reference)
  have hm : Measurable F := hf.stronglyMeasurable.integral_kernel.measurable
  have hb (x : X) : c≤F x ∧ F x≤c+(1-ρ) := pullback_interval P reference ρ hρ0 hmin f hf h0 h1 x
  by_cases hz : ρ=1
  · have he (x : X) : F x=c := by have h:=hb x; simp only [hz,sub_self,add_zero] at h; exact le_antisymm h.2 h.1
    change |(∫ x,F x∂ν)-(∫ x,F x∂η)|≤(1-ρ)*lawTV ν η
    simp only [he,integral_const,measureReal_def,measure_univ,ENNReal.toReal_one,one_smul,sub_self,abs_zero,hz,zero_mul,le_refl]
  · have hp : 0<1-ρ := sub_pos.mpr (lt_of_le_of_ne hρ1 hz)
    let g : X → ℝ := fun x => (F x-c)/(1-ρ)
    have hgm : Measurable g := (hm.sub measurable_const).div_const _
    have hg0 (x : X) : 0≤g x := div_nonneg (sub_nonneg.mpr (hb x).1) hp.le
    have hg1 (x : X) : g x≤1 := (div_le_one hp).mpr (by linarith [(hb x).2])
    have hge (x : X) : F x=c+(1-ρ)*g x := by dsimp [g]; field_simp; ring
    have hi (ξ : Measure X) [IsProbabilityMeasure ξ] :
        (∫ x,F x∂ξ)=c+(1-ρ)*(∫ x,g x∂ξ) := by
      calc (∫ x,F x∂ξ)=∫ x,c+(1-ρ)*g x∂ξ := integral_congr_ae (ae_of_all _ hge)
        _ = _ := by
          rw [integral_add (integrable_const _) ((bounded_test_integrable ξ g hgm hg0 hg1).const_mul _),
            integral_const_mul (1-ρ) g]
          simp only [integral_const,measureReal_def,measure_univ,ENNReal.toReal_one,one_smul]
    change |(∫ x,F x∂ν)-(∫ x,F x∂η)|≤(1-ρ)*lawTV ν η
    rw [hi ν,hi η]
    calc |c+(1-ρ)*(∫ x,g x∂ν)-(c+(1-ρ)*(∫ x,g x∂η))|=
        (1-ρ)*|(∫ x,g x∂ν)-(∫ x,g x∂η)| := by
          rw [show c+(1-ρ)*(∫ x,g x∂ν)-(c+(1-ρ)*(∫ x,g x∂η))=
            (1-ρ)*((∫ x,g x∂ν)-(∫ x,g x∂η)) by ring,abs_mul,abs_of_pos hp]
      _ ≤ (1-ρ)*lawTV ν η := mul_le_mul_of_nonneg_left
        (bounded_test_integral_le_tv ν η g hgm hg0 hg1) hp.le

/-- A uniform actual conditional-TV budget controls changing one kernel under
an actual common prefix. Conditional-TV measurability is not needed for this
constant budget on arbitrary measurable spaces. -/
theorem compProd_uniform_change (ν : Measure X) [IsProbabilityMeasure ν]
    (K L : Kernel X Y) [IsMarkovKernel K] [IsMarkovKernel L] (Δ : ℝ)
    (hΔ : ∀ x,lawTV (K x) (L x)≤Δ) : lawTV (ν ⊗ₘ K) (ν ⊗ₘ L)≤Δ := by
  apply lawTV_le_of_bounded_tests
  intro f hf h0 h1
  have hfi (J : Kernel X Y) [IsMarkovKernel J] (x : X) : Integrable (fun y => f (x,y)) (J x) :=
    bounded_test_integrable (J x) _ (hf.comp (measurable_const.prodMk measurable_id))
      (fun y => h0 (x,y)) (fun y => h1 (x,y))
  have hFm (J : Kernel X Y) [IsMarkovKernel J] : Measurable (fun x => ∫ y,f (x,y)∂J x) :=
    hf.stronglyMeasurable.integral_kernel_prod_right'.measurable
  have hF0 (J : Kernel X Y) [IsMarkovKernel J] (x : X) : 0≤∫ y,f (x,y)∂J x :=
    integral_nonneg (fun y => h0 (x,y))
  have hF1 (J : Kernel X Y) [IsMarkovKernel J] (x : X) : (∫ y,f (x,y)∂J x)≤1 := by
    calc (∫ y,f (x,y)∂J x)≤∫ _ : Y,(1:ℝ)∂J x :=
        integral_mono (hfi J x) (integrable_const _) (fun y => h1 (x,y))
      _ = 1 := by simp
  have hFk := bounded_test_integrable ν _ (hFm K) (hF0 K) (hF1 K)
  have hFl := bounded_test_integrable ν _ (hFm L) (hF0 L) (hF1 L)
  have hd : Integrable (fun x => (∫ y,f (x,y)∂K x)-(∫ y,f (x,y)∂L x)) ν :=
    (hFk.sub hFl).congr (by filter_upwards with x; rfl)
  rw [Measure.integral_compProd (bounded_test_integrable (ν ⊗ₘ K) f hf h0 h1),
    Measure.integral_compProd (bounded_test_integrable (ν ⊗ₘ L) f hf h0 h1),← integral_sub hFk hFl]
  calc |∫ x,(∫ y,f (x,y)∂K x)-(∫ y,f (x,y)∂L x)∂ν|≤
      ∫ x,|(∫ y,f (x,y)∂K x)-(∫ y,f (x,y)∂L x)|∂ν := abs_integral_le_integral_abs
    _ ≤ ∫ _ : X,Δ∂ν := by
      apply integral_mono hd.abs (integrable_const _)
      intro x
      exact (bounded_test_integral_le_tv (K x) (L x) _
        (hf.comp (measurable_const.prodMk measurable_id))
        (fun y => h0 (x,y)) (fun y => h1 (x,y))).trans (hΔ x)
    _ = Δ := by simp

/-- The one-step output-marginal budget follows by actual projection of the
joint composition-product laws. -/
theorem comp_measure_uniform_change (ν : Measure X) [IsProbabilityMeasure ν]
    (K L : Kernel X Y) [IsMarkovKernel K] [IsMarkovKernel L] (Δ : ℝ)
    (hΔ : ∀ x,lawTV (K x) (L x)≤Δ) : lawTV (K ∘ₘ ν) (L ∘ₘ ν)≤Δ := by
  have h := (lawTV_map (ν ⊗ₘ K) (ν ⊗ₘ L) Prod.snd measurable_snd).trans
    (compProd_uniform_change ν K L Δ hΔ)
  change lawTV (ν ⊗ₘ K).snd (ν ⊗ₘ L).snd≤Δ at h
  simpa only [Measure.snd_compProd] using h

end Komorebi.LSM.MarkovStability
