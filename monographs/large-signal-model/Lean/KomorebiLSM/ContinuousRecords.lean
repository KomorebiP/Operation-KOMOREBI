import KomorebiLSM.ContinuousInstrument
import Mathlib.MeasureTheory.Measure.Prod
import Mathlib.MeasureTheory.Integral.Lebesgue.Countable
import Mathlib.Probability.Kernel.Composition.WithDensity

/-! Finite continuous record laws are literal densities of operator products.
Policy factors are measurable and normalized at each history. Normalization and
prefix consistency are derived by integration, rather than supplied as fields. -/
set_option autoImplicit false
namespace Komorebi.LSM.ContinuousRecords
open MeasureTheory ProbabilityTheory
open scoped ENNReal BigOperators

universe u
/-- A finite ordered record, extended on the right. -/
def History (X : Type u) : ℕ → Type u
  | 0 => PUnit.{u+1}
  | n+1 => History X n × X

instance historyMeasurable {X : Type*} [MeasurableSpace X] :
    (n : ℕ) → MeasurableSpace (History X n)
  | 0 => inferInstanceAs (MeasurableSpace PUnit)
  | n+1 => by
    letI := historyMeasurable (X := X) n
    exact inferInstanceAs (MeasurableSpace (History X n × X))

attribute [reducible] History

/-- The actual iterated product reference measure, including the empty record. -/
noncomputable def reference {X : Type*} [MeasurableSpace X] (ν : Measure X) :
    (n : ℕ) → Measure (History X n)
  | 0 => Measure.dirac PUnit.unit
  | n+1 => (reference ν n).prod ν

instance reference_finite {X : Type*} [MeasurableSpace X] (ν : Measure X)
    [IsFiniteMeasure ν] : (n : ℕ) → IsFiniteMeasure (reference ν n)
  | 0 => inferInstanceAs (IsFiniteMeasure (Measure.dirac PUnit.unit))
  | n+1 => by
    let := reference_finite ν n
    exact inferInstanceAs (IsFiniteMeasure ((reference ν n).prod ν))

/-- Remove a specified number of terminal records. -/
def truncate {X : Type*} (n : ℕ) : (k : ℕ) → History X (n+k) → History X n
  | 0,h => h
  | k+1,h => truncate n k h.1

theorem truncate_measurable {X : Type*} [MeasurableSpace X] (n : ℕ) :
    (k : ℕ) → Measurable (truncate (X := X) n k)
  | 0 => measurable_id
  | k+1 => (truncate_measurable n k).comp measurable_fst

/-- Apply a measurable observation or record map coordinate by coordinate. -/
def mapHistory {X Z : Type*} (f : X → Z) : (n : ℕ) → History X n → History Z n
  | 0,_ => PUnit.unit
  | n+1,h => (mapHistory f n h.1,f h.2)

theorem mapHistory_measurable {X Z : Type*} [MeasurableSpace X] [MeasurableSpace Z]
    {f : X → Z} (hf : Measurable f) : (n : ℕ) → Measurable (mapHistory f n)
  | 0 => measurable_const
  | n+1 => ((mapHistory_measurable hf n).comp measurable_fst).prodMk (hf.comp measurable_snd)

theorem mapHistory_first_marginal {X Z : Type*} [MeasurableSpace X] [MeasurableSpace Z]
    {f : X → Z} (hf : Measurable f) (n : ℕ) (ν : Measure (History X (n+1))) :
    (ν.map (mapHistory f (n+1))).fst=ν.fst.map (mapHistory f n) := by
  exact (Measure.map_map (μ := ν) measurable_fst (mapHistory_measurable hf (n+1))).trans
    (Measure.map_map (μ := ν) (mapHistory_measurable hf n) measurable_fst).symm

/-- Integrating the last coordinate gives the actual first marginal. -/
theorem density_first_marginal {X Z : Type*} [MeasurableSpace X] [MeasurableSpace Z]
    (ν : Measure X) (η : Measure Z) [SFinite ν] [SFinite η]
    (f : X × Z → ℝ≥0∞) (g : X → ℝ≥0∞) (hf : Measurable f)
    (h : ∀ᵐ x∂ν,(∫⁻ y,f (x,y)∂η)=g x) :
    ((ν.prod η).withDensity f).fst=ν.withDensity g := by
  ext S hS
  rw [Measure.fst_apply hS,withDensity_apply _ (measurable_fst hS),
    withDensity_apply _ hS]
  have he : Prod.fst ⁻¹' S=S ×ˢ (Set.univ : Set Z) := Set.ext (by simp)
  rw [he,setLIntegral_prod _ hf.aemeasurable]
  simp only [Measure.restrict_univ]
  exact lintegral_congr_ae (h.filter_mono (ae_mono Measure.restrict_le_self))

