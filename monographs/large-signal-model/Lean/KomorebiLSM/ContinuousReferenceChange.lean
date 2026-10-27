import KomorebiLSM.ContinuousInstrument

/-! P52 reference changes: the new reference and reciprocal operator density
are constructed explicitly; equality of kernels follows by cancellation. -/
set_option autoImplicit false
namespace Komorebi.LSM.ContinuousInstrument
open MeasureTheory ProbabilityTheory
open scoped ENNReal
variable {E A Y : Type*} [MeasurableSpace Y]

/-- A strictly positive, normalized density for a change of reference. -/
structure ReferenceDensity (μ : Measure Y) where
  weight : Y → ℝ
  measurable_weight : Measurable weight
  positive : ∀ᵐ y∂μ,0<weight y
  integral_one : (∫ y,weight y∂μ)=1

namespace ReferenceDensity
variable {μ : Measure Y} (R : ReferenceDensity μ)

theorem integrable_weight : Integrable R.weight μ := integrable_of_integral_eq_one R.integral_one

noncomputable def measure : Measure Y := μ.withDensity (fun y => ENNReal.ofReal (R.weight y))

instance measure_probability : IsProbabilityMeasure R.measure := by
  constructor
  rw [measure,withDensity_apply _ MeasurableSet.univ,Measure.restrict_univ,
    ← ofReal_integral_eq_lintegral_ofReal R.integrable_weight (R.positive.mono fun _ h => h.le),
    R.integral_one]
  exact ENNReal.ofReal_one

theorem measure_ac : R.measure ≪ μ := withDensity_absolutelyContinuous _ _

theorem original_ac : μ ≪ R.measure :=
  withDensity_absolutelyContinuous' R.measurable_weight.ennreal_ofReal.aemeasurable
    (R.positive.mono fun _ h => by simpa using h)

theorem ae_iff {p : Y → Prop} : (∀ᵐ y∂R.measure,p y) ↔ ∀ᵐ y∂μ,p y :=
  ⟨fun h => R.original_ac.ae_le h,fun h => R.measure_ac.ae_le h⟩

variable [NormedAddCommGroup E] [NormedSpace ℝ E]

