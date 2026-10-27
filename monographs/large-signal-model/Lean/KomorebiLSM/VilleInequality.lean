import Mathlib.Probability.Martingale.OptionalStopping
import Mathlib.MeasureTheory.Measure.Continuity

/-! The actual crossing event of a nonnegative supermartingale. Finite stopped
expectations are controlled before passing to every natural-number time. -/
set_option autoImplicit false
namespace Komorebi.LSM.VilleInequality
open MeasureTheory ProbabilityTheory Set
open scoped ENNReal
variable {Ω : Type*} [MeasurableSpace Ω] (μ : Measure Ω) [IsProbabilityMeasure μ]
variable (F : Filtration ℕ ‹MeasurableSpace Ω›) (M : ℕ → Ω → ℝ)

def crossingUpTo (c : ℝ) (N : ℕ) : Set Ω := {ω | ∃ n≤N,c≤M n ω}
def crossing (c : ℝ) : Set Ω := {ω | ∃ n,c≤M n ω}

omit [IsProbabilityMeasure μ] in
theorem crossingUpTo_measurable (hM : Supermartingale M F μ) (c : ℝ) (N : ℕ) :
    MeasurableSet (crossingUpTo M c N) := by
  have he : crossingUpTo M c N=⋃ n : ℕ,⋃ _h : n≤N,{ω | c≤M n ω} := by
    ext ω
    simp only [crossingUpTo,mem_ofPred_eq,mem_iUnion,exists_prop]
  rw [he]
  exact MeasurableSet.iUnion fun n => MeasurableSet.iUnion fun _ =>
    measurableSet_le measurable_const ((hM.stronglyMeasurable n).measurable.le (F.le n))

omit [IsProbabilityMeasure μ] in
theorem crossing_measurable (hM : Supermartingale M F μ) (c : ℝ) :
    MeasurableSet (crossing M c) := by
  have he : crossing M c=⋃ n : ℕ,{ω | c≤M n ω} := by ext ω; simp [crossing]
  rw [he]
  exact MeasurableSet.iUnion fun n =>
    measurableSet_le measurable_const ((hM.stronglyMeasurable n).measurable.le (F.le n))

/-- Bounded hitting and optional stopping give the finite crossing bound. -/
theorem finite_crossing_bound (hM : Supermartingale M F μ)
    (h0 : ∀ n ω,0≤M n ω) (hinitial : (∫ ω,M 0 ω ∂μ)≤1)
    (c : ℝ) (hc : 0<c) (N : ℕ) : μ (crossingUpTo M c N)≤ENNReal.ofReal (1/c) := by
  let τ : Ω → WithTop ℕ := fun ω => (hittingBtwn M (Ici c) 0 N ω : ℕ)
  have hτ : IsStoppingTime F τ :=
    hM.stronglyAdapted.adapted.isStoppingTime_hittingBtwn measurableSet_Ici
  have hb : ∀ ω,τ ω≤N := fun ω => by
    change ((hittingBtwn M (Ici c) 0 N ω : ℕ) : WithTop ℕ)≤(N : WithTop ℕ)
    exact_mod_cast hittingBtwn_le (u := M) (s := Ici c) (n := 0) (m := N) ω
  have hint : Integrable (stoppedValue M τ) μ := integrable_stoppedValue ℕ hτ hM.integrable hb
  have hstop : (∫ ω,stoppedValue M τ ω ∂μ)≤∫ ω,M 0 ω ∂μ := by
    have he := hM.neg.expected_stoppedValue_mono (isStoppingTime_const F 0) hτ
      (fun ω => by change (0 : WithTop ℕ)≤τ ω; exact bot_le) hb
    change (∫ ω,-M 0 ω ∂μ)≤∫ ω,-stoppedValue M τ ω ∂μ at he
    rw [integral_neg,integral_neg,neg_le_neg_iff] at he
    exact he
  have hhit (ω : Ω) (hω : ω∈crossingUpTo M c N) : c≤stoppedValue M τ ω := by
    apply stoppedValue_hittingBtwn_mem
    obtain ⟨n,hn,hval⟩ := hω
    exact ⟨n,⟨Nat.zero_le _,hn⟩,hval⟩
  have hs := crossingUpTo_measurable μ F M hM c N
  have hl := setIntegral_ge_of_const_le_real hs (measure_ne_top μ _) hhit hint.integrableOn
  have hn : 0≤ᵐ[μ] stoppedValue M τ := ae_of_all _ fun ω => h0 _ _
  have hu := (setIntegral_le_integral hint hn (s := crossingUpTo M c N)).trans (hstop.trans hinitial)
  have hr : μ.real (crossingUpTo M c N)≤1/c := (le_div_iff₀ hc).mpr (by nlinarith)
  simpa only [Measure.real,ENNReal.ofReal_toReal (measure_ne_top μ _)] using ENNReal.ofReal_le_ofReal hr

/-- Ville's inequality for the literal event of ever crossing the threshold. -/
theorem crossing_bound (hM : Supermartingale M F μ)
    (h0 : ∀ n ω,0≤M n ω) (hinitial : (∫ ω,M 0 ω ∂μ)≤1)
    (c : ℝ) (hc : 0<c) : μ (crossing M c)≤ENNReal.ofReal (1/c) := by
  have hmono : Monotone (crossingUpTo M c) := by
    intro n k hnk ω hω
    obtain ⟨i,hi,hval⟩ := hω
    exact ⟨i,hi.trans hnk,hval⟩
  have he : crossing M c=⋃ N : ℕ,crossingUpTo M c N := by
    ext ω
    constructor
    · rintro ⟨n,hn⟩
      exact mem_iUnion.mpr ⟨n,n,le_rfl,hn⟩
    · intro h
      obtain ⟨N,n,_,hn⟩ := mem_iUnion.mp h
      exact ⟨n,hn⟩
  rw [he,hmono.measure_iUnion]
  exact iSup_le fun N => finite_crossing_bound μ F M hM h0 hinitial c hc N

/-- Every data-selected natural time is covered by the same actual event. -/
theorem selected_time_bound (hM : Supermartingale M F μ)
    (h0 : ∀ n ω,0≤M n ω) (hinitial : (∫ ω,M 0 ω ∂μ)≤1)
    (c : ℝ) (hc : 0<c) (t : Ω → ℕ) :
    μ {ω | c≤M (t ω) ω}≤ENNReal.ofReal (1/c) := by
  have hs : {ω | c≤M (t ω) ω}⊆crossing M c := by
    intro ω hω
    exact ⟨t ω,hω⟩
  exact (measure_mono hs).trans (crossing_bound μ F M hM h0 hinitial c hc)

end Komorebi.LSM.VilleInequality