variable {E A Y : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E]
variable [FiniteDimensional ℝ E] [MeasurableSpace E] [BorelSpace E]
variable [MeasurableSpace Y] [MeasurableSpace A] [Fintype A] [MeasurableSingletonClass A]
variable {C : BaseNorm.ProbabilityCone E} {μ : Measure Y}
variable (D : ContinuousInstrument.DensityInstrument (A := A) C μ)

/-- The genuine unnormalized operator product on a recorded action/observation history. -/
noncomputable def run (z : E) : (n : ℕ) → History (A × Y) n → E
  | 0, _ => z
  | n+1, h => D.op h.2.1 h.2.2 (run z n h.1)

omit [FiniteDimensional ℝ E] [MeasurableSpace E] [BorelSpace E] in
theorem op_measurable : Measurable (Function.uncurry D.op) :=
  measurable_from_prod_countable_right D.measurable_op

theorem run_measurable (z : E) : (n : ℕ) → Measurable (run D z n)
  | 0 => measurable_const
  | n+1 => by
    exact (isBoundedBilinearMap_apply (𝕜 := ℝ) (E := E) (F := E)).continuous.measurable.comp
      (((op_measurable D).comp measurable_snd).prodMk ((run_measurable z n).comp measurable_fst))

/-- Any measurable randomized finite-action policy, with explicit pointwise normalization. -/
structure Policy where
  probability : (n : ℕ) → History (A × Y) n → A → ℝ≥0∞
  measurable_probability : ∀ n a,Measurable (fun h => probability n h a)
  sum_one : ∀ n h,∑ a,probability n h a=1

namespace Policy
variable (π : Policy (A := A) (Y := Y))

noncomputable def weight : (n : ℕ) → History (A × Y) n → ℝ≥0∞
  | 0, _ => 1
  | n+1, h => weight n h.1 * π.probability n h.1 h.2.1

theorem weight_measurable : (n : ℕ) → Measurable (π.weight n)
  | 0 => measurable_const
  | n+1 => by
    have hp : Measurable (fun p : History (A × Y) n × A => π.probability n p.1 p.2) :=
      measurable_from_prod_countable_left (π.measurable_probability n)
    exact ((weight_measurable n).comp measurable_fst).mul
      (hp.comp (measurable_fst.prodMk (measurable_fst.comp measurable_snd)))

end Policy

/-- The counting-action and observation reference for one recorded step. -/
noncomputable def stepReference (μ : Measure Y) : Measure (A × Y) := Measure.count.prod μ

instance stepReference_finite [IsFiniteMeasure μ] :
    IsFiniteMeasure (stepReference (A := A) μ) :=
  inferInstanceAs (IsFiniteMeasure (Measure.count.prod μ))

/-- Policy factors multiply the mass of the actual operator product. -/
noncomputable def recordDensity (π : Policy (A := A) (Y := Y)) (z : E) (n : ℕ)
    (h : History (A × Y) n) : ℝ≥0∞ := π.weight n h * ENNReal.ofReal (C.mass (run D z n h))

theorem recordDensity_measurable (π : Policy (A := A) (Y := Y)) (z : E) (n : ℕ) :
    Measurable (recordDensity D π z n) :=
  (Policy.weight_measurable π n).mul (((ContinuousInstrument.massCLM C).continuous.measurable.comp
    (run_measurable D z n)).ennreal_ofReal)

/-- An actual measure on finite action/observation records. -/
noncomputable def recordLaw (π : Policy (A := A) (Y := Y)) (z : E) (n : ℕ) :
    Measure (History (A × Y) n) :=
  (reference (stepReference (A := A) μ) n).withDensity (recordDensity D π z n)


variable [IsProbabilityMeasure μ]

