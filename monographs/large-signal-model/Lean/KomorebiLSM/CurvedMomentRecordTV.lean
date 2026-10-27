import KomorebiLSM.CurvedMomentTV
import KomorebiLSM.ObservationLawComparison
import KomorebiLSM.MarkovMinorization
import Mathlib.Tactic

/-! Completed observable history kernels and their exact P52 operator-product
law. Completion preserves every interval signal, including model-null histories. -/
set_option autoImplicit false
namespace Komorebi.LSM.CurvedMoment
open MeasureTheory ProbabilityTheory
open scoped ENNReal
noncomputable section

/-- Only observations outside the declared support use a fallback. -/
def observedSignal (u : ℝ) : Signal :=
  ⟨if u∈Set.Icc (-1:ℝ) 1 then u else 0,by
    split_ifs with hu
    · exact hu
    · norm_num⟩

theorem observedSignal_eq {u : ℝ} (hu : u∈Set.Icc (-1:ℝ) 1) :
    (observedSignal u : ℝ)=u := by simp [observedSignal,hu]

theorem observedSignal_measurable : Measurable observedSignal := by
  apply Measurable.subtype_mk
  exact measurable_id.ite measurableSet_Icc measurable_const

def currentSignal (s : Signal) : (n : ℕ) → ContinuousRecords.History ℝ n → Signal
  | 0,_ => s
  | _+1,h => observedSignal h.2

theorem currentSignal_measurable (s : Signal) :
    (n : ℕ) → Measurable (currentSignal s n)
  | 0 => measurable_const
  | _+1 => observedSignal_measurable.comp measurable_snd

namespace Reference
variable {μ : Measure ℝ} (R : Reference μ)

def completedKernel (a b ρ : ℝ) (hρ : 0≤ρ) (hab : |a|+|b|≤1-ρ) : Kernel ℝ ℝ :=
  (R.signalKernel a b ρ hρ hab).comap observedSignal observedSignal_measurable

instance completedKernel_markov (a b ρ : ℝ) (hρ : 0≤ρ) (hab : |a|+|b|≤1-ρ) :
    IsMarkovKernel (R.completedKernel a b ρ hρ hab) := by unfold completedKernel;infer_instance

theorem completedKernel_on_interval (a b ρ : ℝ) (hρ : 0≤ρ) (hab : |a|+|b|≤1-ρ)
    (u : ℝ) (hu : u∈Set.Icc (-1:ℝ) 1) :
    R.completedKernel a b ρ hρ hab u=R.signalKernel a b ρ hρ hab ⟨u,hu⟩ := by
  change R.signalKernel a b ρ hρ hab (observedSignal u)=_
  congr 1
  exact Subtype.ext (observedSignal_eq hu)

def futureKernel (a b ρ : ℝ) (hρ : 0≤ρ) (hab : |a|+|b|≤1-ρ) (s : Signal) (n : ℕ) :
    Kernel (ContinuousRecords.History ℝ n) ℝ :=
  (R.signalKernel a b ρ hρ hab).comap (currentSignal s n) (currentSignal_measurable s n)

instance futureKernel_markov (a b ρ : ℝ) (hρ : 0≤ρ) (hab : |a|+|b|≤1-ρ) (s : Signal) (n : ℕ) :
    IsMarkovKernel (R.futureKernel a b ρ hρ hab s n) := by unfold futureKernel;infer_instance

/-- The literal chronological law of the globally completed observation kernels. -/
def futureLaw (a b ρ : ℝ) (hρ : 0≤ρ) (hab : |a|+|b|≤1-ρ) (s : Signal) :
    (n : ℕ) → Measure (ContinuousRecords.History ℝ n)
  | 0 => Measure.dirac PUnit.unit
  | n+1 => futureLaw a b ρ hρ hab s n ⊗ₘ R.futureKernel a b ρ hρ hab s n

instance futureLaw_probability (a b ρ : ℝ) (hρ : 0≤ρ) (hab : |a|+|b|≤1-ρ) (s : Signal) :
    (n : ℕ) → IsProbabilityMeasure (R.futureLaw a b ρ hρ hab s n)
  | 0 => inferInstanceAs (IsProbabilityMeasure (Measure.dirac PUnit.unit))
  | n+1 => by
    let := futureLaw_probability a b ρ hρ hab s n
    exact inferInstanceAs (IsProbabilityMeasure
      (R.futureLaw a b ρ hρ hab s n ⊗ₘ R.futureKernel a b ρ hρ hab s n))

