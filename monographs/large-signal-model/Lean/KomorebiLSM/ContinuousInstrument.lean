import KomorebiLSM.BaseNorm
import Mathlib.Probability.Kernel.WithDensity
import Mathlib.MeasureTheory.Constructions.BorelSpace.ContinuousLinearMap
import Mathlib.MeasureTheory.Integral.Bochner.ContinuousLinearMap
import Mathlib.MeasureTheory.Integral.Bochner.Set
import Mathlib.MeasureTheory.Measure.Real

/-! P52: continuous observation densities are actual operator-valued Bochner
integrals. Probability kernels and normalized updates are derived from these
operators, whole-cone positivity almost everywhere, and exact integrated mass. -/
set_option autoImplicit false
namespace Komorebi.LSM.ContinuousInstrument
open MeasureTheory ProbabilityTheory
open scoped ENNReal
variable {E A Y : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E]
variable [FiniteDimensional ℝ E] [MeasurableSpace E] [BorelSpace E]
variable [MeasurableSpace Y]

noncomputable def massCLM (C : BaseNorm.ProbabilityCone E) : E →L[ℝ] ℝ :=
  C.mass.toContinuousLinearMap

/-- Input assumptions concern the literal operator density. In particular,
positivity holds on the entire cone outside one null set per action. -/
structure DensityInstrument (C : BaseNorm.ProbabilityCone E) (μ : Measure Y) where
  op : A → Y → E →L[ℝ] E
  measurable_op : ∀ a,Measurable (op a)
  integrable_op : ∀ a,Integrable (op a) μ
  positive : ∀ a,∀ᵐ y∂μ,∀ z∈C.carrier,op a y z∈C.carrier
  mass_preserving : ∀ a z,C.mass ((∫ y,op a y∂μ) z)=C.mass z

namespace DensityInstrument
variable {C : BaseNorm.ProbabilityCone E} {μ : Measure Y}
variable (D : DensityInstrument (A := A) C μ)

noncomputable def density (a : A) (y : Y) (z : E) : ℝ := C.mass (D.op a y z)

omit [FiniteDimensional ℝ E] [MeasurableSpace E] [BorelSpace E] in
theorem applied_integrable (a : A) (z : E) : Integrable (fun y => D.op a y z) μ :=
  (ContinuousLinearMap.apply ℝ E z).integrable_comp (D.integrable_op a)

omit [MeasurableSpace E] [BorelSpace E] in
theorem density_integrable (a : A) (z : E) : Integrable (fun y => D.density a y z) μ :=
  (massCLM C).integrable_comp (D.applied_integrable a z)

omit [FiniteDimensional ℝ E] [MeasurableSpace E] [BorelSpace E] in
theorem density_nonneg_ae (a : A) {z : E} (hz : z∈C.carrier) :
    0≤ᵐ[μ] (fun y => D.density a y z) := by
  filter_upwards [D.positive a] with y hy
  exact C.mass_nonneg (hy z hz)

omit [MeasurableSpace E] [BorelSpace E] in
theorem integral_density (a : A) (z : E) : (∫ y,D.density a y z∂μ)=C.mass z := by
  change (∫ y,massCLM C (D.op a y z)∂μ)=C.mass z
  rw [(massCLM C).integral_comp_comm (D.applied_integrable a z)]
  rw [← ContinuousLinearMap.integral_apply (D.integrable_op a) z]
  exact D.mass_preserving a z

theorem density_measurable (a : A) :
    Measurable (fun p : E × Y => D.density a p.2 p.1) := by
  change Measurable (fun p : E × Y => massCLM C (D.op a p.2 p.1))
  apply (massCLM C).continuous.measurable.comp
  exact (isBoundedBilinearMap_apply (𝕜 := ℝ) (E := E) (F := E)).continuous.measurable.comp
    (((D.measurable_op a).comp measurable_snd).prodMk measurable_fst)