theorem run_mem_ae {z : E} (hz : z∈C.carrier) : (n : ℕ) →
    ∀ᵐ h∂reference (stepReference (A := A) μ) n,run D z n h∈C.carrier
  | 0 => by simpa [run] using Filter.Eventually.of_forall (fun _ => hz)
  | n+1 => by
    apply (Measure.ae_prod_iff_ae_ae (C.closed.measurableSet.preimage (run_measurable D z (n+1)))).mpr
    filter_upwards [run_mem_ae hz n] with h hh
    apply (Measure.ae_prod_iff_ae_ae (C.closed.measurableSet.preimage
      ((run_measurable D z (n+1)).comp (measurable_const.prodMk measurable_id)))).mpr
    rw [Measure.ae_count_iff]
    intro a
    filter_upwards [D.positive a] with y hy
    exact hy _ hh

omit [MeasurableSpace E] [BorelSpace E] [MeasurableSpace A] [Fintype A]
  [MeasurableSingletonClass A] [IsProbabilityMeasure μ] in
theorem integrated_density_mass (a : A) {z : E} (hz : z∈C.carrier) :
    (∫⁻ y,ENNReal.ofReal (D.density a y z)∂μ)=ENNReal.ofReal (C.mass z) := by
  rw [← ofReal_integral_eq_lintegral_ofReal (D.density_integrable a z)
    (D.density_nonneg_ae a hz),D.integral_density a z]

theorem recordDensity_integrate_last (π : Policy (A := A) (Y := Y))
    (z : E) (n : ℕ) (h : History (A × Y) n) (hh : run D z n h∈C.carrier) :
    (∫⁻ r,recordDensity D π z (n+1) (h,r)∂stepReference (A := A) μ)=
      recordDensity D π z n h := by
  have hm : Measurable (fun r : A × Y => recordDensity D π z (n+1) (h,r)) :=
    (recordDensity_measurable D π z (n+1)).comp (measurable_const.prodMk measurable_id)
  rw [stepReference,lintegral_prod _ hm.aemeasurable]
  change (∫⁻ a,∫⁻ y,(π.weight n h * π.probability n h a) *
    ENNReal.ofReal (D.density a y (run D z n h))∂μ∂Measure.count)=recordDensity D π z n h
  have hi (a : A) : (∫⁻ y,(π.weight n h * π.probability n h a) *
      ENNReal.ofReal (D.density a y (run D z n h))∂μ)=
      (π.weight n h * π.probability n h a)*ENNReal.ofReal (C.mass (run D z n h)) := by
    have hd : Measurable (fun y : Y => ENNReal.ofReal (D.density a y (run D z n h))) :=
      ((D.density_measurable a).comp (measurable_const.prodMk measurable_id)).ennreal_ofReal
    rw [lintegral_const_mul _ hd,integrated_density_mass D a hh]
  simp_rw [hi,lintegral_count,tsum_fintype]
  rw [← Finset.sum_mul,← Finset.mul_sum,π.sum_one,mul_one]
  rfl



/-- Consistency is the equality of literal prefix marginals. -/
theorem recordLaw_consistent (π : Policy (A := A) (Y := Y)) {z : E}
    (hz : z∈C.carrier) (n : ℕ) :
    (recordLaw D π z (n+1)).fst=recordLaw D π z n := by
  apply density_first_marginal _ _ _ _ (recordDensity_measurable D π z (n+1))
  filter_upwards [run_mem_ae D hz n] with h hh
  exact recordDensity_integrate_last D π z n h hh

/-- Every finite record law has total probability one. -/
theorem recordLaw_univ (π : Policy (A := A) (Y := Y))
    (z : ContinuousInstrument.DensityInstrument.State C) :
    (n : ℕ) → recordLaw D π z.1 n Set.univ=1
  | 0 => by simp [recordLaw,reference,recordDensity,Policy.weight,run,z.2.2]
  | n+1 => by
    have hm := congrArg (fun ν : Measure (History (A × Y) n) => ν Set.univ)
      (recordLaw_consistent D π z.2.1 n)
    exact (Measure.fst_univ (ρ := recordLaw D π z.1 (n+1))).symm.trans (hm.trans (recordLaw_univ π z n))

instance recordLaw_probability (π : Policy (A := A) (Y := Y))
    (z : ContinuousInstrument.DensityInstrument.State C) (n : ℕ) :
    IsProbabilityMeasure (recordLaw D π z.1 n) := ⟨recordLaw_univ D π z n⟩

omit [FiniteDimensional ℝ E] [MeasurableSpace E] [BorelSpace E]
  [MeasurableSingletonClass A] [IsProbabilityMeasure μ] in