/-- This is exact even on zero-mass and signed histories. No normalized
posterior identity on null branches is used. -/
theorem observationRun_rank_one (a b ρ : ℝ) (hρ : 0≤ρ) (hab : |a|+|b|≤1-ρ)
    (z : State) (n : ℕ) (h : ContinuousRecords.History ℝ (n+1)) :
    ContinuousRecords.observationRun (R.instrument a b ρ hρ hab) (fun _ => ()) z (n+1) h=
      mass (ContinuousRecords.observationRun (R.instrument a b ρ hρ hab) (fun _ => ()) z (n+1) h) • curve h.2 := by
  change branch a b h.2 _=mass (branch a b h.2 _) • curve h.2
  rw [branch_mass,branch_apply]

theorem observationRun_mass_factor (a b ρ : ℝ) (hρ : 0≤ρ) (hab : |a|+|b|≤1-ρ)
    (s : Signal) : ∀ n,∀ᵐ h∂ContinuousRecords.reference μ n,∀ u,
      mass (ContinuousRecords.observationRun (R.instrument a b ρ hρ hab) (fun _ => ())
        (curve s) (n+1) (h,u))=
      mass (ContinuousRecords.observationRun (R.instrument a b ρ hρ hab) (fun _ => ())
        (curve s) n h)*likelihood a b u (curve (currentSignal s n h)) := by
  let := R.probability
  intro n
  cases n with
  | zero =>
    apply Filter.Eventually.of_forall
    intro h u
    change mass (branch a b u (curve s))=mass (curve s)*likelihood a b u (curve s)
    rw [branch_mass]
    simp [mass,curve]
  | succ n =>
    have hs : ∀ᵐ h∂ContinuousRecords.reference μ (n+1),h.2∈Set.Icc (-1:ℝ) 1 := by
      apply (Measure.ae_prod_iff_ae_ae (measurableSet_Icc.preimage measurable_snd)).mpr
      exact Filter.Eventually.of_forall (fun _ => R.support)
    filter_upwards [hs] with h hv u
    obtain ⟨h,v⟩ := h
    change mass (branch a b u _)=_
    rw [observationRun_rank_one,map_smul,map_smul,branch_mass]
    simp only [smul_eq_mul]
    simp [currentSignal,mass_apply,curve,observedSignal_eq hv]

/-- The actual P52 operator-density law equals the completed-kernel law.
In particular, model-null interval histories keep the observed curve state. -/
theorem observationLaw_eq_futureLaw (a b ρ : ℝ) (hρ : 0≤ρ) (hab : |a|+|b|≤1-ρ)
    (s : Signal) : ∀ n,
    ContinuousRecords.observationLaw (R.instrument a b ρ hρ hab) (fun _ => ()) (curve s) n=
      R.futureLaw a b ρ hρ hab s n := by
  let := R.probability
  let D := R.instrument a b ρ hρ hab
  intro n
  induction n with
  | zero =>
    change (Measure.dirac PUnit.unit).withDensity (fun _ => ENNReal.ofReal (mass (curve s)))=
      Measure.dirac PUnit.unit
    norm_num [mass,curve]
  | succ n ih =>
    let k : ContinuousRecords.History ℝ n → ℝ → ℝ≥0∞ := fun h u =>
      ENNReal.ofReal (likelihood a b u (curve (currentSignal s n h)))
    have hk : Measurable (Function.uncurry k) := by
      unfold k likelihood legendre curve
      have hs : Measurable (fun p : ContinuousRecords.History ℝ n × ℝ =>
          (currentSignal s n p.1 : ℝ)) :=
        (measurable_subtype_coe.comp (currentSignal_measurable s n)).comp measurable_fst
      fun_prop
    have hkernel : R.futureKernel a b ρ hρ hab s n=
        (Kernel.const _ μ).withDensity k := by
      apply Kernel.ext
      intro h
      rw [Kernel.withDensity_apply _ hk]
      change R.signalKernel a b ρ hρ hab (currentSignal s n h)=μ.withDensity (k h)
      rw [R.signalKernel_apply]
      congr 1
      funext u
      change ENNReal.ofReal (1+a*(currentSignal s n h:ℝ)*u+
        b*(currentSignal s n h:ℝ)^2*legendre u)=
          ENNReal.ofReal (1+a*u*(currentSignal s n h:ℝ)+
            b*legendre u*(currentSignal s n h:ℝ)^2)
      congr 1
      ring
    have : IsMarkovKernel ((Kernel.const (ContinuousRecords.History ℝ n) μ).withDensity k) := by
      rw [←hkernel]
      infer_instance
    rw [futureLaw,← ih,hkernel]
    simp only [ContinuousRecords.observationLaw]
    rw [
      Measure.withDensity_compProd_withDensity (ContinuousRecords.observationDensity_measurable D _ _ n) hk,
      Measure.compProd_const]
    change (ContinuousRecords.reference μ (n+1)).withDensity _=
      (ContinuousRecords.reference μ (n+1)).withDensity _
    apply withDensity_congr_ae
    have hmleft := ContinuousRecords.observationDensity_measurable D (fun _ => ()) (curve s) (n+1)
    have hmright := ((ContinuousRecords.observationDensity_measurable D (fun _ => ()) (curve s) n).comp
      (measurable_fst : Measurable (Prod.fst : ContinuousRecords.History ℝ n × ℝ → _))).mul hk
    apply (Measure.ae_prod_iff_ae_ae (measurableSet_eq_fun hmleft hmright)).mpr
    filter_upwards [R.observationRun_mass_factor a b ρ hρ hab s n,
      ContinuousRecords.observationRun_mem_ae D (fun _ => ()) (curve_mem s s.2) n] with h hh hc
    apply Filter.Eventually.of_forall
    intro u
    change ENNReal.ofReal (mass _)=ENNReal.ofReal (mass _)*ENNReal.ofReal (likelihood a b u (curve (currentSignal s n h)))
    rw [hh u]
    have hm : 0≤mass (ContinuousRecords.observationRun (R.instrument a b ρ hρ hab)
        (fun _ => ()) (curve s) n h) := probabilityCone.mass_nonneg hc
    exact ENNReal.ofReal_mul hm

