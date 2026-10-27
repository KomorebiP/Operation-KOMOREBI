import KomorebiLSM.ContinuousTV
import Mathlib.Probability.ConditionalProbability

/-! Eventwise comparison of the actual conditional probability measures.
Conditioning is used only when the common event has positive mass under both laws. -/
set_option autoImplicit false
namespace Komorebi.LSM.ConditionalEventTV
open MeasureTheory ProbabilityTheory
open scoped ENNReal ProbabilityTheory
variable {Ω : Type*} [MeasurableSpace Ω]

theorem event_error_le_tv (P Q : Measure Ω) [IsProbabilityMeasure P] [IsProbabilityMeasure Q]
    (S : Set Ω) (hS : MeasurableSet S) :
    |P.real S-Q.real S|≤SequentialLowerCertificate.lawTV P Q := by
  let φ : Ω → ℝ := S.indicator (fun _ => 1)
  have hm : Measurable φ := measurable_const.indicator hS
  have h0 : ∀ x,0≤φ x := by intro x; by_cases hx : x∈S <;> simp [φ,hx]
  have h1 : ∀ x,φ x≤1 := by intro x; by_cases hx : x∈S <;> simp [φ,hx]
  have h := SequentialLowerCertificate.bounded_test_integral_le_tv P Q φ hm h0 h1
  simpa [φ,integral_indicator hS,Measure.real] using h

theorem conditional_real (P : Measure Ω) (S T : Set Ω) (hS : MeasurableSet S) :
    (ProbabilityTheory.cond P S).real T=P.real (S∩T)/P.real S := by
  rw [Measure.real,ProbabilityTheory.cond_apply hS,ENNReal.toReal_mul,ENNReal.toReal_inv]
  simp only [Measure.real,div_eq_mul_inv,mul_comm]

/-- Scalar normalization uses both positive denominators and the actual event mass bound. -/
theorem ratio_error {a b p q δ : ℝ} (hp : 0<p) (hq : 0<q) (hb0 : 0≤b) (hb : b≤q)
    (hδ : 0≤δ) (hab : |a-b|≤δ) (hpq : |p-q|≤δ) :
    |a/p-b/q|≤2*δ/p := by
  have hbq0 : 0≤b/q := div_nonneg hb0 hq.le
  have hbq1 : b/q≤1 := (div_le_one hq).mpr hb
  have he : a/p-b/q=(a-b)/p+(b/q)*((q-p)/p) := by field_simp; ring
  rw [he]
  calc |(a-b)/p+(b/q)*((q-p)/p)|≤|(a-b)/p|+|(b/q)*((q-p)/p)| := abs_add_le _ _
    _ = |a-b|/p+(b/q)*(|p-q|/p) := by
      rw [abs_mul,abs_div,abs_of_pos hp,abs_of_nonneg hbq0,abs_div,abs_of_pos hp,abs_sub_comm q p]
    _ ≤ δ/p+(b/q)*(δ/p) := add_le_add (div_le_div_of_nonneg_right hab hp.le)
      (mul_le_mul_of_nonneg_left (div_le_div_of_nonneg_right hpq hp.le) hbq0)
    _ ≤ δ/p+δ/p := add_le_add le_rfl (by
      simpa using mul_le_mul_of_nonneg_right hbq1 (div_nonneg hδ hp.le))
    _ = 2*δ/p := by ring