/-- The normalized state space carries the induced measurable structure. -/
abbrev State (C : BaseNorm.ProbabilityCone E) := {z : E // z∈C.base}

noncomputable def kernel [IsProbabilityMeasure μ] (a : A) : Kernel (State C) Y :=
  (Kernel.const (State C) μ).withDensity (fun z y => ENNReal.ofReal (D.density a y z.1))

theorem kernel_density_measurable (a : A) :
    Measurable (Function.uncurry (fun (z : State C) y => ENNReal.ofReal (D.density a y z.1))) := by
  exact (D.density_measurable a |>.comp (measurable_subtype_coe.prodMap measurable_id)).ennreal_ofReal

theorem kernel_apply [IsProbabilityMeasure μ] (a : A) (z : State C) :
    D.kernel a z=μ.withDensity (fun y => ENNReal.ofReal (D.density a y z.1)) :=
  Kernel.withDensity_apply _ (D.kernel_density_measurable a) z

instance kernel_markov [IsProbabilityMeasure μ] (a : A) : IsMarkovKernel (D.kernel a) := by
  constructor
  intro z
  constructor
  rw [D.kernel_apply a z,withDensity_apply _ MeasurableSet.univ,Measure.restrict_univ,
    ← ofReal_integral_eq_lintegral_ofReal (D.density_integrable a z.1)
      (D.density_nonneg_ae a z.2.1),D.integral_density a z.1,z.2.2]
  exact ENNReal.ofReal_one


theorem kernel_event_real [IsProbabilityMeasure μ] (a : A) (z : State C)
    (S : Set Y) (hS : MeasurableSet S) :
    (D.kernel a z).real S=∫ y in S,D.density a y z.1∂μ := by
  rw [Measure.real,D.kernel_apply a z,withDensity_apply _ hS,
    ← ofReal_integral_eq_lintegral_ofReal (D.density_integrable a z.1).integrableOn
      ((D.density_nonneg_ae a z.2.1).filter_mono (ae_mono Measure.restrict_le_self)),
    ENNReal.toReal_ofReal]
  exact integral_nonneg_of_ae ((D.density_nonneg_ae a z.2.1).filter_mono
    (ae_mono Measure.restrict_le_self))

omit [FiniteDimensional ℝ E] [MeasurableSpace E] [BorelSpace E] in
/-- A measurable common exceptional set is extracted from the whole-cone
almost-everywhere hypothesis, without presuming that an uncountable
intersection of measurable sets is measurable. -/
theorem exists_exceptional (a : A) : ∃ N : Set Y,MeasurableSet N ∧ μ N=0 ∧
    ∀ y∉N,∀ z∈C.carrier,D.op a y z∈C.carrier := by
  have hb : μ {y | ¬∀ z∈C.carrier,D.op a y z∈C.carrier}=0 := ae_iff.mp (D.positive a)
  obtain ⟨N,hsub,hm,hnull⟩ := exists_measurable_superset_of_null hb
  refine ⟨N,hm,hnull,?_⟩
  intro y hy
  by_contra hn
  exact hy (hsub hn)

noncomputable def exceptional (a : A) : Set Y := (D.exists_exceptional a).choose

omit [FiniteDimensional ℝ E] [MeasurableSpace E] [BorelSpace E] in
theorem exceptional_measurable (a : A) : MeasurableSet (D.exceptional a) :=
  (D.exists_exceptional a).choose_spec.1

omit [FiniteDimensional ℝ E] [MeasurableSpace E] [BorelSpace E] in
theorem exceptional_null (a : A) : μ (D.exceptional a)=0 :=
  (D.exists_exceptional a).choose_spec.2.1

omit [FiniteDimensional ℝ E] [MeasurableSpace E] [BorelSpace E] in
theorem positive_off_exceptional (a : A) (y : Y) (hy : y∉D.exceptional a)
    {z : E} (hz : z∈C.carrier) : D.op a y z∈C.carrier :=
  (D.exists_exceptional a).choose_spec.2.2 y hy z hz

noncomputable def updateValue (fallback : State C) (a : A) (z : State C) (y : Y) : E := by
  classical
  exact if y∉D.exceptional a ∧ 0<D.density a y z.1 then
    (D.density a y z.1)⁻¹ • D.op a y z.1 else fallback.1

omit [FiniteDimensional ℝ E] [MeasurableSpace E] [BorelSpace E] in
theorem updateValue_mem (fallback : State C) (a : A) (z : State C) (y : Y) :
    D.updateValue fallback a z y∈C.base := by
  classical
  unfold updateValue
  split_ifs with h
  · refine ⟨C.smul_mem (inv_nonneg.mpr h.2.le)
      (D.positive_off_exceptional a y h.1 z.2.1),?_⟩
    rw [map_smul,smul_eq_mul]
    exact inv_mul_cancel₀ h.2.ne'
  · exact fallback.2

/-- A fixed valid state fills null-set and zero-density branches. -/
noncomputable def update (fallback : State C) (a : A) (z : State C) (y : Y) : State C :=
  ⟨D.updateValue fallback a z y,D.updateValue_mem fallback a z y⟩

theorem update_measurable (fallback : State C) (a : A) :
    Measurable (Function.uncurry (D.update fallback a)) := by
  have hd : Measurable (fun p : State C × Y => D.density a p.2 p.1.1) :=
    (D.density_measurable a).comp (measurable_subtype_coe.prodMap measurable_id)
  have hp : Measurable (fun p : State C × Y => D.op a p.2 p.1.1) :=
    (isBoundedBilinearMap_apply (𝕜 := ℝ) (E := E) (F := E)).continuous.measurable.comp
      (((D.measurable_op a).comp measurable_snd).prodMk
        (measurable_subtype_coe.comp measurable_fst))
  have hg : MeasurableSet {p : State C × Y | p.2∉D.exceptional a ∧ 0<D.density a p.2 p.1.1} :=
    ((D.exceptional_measurable a).compl.preimage measurable_snd).inter
      (measurableSet_lt measurable_const hd)
  have hm : Measurable (fun p : State C × Y => D.updateValue fallback a p.1 p.2) :=
    (hd.inv.smul hp).ite hg measurable_const
  exact hm.subtype_mk

omit [FiniteDimensional ℝ E] [MeasurableSpace E] [BorelSpace E] in
theorem update_eq_ae (fallback : State C) (a : A) (z : State C) :
    ∀ᵐ y∂μ,0<D.density a y z.1 →
      (D.update fallback a z y).1=(D.density a y z.1)⁻¹ • D.op a y z.1 := by
  have hN : ∀ᵐ y∂μ,y∉D.exceptional a := by
    exact ae_iff.mpr (by simpa using D.exceptional_null a)
  filter_upwards [hN] with y hy hp
  exact ite_eq_left ⟨hy,hp⟩

omit [FiniteDimensional ℝ E] [MeasurableSpace E] [BorelSpace E] in
/-- Density times the updated state is the unnormalized branch, including the
zero-density case. Strict positivity of cone mass makes that branch zero. -/
theorem density_smul_update (fallback : State C) (a : A) (z : State C) (y : Y)
    (hy : y∉D.exceptional a) :
    D.density a y z.1 • (D.update fallback a z y).1=D.op a y z.1 := by
  have hc := D.positive_off_exceptional a y hy z.2.1
  by_cases hp : 0<D.density a y z.1
  · change D.density a y z.1 • D.updateValue fallback a z y=_
    rw [updateValue,ite_eq_left ⟨hy,hp⟩,smul_smul,mul_inv_cancel₀ hp.ne',one_smul]
  · have hz : D.density a y z.1=0 :=
      le_antisymm (le_of_not_gt hp) (C.mass_nonneg hc)
    have ho : D.op a y z.1=0 := (C.mass_zero_iff hc).mp hz
    rw [hz,zero_smul,ho]

omit [FiniteDimensional ℝ E] [MeasurableSpace E] [BorelSpace E] in
theorem density_smul_update_ae (fallback : State C) (a : A) (z : State C) :
    ∀ᵐ y∂μ,D.density a y z.1 • (D.update fallback a z y).1=D.op a y z.1 := by
  have hN : ∀ᵐ y∂μ,y∉D.exceptional a :=
    ae_iff.mpr (by simpa using D.exceptional_null a)
  exact hN.mono (fun y hy => D.density_smul_update fallback a z y hy)

end DensityInstrument
end Komorebi.LSM.ContinuousInstrument