/-- Reciprocal-density cancellation is an actual Bochner integral identity,
valid for every integrable vector-valued quantity. -/
theorem integral_reciprocal {F : Type*} [NormedAddCommGroup F] [NormedSpace ℝ F]
    (g : Y → F) :
    (∫ y,(R.weight y)⁻¹ • g y∂R.measure)=∫ y,g y∂μ := by
  rw [measure,integral_withDensity_eq_integral_toReal_smul R.measurable_weight.ennreal_ofReal
    (ae_of_all _ fun y => ENNReal.ofReal_lt_top)]
  apply integral_congr_ae
  filter_upwards [R.positive] with y hy
  rw [ENNReal.toReal_ofReal hy.le,smul_smul,mul_inv_cancel₀ hy.ne',one_smul]

theorem integrable_reciprocal {F : Type*} [NormedAddCommGroup F] [NormedSpace ℝ F]
    {g : Y → F} (hg : Integrable g μ) :
    Integrable (fun y => (R.weight y)⁻¹ • g y) R.measure := by
  rw [measure,integrable_withDensity_iff_integrable_smul' R.measurable_weight.ennreal_ofReal
    (ae_of_all _ fun y => ENNReal.ofReal_lt_top)]
  apply hg.congr
  filter_upwards [R.positive] with y hy
  rw [ENNReal.toReal_ofReal hy.le,smul_smul,mul_inv_cancel₀ hy.ne',one_smul]

end ReferenceDensity

namespace DensityInstrument
variable [NormedAddCommGroup E] [NormedSpace ℝ E] [FiniteDimensional ℝ E]
variable [MeasurableSpace E] [BorelSpace E]
variable {C : BaseNorm.ProbabilityCone E} {μ : Measure Y}
variable (D : DensityInstrument (A := A) C μ) (R : ReferenceDensity μ)

/-- The changed operator is B/r against the changed reference r μ. -/
noncomputable def reweighted : DensityInstrument (A := A) C R.measure where
  op a y := (R.weight y)⁻¹ • D.op a y
  measurable_op a := R.measurable_weight.inv.smul (D.measurable_op a)
  integrable_op a := R.integrable_reciprocal (D.integrable_op a)
  positive a := by
    apply R.ae_iff.mpr
    filter_upwards [R.positive,D.positive a] with y hy hp
    intro z hz
    exact C.smul_mem (inv_nonneg.mpr hy.le) (hp z hz)
  mass_preserving a z := by
    rw [R.integral_reciprocal]
    exact D.mass_preserving a z

omit [MeasurableSpace E] [BorelSpace E] in
theorem reweighted_density (a : A) (y : Y) (z : E) :
    (D.reweighted R).density a y z=(R.weight y)⁻¹*D.density a y z := by
  exact map_smul C.mass (R.weight y)⁻¹ (D.op a y z)


/-- The changed reference and changed density define exactly the same kernel. -/
theorem reweighted_kernel [IsProbabilityMeasure μ] (a : A) :
    (D.reweighted R).kernel a=D.kernel a := by
  apply DFunLike.ext
  intro z
  rw [(D.reweighted R).kernel_apply a z,D.kernel_apply a z]
  have hg : Measurable (fun y => ENNReal.ofReal ((D.reweighted R).density a y z.1)) :=
    (((D.reweighted R).density_measurable a).comp
      (measurable_const.prodMk measurable_id)).ennreal_ofReal
  change (μ.withDensity (fun y => ENNReal.ofReal (R.weight y))).withDensity
    (fun y => ENNReal.ofReal ((D.reweighted R).density a y z.1))=
      μ.withDensity (fun y => ENNReal.ofReal (D.density a y z.1))
  rw [← withDensity_mul μ R.measurable_weight.ennreal_ofReal hg]
  apply withDensity_congr_ae
  filter_upwards [R.positive] with y hy
  change ENNReal.ofReal (R.weight y)*ENNReal.ofReal ((D.reweighted R).density a y z.1)=_
  rw [← ENNReal.ofReal_mul hy.le,D.reweighted_density R a y z.1]
  congr 1
  rw [← mul_assoc,mul_inv_cancel₀ hy.ne',one_mul]

omit [MeasurableSpace E] [BorelSpace E] in
/-- Reciprocal rescaling cancels inside every normalized positive-density update. -/
theorem reweighted_normalized (a : A) (y : Y) (z : E) (hy : 0<R.weight y) :
    ((D.reweighted R).density a y z)⁻¹ • (D.reweighted R).op a y z=
      (D.density a y z)⁻¹ • D.op a y z := by
  rw [D.reweighted_density R a y z]
  change ((R.weight y)⁻¹*D.density a y z)⁻¹ • ((R.weight y)⁻¹ • D.op a y z)=_
  rw [smul_smul,mul_inv_rev,inv_inv,mul_assoc,mul_inv_cancel₀ hy.ne',mul_one]

omit [MeasurableSpace E] [BorelSpace E] in
/-- With the same fixed fallback, measurable update versions agree almost
surely under either equivalent reference measure. -/
theorem reweighted_update_ae (fallback : State C) (a : A) (z : State C) :
    ∀ᵐ y∂μ,(D.reweighted R).update fallback a z y=D.update fallback a z y := by
  have hN : ∀ᵐ y∂μ,y∉D.exceptional a :=
    ae_iff.mpr (by simpa using D.exceptional_null a)
  have hN' : ∀ᵐ y∂μ,y∉(D.reweighted R).exceptional a :=
    R.ae_iff.mp (ae_iff.mpr (by simpa using (D.reweighted R).exceptional_null a))
  filter_upwards [R.positive,hN,hN'] with y hy hN hN'
  have hp : 0<(D.reweighted R).density a y z.1 ↔ 0<D.density a y z.1 := by
    rw [D.reweighted_density R a y z.1]
    exact mul_pos_iff_of_pos_left (inv_pos.mpr hy)
  apply Subtype.ext
  change (D.reweighted R).updateValue fallback a z y=D.updateValue fallback a z y
  unfold updateValue
  simp only [hN,hN',not_false_eq_true,true_and,hp]
  split_ifs
  · exact D.reweighted_normalized R a y z.1 hy
  · rfl

theorem reweighted_event [IsProbabilityMeasure μ] (a : A) (z : State C) (S : Set Y) :
    ((D.reweighted R).kernel a z).real S=(D.kernel a z).real S := by
  rw [D.reweighted_kernel R a]

omit [MeasurableSpace E] [BorelSpace E] in
theorem reweighted_update_ae_changed (fallback : State C) (a : A) (z : State C) :
    ∀ᵐ y∂R.measure,(D.reweighted R).update fallback a z y=D.update fallback a z y :=
  R.ae_iff.mpr (D.reweighted_update_ae R fallback a z)

end DensityInstrument
end Komorebi.LSM.ContinuousInstrument
