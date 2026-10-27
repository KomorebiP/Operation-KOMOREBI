import KomorebiLSM.SequentialLowerCertificate
import Mathlib.Probability.Kernel.Composition.IntegralCompProd
import Mathlib.Probability.Kernel.MeasurableIntegral

/-! Actual probability-law total variation: event attainment, test duality,
triangle inequality, and contraction under measurable reporting or continuation.
-/
set_option autoImplicit false
namespace Komorebi.LSM.MeasureTVCalculus
noncomputable section
open MeasureTheory Set ProbabilityTheory
open scoped ENNReal
open SequentialLowerCertificate

variable {X Y : Type*} [MeasurableSpace X] [MeasurableSpace Y]

/-- A measurable event attains the probability convention of total variation. -/
theorem lawTV_event_attained (P Q : Measure X)
    [IsProbabilityMeasure P] [IsProbabilityMeasure Q] :
    ∃ s : Set X, MeasurableSet s ∧ P.real s-Q.real s=lawTV P Q := by
  let v : SignedMeasure X := P.toSignedMeasure-Q.toSignedMeasure
  let j := v.toJordanDecomposition
  obtain ⟨s, hs, hp, hn⟩ := j.mutuallySingular
  have hpu : j.posPart.real sᶜ = j.posPart.real univ := by
    have h : j.posPart sᶜ = j.posPart univ := by
      simpa only [hp, zero_add] using (measure_add_measure_compl hs (μ := j.posPart))
    exact congrArg ENNReal.toReal h
  have hv0 : v univ=0 := by simp [v]
  have hj0 : j.posPart.real univ=j.negPart.real univ := by
    have h := v.apply_eq_posPart_real_sub_negPart_real MeasurableSet.univ
    change v univ=j.posPart.real univ-j.negPart.real univ at h
    linarith
  have hvs : v sᶜ=j.posPart.real univ := by
    rw [v.apply_eq_posPart_real_sub_negPart_real hs.compl]
    change j.posPart.real sᶜ-j.negPart.real sᶜ= _
    rw [hpu]
    simp only [Measure.real, hn, ENNReal.toReal_zero, sub_zero]
  refine ⟨sᶜ, hs.compl, ?_⟩
  have hid : v sᶜ=P.real sᶜ-Q.real sᶜ := by
    simp [v, hs.compl]
  have htv : lawTV P Q=j.posPart.real univ := by
    change (1/2:ℝ)*v.totalVariation.real univ= _
    rw [SignedMeasure.totalVariation, measureReal_add_apply]
    change (1/2:ℝ)*(j.posPart.real univ+j.negPart.real univ)= _
    rw [← hj0]
    ring
  linarith

/-- Bounds on every actual measurable [0,1] test imply a total variation bound. -/
theorem lawTV_le_of_bounded_tests (P Q : Measure X)
    [IsProbabilityMeasure P] [IsProbabilityMeasure Q] (e : ℝ)
    (h : ∀ (f : X → ℝ), Measurable f → (∀ x, 0 ≤ f x) → (∀ x, f x ≤ 1) →
      |(∫ x, f x ∂P)-(∫ x, f x ∂Q)| ≤ e) : lawTV P Q ≤ e := by
  obtain ⟨s, hs, he⟩ := lawTV_event_attained P Q
  let f : X → ℝ := s.indicator (fun _ => 1)
  have hf : Measurable f := measurable_const.indicator hs
  have hf0 : ∀ x, 0 ≤ f x := fun x => by by_cases hx : x∈s <;> simp [f,hx]
  have hf1 : ∀ x, f x ≤ 1 := fun x => by by_cases hx : x∈s <;> simp [f,hx]
  have hb := h f hf hf0 hf1
  have hi (μ : Measure X) : (∫ x, f x ∂μ)=μ.real s := by
    simp [f, integral_indicator hs]
  rw [hi P,hi Q,he,abs_of_nonneg (lawTV_nonneg P Q)] at hb
  exact hb

theorem lawTV_symm (P Q : Measure X)
    [IsProbabilityMeasure P] [IsProbabilityMeasure Q] : lawTV P Q=lawTV Q P := by
  unfold lawTV
  rw [← SignedMeasure.totalVariation_neg, neg_sub]

theorem lawTV_triangle (P Q R : Measure X)
    [IsProbabilityMeasure P] [IsProbabilityMeasure Q] [IsProbabilityMeasure R] :
    lawTV P R ≤ lawTV P Q+lawTV Q R := by
  apply lawTV_le_of_bounded_tests
  intro f hf h0 h1
  have hp := bounded_test_integral_le_tv P Q f hf h0 h1
  have hq := bounded_test_integral_le_tv Q R f hf h0 h1
  exact (abs_sub_le (∫ x, f x ∂P) (∫ x, f x ∂Q) (∫ x, f x ∂R)).trans (add_le_add hp hq)

/-- Common measurable reporting cannot increase actual total variation. -/
theorem lawTV_map (P Q : Measure X)
    [IsProbabilityMeasure P] [IsProbabilityMeasure Q]
    (f : X → Y) (hf : Measurable f) :
    lawTV (P.map f) (Q.map f) ≤ lawTV P Q := by
  apply lawTV_le_of_bounded_tests
  intro g hg h0 h1
  rw [integral_map hf.aemeasurable hg.aestronglyMeasurable,
    integral_map hf.aemeasurable hg.aestronglyMeasurable]
  exact bounded_test_integral_le_tv P Q (fun x => g (f x)) (hg.comp hf)
    (fun x => h0 (f x)) (fun x => h1 (f x))

/-- A common Markov continuation, retaining the starting history, is contractive. -/
theorem lawTV_compProd (P Q : Measure X)
    [IsProbabilityMeasure P] [IsProbabilityMeasure Q]
    (κ : Kernel X Y) [IsMarkovKernel κ] :
    lawTV (P ⊗ₘ κ) (Q ⊗ₘ κ) ≤ lawTV P Q := by
  apply lawTV_le_of_bounded_tests
  intro f hf h0 h1
  have hfi (x : X) : Integrable (fun y => f (x,y)) (κ x) :=
    bounded_test_integrable (κ x) (fun y => f (x,y))
      (hf.comp (measurable_const.prodMk measurable_id))
      (fun y => h0 (x,y)) (fun y => h1 (x,y))
  have hF : Measurable (fun x => ∫ y, f (x,y) ∂κ x) :=
    hf.stronglyMeasurable.integral_kernel_prod_right'.measurable
  have hF0 (x : X) : 0 ≤ ∫ y, f (x,y) ∂κ x :=
    integral_nonneg fun y => h0 (x,y)
  have hF1 (x : X) : (∫ y, f (x,y) ∂κ x) ≤ 1 := by
    calc
      _ ≤ ∫ _ : Y, (1:ℝ) ∂κ x := integral_mono (hfi x) (integrable_const _) (fun y => h1 (x,y))
      _ = 1 := by simp
  rw [Measure.integral_compProd (bounded_test_integrable (P ⊗ₘ κ) f hf h0 h1),
    Measure.integral_compProd (bounded_test_integrable (Q ⊗ₘ κ) f hf h0 h1)]
  exact bounded_test_integral_le_tv P Q _ hF hF0 hF1

end
end Komorebi.LSM.MeasureTVCalculus