/-- Full future observation records telescope the genuine conditional kernel
error; no coordinate-state estimation error is accumulated. -/
theorem futureLaw_lawTV_le (a b ρ a' b' ρ' da db : ℝ)
    (hρ : 0≤ρ) (hab : |a|+|b|≤1-ρ) (hρ' : 0≤ρ') (hab' : |a'|+|b'|≤1-ρ')
    (ha : |a-a'|≤da) (hb : |b-b'|≤db) (s : Signal) (T : ℕ) :
    SequentialLowerCertificate.lawTV (R.futureLaw a b ρ hρ hab s T)
      (R.futureLaw a' b' ρ' hρ' hab' s T)≤min 1 ((T:ℝ)*R.parameterBudget da db) := by
  apply le_min (SequentialLowerCertificate.lawTV_le_one _ _)
  induction T with
  | zero => simp [futureLaw,SequentialLowerCertificate.lawTV_self]
  | succ n ih =>
    have hu := MarkovStability.compProd_uniform_change
      (R.futureLaw a b ρ hρ hab s n) (R.futureKernel a b ρ hρ hab s n)
      (R.futureKernel a' b' ρ' hρ' hab' s n) (R.parameterBudget da db)
      (fun h => R.signalKernel_lawTV_le a b ρ a' b' ρ' da db hρ hab hρ' hab' ha hb (currentSignal s n h))
    have hc := MeasureTVCalculus.lawTV_compProd (R.futureLaw a b ρ hρ hab s n)
      (R.futureLaw a' b' ρ' hρ' hab' s n) (R.futureKernel a' b' ρ' hρ' hab' s n)
    have ht := MeasureTVCalculus.lawTV_triangle
      (R.futureLaw a b ρ hρ hab s n ⊗ₘ R.futureKernel a b ρ hρ hab s n)
      (R.futureLaw a b ρ hρ hab s n ⊗ₘ R.futureKernel a' b' ρ' hρ' hab' s n)
      (R.futureLaw a' b' ρ' hρ' hab' s n ⊗ₘ R.futureKernel a' b' ρ' hρ' hab' s n)
    change SequentialLowerCertificate.lawTV (_ ⊗ₘ _) (_ ⊗ₘ _)≤_
    have he := ht.trans (add_le_add hu hc)
    push_cast
    linarith

instance observationLaw_curve_probability (a b ρ : ℝ) (hρ : 0≤ρ) (hab : |a|+|b|≤1-ρ)
    (s : Signal) (T : ℕ) : IsProbabilityMeasure
      (ContinuousRecords.observationLaw (R.instrument a b ρ hρ hab) (fun _ => ()) (curve s) T) := by
  let := R.probability
  exact ContinuousRecords.observationLaw_probability _ _ (curveState s) T

/-- The complete future records are the actual P52 operator-product measures. -/
theorem observationLaw_lawTV_le (a b ρ a' b' ρ' da db : ℝ)
    (hρ : 0≤ρ) (hab : |a|+|b|≤1-ρ) (hρ' : 0≤ρ') (hab' : |a'|+|b'|≤1-ρ')
    (ha : |a-a'|≤da) (hb : |b-b'|≤db) (s : Signal) (T : ℕ) :
    SequentialLowerCertificate.lawTV
      (ContinuousRecords.observationLaw (R.instrument a b ρ hρ hab) (fun _ => ()) (curve s) T)
      (ContinuousRecords.observationLaw (R.instrument a' b' ρ' hρ' hab') (fun _ => ()) (curve s) T)
      ≤min 1 ((T:ℝ)*R.parameterBudget da db) := by
  simpa only [R.observationLaw_eq_futureLaw] using
    R.futureLaw_lawTV_le a b ρ a' b' ρ' da db hρ hab hρ' hab' ha hb s T

end Reference
end
end Komorebi.LSM.CurvedMoment