/-- The bound concerns literal normalized restrictions, with both event masses
strictly positive. It controls every measurable event under those measures. -/
theorem conditional_event_error (P Q : Measure Ω) [IsProbabilityMeasure P] [IsProbabilityMeasure Q]
    (S T : Set Ω) (hS : MeasurableSet S) (hT : MeasurableSet T)
    (hp : 0<P.real S) (hq : 0<Q.real S) :
    |(ProbabilityTheory.cond P S).real T-(ProbabilityTheory.cond Q S).real T|≤
      min 1 (2*SequentialLowerCertificate.lawTV P Q/min (P.real S) (Q.real S)) := by
  have hPnz : P S≠0 := by intro h; simp [Measure.real,h] at hp
  have hQnz : Q S≠0 := by intro h; simp [Measure.real,h] at hq
  have : IsProbabilityMeasure (ProbabilityTheory.cond P S) := ProbabilityTheory.cond_isProbabilityMeasure hPnz
  have : IsProbabilityMeasure (ProbabilityTheory.cond Q S) := ProbabilityTheory.cond_isProbabilityMeasure hQnz
  have h0P : 0≤(ProbabilityTheory.cond P S).real T := measureReal_nonneg
  have h0Q : 0≤(ProbabilityTheory.cond Q S).real T := measureReal_nonneg
  have h1P : (ProbabilityTheory.cond P S).real T≤1 := measureReal_le_one
  have h1Q : (ProbabilityTheory.cond Q S).real T≤1 := measureReal_le_one
  apply le_min
  · exact abs_sub_le_iff.mpr ⟨by linarith,by linarith⟩
  · rw [conditional_real P S T hS,conditional_real Q S T hS]
    have hδ := SequentialLowerCertificate.lawTV_nonneg P Q
    apply (ratio_error hp hq measureReal_nonneg
      (measureReal_mono (Set.inter_subset_left : S∩T⊆S)) hδ
      (event_error_le_tv P Q (S∩T) (hS.inter hT)) (event_error_le_tv P Q S hS)).trans
    apply (div_le_div_iff₀ hp (lt_min hp hq)).mpr
    exact mul_le_mul_of_nonneg_left (min_le_left _ _) (mul_nonneg (by norm_num) hδ)


section Records
open ContinuousRecords
variable {E A Y : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E]
variable [FiniteDimensional ℝ E] [MeasurableSpace E] [BorelSpace E]
variable [MeasurableSpace A] [MeasurableSpace Y] [Fintype A] [MeasurableSingletonClass A]
variable {C : BaseNorm.ProbabilityCone E} {μ : Measure Y} [IsProbabilityMeasure μ]

/-- The full-law budget controls every event of the actual conditional record
measures whenever the conditioning event has positive probability under both laws. -/
theorem record_conditional_event_error
    (Ds Fs : ℕ → ContinuousInstrument.DensityInstrument (A := A) C μ)
    (π : Policy (A := A) (Y := Y)) (u v : ContinuousInstrument.DensityInstrument.State C)
    (ε : ℕ → ℝ) (hε0 : ∀ n,0≤ε n)
    (hε : ∀ n a z,z∈C.base → (∫ y,C.value ((Ds n).op a y z-(Fs n).op a y z)∂μ)≤ε n)
    (e0 : ℝ) (he0 : C.value (u.1-v.1)≤e0) (n : ℕ)
    (S T : Set (History (A × Y) n)) (hS : MeasurableSet S) (hT : MeasurableSet T)
    (hp : 0<(TimeRecords.recordLaw Ds π u.1 n).real S)
    (hq : 0<(TimeRecords.recordLaw Fs π v.1 n).real S) :
    |(ProbabilityTheory.cond (TimeRecords.recordLaw Ds π u.1 n) S).real T-
      (ProbabilityTheory.cond (TimeRecords.recordLaw Fs π v.1 n) S).real T|≤
      min 1 ((e0+∑ i∈Finset.range n,ε i)/
        min ((TimeRecords.recordLaw Ds π u.1 n).real S) ((TimeRecords.recordLaw Fs π v.1 n).real S)) := by
  have h := conditional_event_error (TimeRecords.recordLaw Ds π u.1 n)
    (TimeRecords.recordLaw Fs π v.1 n) S T hS hT hp hq
  apply h.trans
  apply min_le_min le_rfl
  apply div_le_div_of_nonneg_right _ (lt_min hp hq).le
  have hTV := (ContinuousTV.record_lawTV_le Ds Fs π u v ε hε0 hε e0 he0 n).trans
    (min_le_right _ _)
  linarith

end Records
end Komorebi.LSM.ConditionalEventTV