theorem recordLaw_event (π : Policy (A := A) (Y := Y)) (z : E) (n : ℕ)
    (S : Set (History (A × Y) n)) (hS : MeasurableSet S) :
    recordLaw D π z n S=∫⁻ h in S,recordDensity D π z n h∂reference (stepReference (A := A) μ) n :=
  withDensity_apply _ hS


/-- Prescribed actions retain the genuine, unnormalized chronological product. -/
noncomputable def observationRun (actions : ℕ → A) (z : E) :
    (n : ℕ) → History Y n → E
  | 0, _ => z
  | n+1,h => D.op (actions n) h.2 (observationRun actions z n h.1)

omit [MeasurableSpace A] [Fintype A] [MeasurableSingletonClass A] [IsProbabilityMeasure μ] in
theorem observationRun_measurable (actions : ℕ → A) (z : E) :
    (n : ℕ) → Measurable (observationRun D actions z n)
  | 0 => measurable_const
  | n+1 => by
    exact (isBoundedBilinearMap_apply (𝕜 := ℝ) (E := E) (F := E)).continuous.measurable.comp
      (((D.measurable_op (actions n)).comp measurable_snd).prodMk
        ((observationRun_measurable actions z n).comp measurable_fst))

omit [MeasurableSpace A] [Fintype A] [MeasurableSingletonClass A] in
theorem observationRun_mem_ae (actions : ℕ → A) {z : E} (hz : z∈C.carrier) :
    (n : ℕ) → ∀ᵐ h∂reference μ n,observationRun D actions z n h∈C.carrier
  | 0 => by simpa [observationRun] using Filter.Eventually.of_forall (fun _ => hz)
  | n+1 => by
    apply (Measure.ae_prod_iff_ae_ae (C.closed.measurableSet.preimage
      (observationRun_measurable D actions z (n+1)))).mpr
    filter_upwards [observationRun_mem_ae actions hz n] with h hh
    filter_upwards [D.positive (actions n)] with y hy
    exact hy _ hh

/-- Exact operator-product density with respect to the nested product reference μ^n. -/
noncomputable def observationDensity (actions : ℕ → A) (z : E) (n : ℕ)
    (h : History Y n) : ℝ≥0∞ := ENNReal.ofReal (C.mass (observationRun D actions z n h))

omit [MeasurableSpace A] [Fintype A] [MeasurableSingletonClass A] [IsProbabilityMeasure μ] in
theorem observationDensity_measurable (actions : ℕ → A) (z : E) (n : ℕ) :
    Measurable (observationDensity D actions z n) :=
  ((ContinuousInstrument.massCLM C).continuous.measurable.comp
    (observationRun_measurable D actions z n)).ennreal_ofReal

noncomputable def observationLaw (actions : ℕ → A) (z : E) (n : ℕ) :
    Measure (History Y n) := (reference μ n).withDensity (observationDensity D actions z n)

omit [MeasurableSpace A] [Fintype A] [MeasurableSingletonClass A] in
theorem observationLaw_consistent (actions : ℕ → A) {z : E}
    (hz : z∈C.carrier) (n : ℕ) :
    (observationLaw D actions z (n+1)).fst=observationLaw D actions z n := by
  apply density_first_marginal _ _ _ _ (observationDensity_measurable D actions z (n+1))
  filter_upwards [observationRun_mem_ae D actions hz n] with h hh
  exact integrated_density_mass D (actions n) hh

omit [MeasurableSpace A] [Fintype A] [MeasurableSingletonClass A] in
theorem observationLaw_univ (actions : ℕ → A)
    (z : ContinuousInstrument.DensityInstrument.State C) :
    (n : ℕ) → observationLaw D actions z.1 n Set.univ=1
  | 0 => by simp [observationLaw,reference,observationDensity,observationRun,z.2.2]
  | n+1 => by
    have hm := congrArg (fun ν : Measure (History Y n) => ν Set.univ)
      (observationLaw_consistent D actions z.2.1 n)
    exact (Measure.fst_univ (ρ := observationLaw D actions z.1 (n+1))).symm.trans
      (hm.trans (observationLaw_univ actions z n))

instance observationLaw_probability (actions : ℕ → A)
    (z : ContinuousInstrument.DensityInstrument.State C) (n : ℕ) :
    IsProbabilityMeasure (observationLaw D actions z.1 n) := ⟨observationLaw_univ D actions z n⟩

omit [FiniteDimensional ℝ E] [MeasurableSpace E] [BorelSpace E]
  [MeasurableSpace A] [Fintype A] [MeasurableSingletonClass A] [IsProbabilityMeasure μ] in
theorem observationLaw_product_density (actions : ℕ → A) (z : E) (n : ℕ)
    (S : Set (History Y n)) (hS : MeasurableSet S) :
    observationLaw D actions z n S=
      ∫⁻ h in S,ENNReal.ofReal (C.mass (observationRun D actions z n h))∂reference μ n :=
  withDensity_apply _ hS


/-- A measurable normalized version, with an explicit valid fallback on null prefixes. -/
noncomputable def normalizeValue (fallback : ContinuousInstrument.DensityInstrument.State C)
    (z : E) : E := by
  classical
  exact if z∈C.carrier ∧ 0<C.mass z then (C.mass z)⁻¹ • z else fallback.1

omit [FiniteDimensional ℝ E] [MeasurableSpace E] [BorelSpace E] in
theorem normalizeValue_mem (fallback : ContinuousInstrument.DensityInstrument.State C) (z : E) :
    normalizeValue fallback z∈C.base := by
  classical
  unfold normalizeValue
  split_ifs with h
  · refine ⟨C.smul_mem (inv_nonneg.mpr h.2.le) h.1,?_⟩
    rw [map_smul,smul_eq_mul,inv_mul_cancel₀ h.2.ne']
  · exact fallback.2

noncomputable def normalize (fallback : ContinuousInstrument.DensityInstrument.State C) (z : E) :
    ContinuousInstrument.DensityInstrument.State C :=
  ⟨normalizeValue fallback z,normalizeValue_mem fallback z⟩

theorem normalize_measurable (fallback : ContinuousInstrument.DensityInstrument.State C) :
    Measurable (normalize fallback) := by
  have hm : Measurable (fun z : E => C.mass z) := (ContinuousInstrument.massCLM C).continuous.measurable
  have hc : MeasurableSet {z : E | z∈C.carrier ∧ 0<C.mass z} :=
    C.closed.measurableSet.inter (measurableSet_lt measurable_const hm)
  exact ((hm.inv.smul measurable_id).ite hc measurable_const).subtype_mk

omit [FiniteDimensional ℝ E] [MeasurableSpace E] [BorelSpace E] in
/-- Zero-mass cone prefixes are zero; consequently the fallback cancels exactly. -/
theorem mass_smul_normalize (fallback : ContinuousInstrument.DensityInstrument.State C)
    {z : E} (hz : z∈C.carrier) : C.mass z • (normalize fallback z).1=z := by
  classical
  by_cases hm : C.mass z=0
  · have hz0 := (C.mass_zero_iff hz).mp hm
    simp [hz0]
  · have hp : 0<C.mass z := lt_of_le_of_ne (C.mass_nonneg hz) (Ne.symm hm)
    simp [normalize,normalizeValue,hz,hp,smul_smul,hm]

omit [FiniteDimensional ℝ E] [MeasurableSpace E] [BorelSpace E]
  [MeasurableSpace A] [Fintype A] [MeasurableSingletonClass A] [IsProbabilityMeasure μ] in
theorem density_normalize_factor (fallback : ContinuousInstrument.DensityInstrument.State C)
    (a : A) (y : Y) {z : E} (hz : z∈C.carrier) :
    C.mass z * D.density a y (normalize fallback z).1=D.density a y z := by
  change C.mass z * C.mass (D.op a y (normalize fallback z).1)=C.mass (D.op a y z)
  rw [← smul_eq_mul,← map_smul,← map_smul,mass_smul_normalize fallback hz]


/-- The conditional action/observation density from the actual normalized prefix. -/
noncomputable def nextDensity (π : Policy (A := A) (Y := Y))
    (fallback : ContinuousInstrument.DensityInstrument.State C) (z : E) (n : ℕ)
    (h : History (A × Y) n) (r : A × Y) : ℝ≥0∞ :=
  π.probability n h r.1 * ENNReal.ofReal
    (D.density r.1 r.2 (normalize fallback (run D z n h)).1)

omit [IsProbabilityMeasure μ] in
theorem nextDensity_measurable (π : Policy (A := A) (Y := Y))
    (fallback : ContinuousInstrument.DensityInstrument.State C) (z : E) (n : ℕ) :
    Measurable (Function.uncurry (nextDensity D π fallback z n)) := by
  have hp : Measurable (fun p : History (A × Y) n × A => π.probability n p.1 p.2) :=
    measurable_from_prod_countable_left (π.measurable_probability n)
  have hd : Measurable (fun p : A × (ContinuousInstrument.DensityInstrument.State C × Y) =>
      ENNReal.ofReal (D.density p.1 p.2.2 p.2.1.1)) :=
    measurable_from_prod_countable_right D.kernel_density_measurable
  exact (hp.comp (measurable_fst.prodMk (measurable_fst.comp measurable_snd))).mul
    (hd.comp ((measurable_fst.comp measurable_snd).prodMk
      (((normalize_measurable fallback).comp ((run_measurable D z n).comp measurable_fst)).prodMk
        (measurable_snd.comp measurable_snd))))

theorem nextDensity_integral (π : Policy (A := A) (Y := Y))
    (fallback : ContinuousInstrument.DensityInstrument.State C) (z : E) (n : ℕ)
    (h : History (A × Y) n) :
    (∫⁻ r,nextDensity D π fallback z n h r∂stepReference (A := A) μ)=1 := by
  have hm : Measurable (nextDensity D π fallback z n h) :=
    (nextDensity_measurable D π fallback z n).comp (measurable_const.prodMk measurable_id)
  rw [stepReference,lintegral_prod _ hm.aemeasurable]
  have hi (a : A) : (∫⁻ y,nextDensity D π fallback z n h (a,y)∂μ)=π.probability n h a := by
    have hd : Measurable (fun y : Y => ENNReal.ofReal
      (D.density a y (normalize fallback (run D z n h)).1)) :=
      (D.kernel_density_measurable a).comp (measurable_const.prodMk measurable_id)
    change (∫⁻ y,π.probability n h a * ENNReal.ofReal
      (D.density a y (normalize fallback (run D z n h)).1)∂μ)=_
    rw [lintegral_const_mul _ hd,integrated_density_mass D a
      (normalize fallback (run D z n h)).2.1,(normalize fallback (run D z n h)).2.2,
      ENNReal.ofReal_one,mul_one]
  simp_rw [hi,lintegral_count,tsum_fintype]
  exact π.sum_one n h

noncomputable def nextKernel (π : Policy (A := A) (Y := Y))
    (fallback : ContinuousInstrument.DensityInstrument.State C) (z : E) (n : ℕ) :
    Kernel (History (A × Y) n) (A × Y) :=
  (Kernel.const _ (stepReference (A := A) μ)).withDensity (nextDensity D π fallback z n)

instance nextKernel_markov (π : Policy (A := A) (Y := Y))
    (fallback : ContinuousInstrument.DensityInstrument.State C) (z : E) (n : ℕ) :
    IsMarkovKernel (nextKernel D π fallback z n) := by
  constructor
  intro h
  constructor
  rw [nextKernel,Kernel.withDensity_apply _ (nextDensity_measurable D π fallback z n),
    Kernel.const_apply,withDensity_apply _ MeasurableSet.univ,Measure.restrict_univ,
    nextDensity_integral D π fallback z n h]

/-- The product-density law is generated one step at a time by the probability
instrument kernel and the randomized policy. Null-prefix fallback choices cancel. -/
theorem recordLaw_compProd (π : Policy (A := A) (Y := Y))
    (fallback : ContinuousInstrument.DensityInstrument.State C) {z : E}
    (hz : z∈C.carrier) (n : ℕ) :
    recordLaw D π z (n+1)=recordLaw D π z n ⊗ₘ nextKernel D π fallback z n := by
  have : IsMarkovKernel ((Kernel.const (History (A × Y) n) (stepReference (A := A) μ)).withDensity
      (nextDensity D π fallback z n)) := nextKernel_markov D π fallback z n
  rw [recordLaw,recordLaw,nextKernel,Measure.withDensity_compProd_withDensity
    (recordDensity_measurable D π z n) (nextDensity_measurable D π fallback z n),
    Measure.compProd_const]
  apply withDensity_congr_ae
  apply (Measure.ae_prod_iff_ae_ae (measurableSet_eq_fun
    (recordDensity_measurable D π z (n+1))
    (((recordDensity_measurable D π z n).comp measurable_fst).mul
      (nextDensity_measurable D π fallback z n)))).mpr
  filter_upwards [run_mem_ae D hz n] with h hh
  apply Filter.Eventually.of_forall
  intro r
  change π.weight n h * π.probability n h r.1 *
    ENNReal.ofReal (D.density r.1 r.2 (run D z n h))=
    (π.weight n h * ENNReal.ofReal (C.mass (run D z n h))) *
      (π.probability n h r.1 * ENNReal.ofReal
        (D.density r.1 r.2 (normalize fallback (run D z n h)).1))
  rw [← density_normalize_factor D fallback r.1 r.2 hh,ENNReal.ofReal_mul (C.mass_nonneg hh)]
  ac_rfl


/-- Consistency holds for every earlier finite horizon. -/
theorem recordLaw_prefix (π : Policy (A := A) (Y := Y)) {z : E}
    (hz : z∈C.carrier) (n : ℕ) : (k : ℕ) →
    (recordLaw D π z (n+k)).map (truncate n k)=recordLaw D π z n
  | 0 => by simp [truncate]
  | k+1 => by
    change (recordLaw D π z (n+k+1)).map ((truncate n k) ∘ Prod.fst)=_
    exact (Measure.map_map (μ := recordLaw D π z (n+k+1))
      (truncate_measurable (X := A × Y) n k) measurable_fst).symm.trans
      ((congrArg (fun ν : Measure (History (A × Y) (n+k)) => ν.map (truncate n k))
        (recordLaw_consistent D π hz (n+k))).trans (recordLaw_prefix π hz n k))

omit [MeasurableSpace A] [Fintype A] [MeasurableSingletonClass A] in
theorem observationLaw_prefix (actions : ℕ → A) {z : E}
    (hz : z∈C.carrier) (n : ℕ) : (k : ℕ) →
    (observationLaw D actions z (n+k)).map (truncate n k)=observationLaw D actions z n
  | 0 => by simp [truncate]
  | k+1 => by
    change (observationLaw D actions z (n+k+1)).map ((truncate n k) ∘ Prod.fst)=_
    exact (Measure.map_map (μ := observationLaw D actions z (n+k+1))
      (truncate_measurable (X := Y) n k) measurable_fst).symm.trans
      ((congrArg (fun ν : Measure (History Y (n+k)) => ν.map (truncate n k))
        (observationLaw_consistent D actions hz (n+k))).trans (observationLaw_prefix actions hz n k))


/-- The conditional law chooses the policy action and then uses the actual
ContinuousInstrument kernel at the normalized prefix state. -/
theorem nextKernel_action_event (π : Policy (A := A) (Y := Y))
    (fallback : ContinuousInstrument.DensityInstrument.State C) (z : E) (n : ℕ)
    (h : History (A × Y) n) (a : A) (S : Set Y) (hS : MeasurableSet S) :
    nextKernel D π fallback z n h ({a} ×ˢ S)=
      π.probability n h a * D.kernel a (normalize fallback (run D z n h)) S := by
  have hm : Measurable (nextDensity D π fallback z n h) :=
    (nextDensity_measurable D π fallback z n).comp (measurable_const.prodMk measurable_id)
  rw [nextKernel,Kernel.withDensity_apply _ (nextDensity_measurable D π fallback z n),
    Kernel.const_apply,withDensity_apply _ ((measurableSet_singleton a).prod hS),
    stepReference,setLIntegral_prod _ hm.aemeasurable,lintegral_singleton,
    Measure.count_singleton,mul_one]
  change (∫⁻ y in S,π.probability n h a * ENNReal.ofReal
    (D.density a y (normalize fallback (run D z n h)).1)∂μ)=_
  have hd : Measurable (fun y : Y => ENNReal.ofReal
      (D.density a y (normalize fallback (run D z n h)).1)) :=
    (D.kernel_density_measurable a).comp (measurable_const.prodMk measurable_id)
  rw [lintegral_const_mul _ hd,D.kernel_apply,withDensity_apply _ hS]


omit [FiniteDimensional ℝ E] [MeasurableSpace E] [BorelSpace E] in
theorem normalize_smul_pos (fallback : ContinuousInstrument.DensityInstrument.State C)
    {z : E} (hz : z∈C.carrier) {c : ℝ} (hc : 0<c) :
    normalize fallback (c • z)=normalize fallback z := by
  classical
  by_cases hm : C.mass z=0
  · have hz0 := (C.mass_zero_iff hz).mp hm
    simp [hz0]
  · have hp : 0<C.mass z := lt_of_le_of_ne (C.mass_nonneg hz) (Ne.symm hm)
    apply Subtype.ext
    have hcz : c • z∈C.carrier := C.smul_mem hc.le hz
    have hcm : 0<C.mass (c • z) := by simpa only [map_smul,smul_eq_mul] using mul_pos hc hp
    dsimp only [normalize,normalizeValue]
    rw [ite_eq_left (show c • z∈C.carrier ∧ 0<C.mass (c • z) from ⟨hcz,hcm⟩),
      ite_eq_left (show z∈C.carrier ∧ 0<C.mass z from ⟨hz,hp⟩),map_smul,smul_eq_mul,smul_smul]
    congr 1
    field_simp [hm,hc.ne']

omit [FiniteDimensional ℝ E] [MeasurableSpace E] [BorelSpace E] [MeasurableSpace A] [Fintype A]
  [MeasurableSingletonClass A] [IsProbabilityMeasure μ] in
/-- The normalized product update agrees with the instrument's measurable update
on every positive-density branch outside its common null set. -/
theorem update_eq_normalize_ae (fallback : ContinuousInstrument.DensityInstrument.State C)
    (a : A) (z : ContinuousInstrument.DensityInstrument.State C) :
    ∀ᵐ y∂μ,0<D.density a y z.1 →
      D.update fallback a z y=normalize fallback (D.op a y z.1) := by
  filter_upwards [D.positive a,D.update_eq_ae fallback a z] with y hy hu
  intro hp
  apply Subtype.ext
  rw [hu hp]
  dsimp only [normalize,normalizeValue]
  rw [ite_eq_left (show D.op a y z.1∈C.carrier ∧ 0<C.mass (D.op a y z.1) from
    ⟨hy z.1 z.2.1,hp⟩)]
  rfl


omit [FiniteDimensional ℝ E] [MeasurableSpace E] [BorelSpace E] [MeasurableSpace A]
  [Fintype A] [MeasurableSingletonClass A] [IsProbabilityMeasure μ] in
theorem normalized_run_update_ae (fallback : ContinuousInstrument.DensityInstrument.State C)
    (a : A) {z : E} (hz : z∈C.carrier) (hp : 0<C.mass z) :
    ∀ᵐ y∂μ,0<D.density a y (normalize fallback z).1 →
      normalize fallback (D.op a y z)=D.update fallback a (normalize fallback z) y := by
  filter_upwards [D.positive a,update_eq_normalize_ae D fallback a (normalize fallback z)] with y hy hu
  intro hd
  have hs : C.mass z • D.op a y (normalize fallback z).1=D.op a y z := by
    rw [← map_smul,mass_smul_normalize fallback hz]
  rw [← hs,normalize_smul_pos fallback (hy _ (normalize fallback z).2.1) hp]
  exact (hu hd).symm


/-- The observation-only law under an arbitrary history-dependent policy is an
actual pushforward of the joint action/observation record law. -/
noncomputable def policyObservationLaw (π : Policy (A := A) (Y := Y)) (z : E) (n : ℕ) :
    Measure (History Y n) := (recordLaw D π z n).map (mapHistory Prod.snd n)

instance policyObservationLaw_probability (π : Policy (A := A) (Y := Y))
    (z : ContinuousInstrument.DensityInstrument.State C) (n : ℕ) :
    IsProbabilityMeasure (policyObservationLaw D π z.1 n) := by
  have := recordLaw_probability D π z n
  exact inferInstanceAs (IsProbabilityMeasure ((recordLaw D π z.1 n).map (mapHistory Prod.snd n)))

theorem policyObservationLaw_consistent (π : Policy (A := A) (Y := Y)) {z : E}
    (hz : z∈C.carrier) (n : ℕ) :
    (policyObservationLaw D π z (n+1)).fst=policyObservationLaw D π z n := by
  exact (mapHistory_first_marginal measurable_snd n (recordLaw D π z (n+1))).trans
    (congrArg (fun ν : Measure (History (A × Y) n) => ν.map (mapHistory Prod.snd n))
      (recordLaw_consistent D π hz n))

end Komorebi.LSM.ContinuousRecords
