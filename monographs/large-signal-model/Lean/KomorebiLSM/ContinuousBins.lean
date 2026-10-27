import KomorebiLSM.InstrumentContraction
import KomorebiLSM.ContinuousInstrument
import KomorebiLSM.PolicyComparison
import Mathlib.Analysis.Convex.Integral
import Mathlib.MeasureTheory.Integral.Bochner.ContinuousLinearMap
import Mathlib.MeasureTheory.Integral.Bochner.Set
import Mathlib.Analysis.Normed.Module.FiniteDimension

/-! P56: exact event-cell operators and the averaged posterior. -/
set_option autoImplicit false
namespace Komorebi.LSM.ContinuousBins
open MeasureTheory
open scoped BigOperators
variable {E Y I : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E]
variable [CompleteSpace E] [MeasurableSpace Y]
variable (C : BaseNorm.ProbabilityCone E) (μ : Measure Y) [IsProbabilityMeasure μ]

noncomputable def cellOperator (B : Y → E →L[ℝ] E) (S : Set Y) : E →L[ℝ] E :=
  ∫ y in S, B y ∂μ

omit [CompleteSpace E] [IsProbabilityMeasure μ] in
theorem cellOperator_apply (B : Y → E →L[ℝ] E) (hB : Integrable B μ)
    (S : Set Y) (z : E) : cellOperator μ B S z = ∫ y in S, B y z ∂μ :=
  ContinuousLinearMap.integral_apply hB.integrableOn z

/-- A measurable event integrates cone-valued outputs to another cone element. -/
theorem setIntegral_mem {f : Y → E} (hf : Integrable f μ) (S : Set Y)
    (hS : MeasurableSet S) (hpos : ∀ᵐ y ∂μ, f y ∈ C.carrier) :
    (∫ y in S, f y ∂μ) ∈ C.carrier := by
  rw [← integral_indicator hS]
  apply C.convex_carrier.integral_mem C.closed ?_ (hf.indicator hS)
  filter_upwards [hpos] with y hy
  by_cases hs : y ∈ S
  · simpa only [Set.indicator_of_mem hs] using hy
  · simpa only [Set.indicator_of_notMem hs] using C.zero_mem

theorem cellOperator_positive (B : Y → E →L[ℝ] E) (hB : Integrable B μ)
    (hpos : ∀ᵐ y ∂μ, ∀ z ∈ C.carrier, B y z ∈ C.carrier)
    (S : Set Y) (hS : MeasurableSet S) (z : E) (hz : z ∈ C.carrier) :
    cellOperator μ B S z ∈ C.carrier := by
  rw [cellOperator_apply μ B hB S z]
  exact setIntegral_mem C μ ((ContinuousLinearMap.apply ℝ E z).integrable_comp hB) S hS
    (hpos.mono fun _ hy => hy z hz)

variable [Fintype I]

omit [CompleteSpace E] [IsProbabilityMeasure μ] in
/-- The sum of exact cell operators is the original integrated operator. -/
theorem cellOperator_sum (B : Y → E →L[ℝ] E) (hB : Integrable B μ)
    (S : I → Set Y) (hS : ∀ i, MeasurableSet (S i))
    (hdis : Pairwise (fun i j => Disjoint (S i) (S j))) (hcover : ⋃ i, S i = Set.univ) :
    ∑ i, cellOperator μ B (S i) = ∫ y, B y ∂μ := by
  symm
  simpa only [hcover,Measure.restrict_univ,cellOperator] using
    (integral_iUnion_fintype hS hdis (fun _ => hB.integrableOn))

/-- Exact integrated mass and event partitioning construct a finite instrument. -/
theorem cellInstrument (B : Y → E →L[ℝ] E) (hB : Integrable B μ)
    (hpos : ∀ᵐ y ∂μ, ∀ z ∈ C.carrier, B y z ∈ C.carrier)
    (hmass : ∀ z, C.mass ((∫ y, B y ∂μ) z)=C.mass z)
    (S : I → Set Y) (hS : ∀ i, MeasurableSet (S i))
    (hdis : Pairwise (fun i j => Disjoint (S i) (S j))) (hcover : ⋃ i, S i = Set.univ) :
    C.Instrument (fun i => (cellOperator μ B (S i)).toLinearMap) := by
  refine ⟨fun i z hz => cellOperator_positive C μ B hB hpos (S i) (hS i) z hz,?_⟩
  intro z
  calc
    ∑ i, C.mass (cellOperator μ B (S i) z) = C.mass ((∑ i, cellOperator μ B (S i)) z) := by
      simp only [_root_.sum_apply,map_sum]
    _ = C.mass ((∫ y, B y ∂μ) z) := by rw [cellOperator_sum μ B hB S hS hdis hcover]
    _ = C.mass z := hmass z

/-- A concrete measurable version may choose any fixed fallback on zero density.
Multiplication by the likelihood removes this arbitrary choice. -/
noncomputable def posterior (B : Y → E →L[ℝ] E) (fallback : E) (z : E) (y : Y) : E :=
  if 0 < C.mass (B y z) then (C.mass (B y z))⁻¹ • B y z else fallback

omit [CompleteSpace E] [MeasurableSpace Y] in
theorem likelihood_smul_posterior (B : Y → E →L[ℝ] E) (fallback z : E) (y : Y)
    (hy : B y z ∈ C.carrier) :
    C.mass (B y z) • posterior C B fallback z y = B y z := by
  by_cases hp : 0 < C.mass (B y z)
  · simp only [posterior,ite_eq_left hp,smul_smul,mul_inv_cancel₀ (ne_of_gt hp),one_smul]
  · have hm : C.mass (B y z)=0 := le_antisymm (le_of_not_gt hp) (C.mass_nonneg hy)
    have hz : B y z=0 := (C.mass_zero_iff hy).mp hm
    simp [posterior,hz]

omit [CompleteSpace E] [IsProbabilityMeasure μ] in
/-- The exact cell posterior is the density-weighted average of the fine
posteriors. A representative observation point does not occur in this formula. -/
theorem cell_posterior_average (B : Y → E →L[ℝ] E) (hB : Integrable B μ)
    (hpos : ∀ᵐ y ∂μ, ∀ z ∈ C.carrier, B y z ∈ C.carrier)
    (S : Set Y) (fallback z : E) (hz : z ∈ C.carrier) :
    (C.mass (cellOperator μ B S z))⁻¹ • cellOperator μ B S z =
      (C.mass (cellOperator μ B S z))⁻¹ •
        ∫ y in S, C.mass (B y z) • posterior C B fallback z y ∂μ := by
  congr 1
  rw [cellOperator_apply μ B hB S z]
  symm
  apply integral_congr_ae
  filter_upwards [ae_restrict_of_ae hpos] with y hy
  exact likelihood_smul_posterior C B fallback z y (hy z hz)

theorem cell_posterior_base (B : Y → E →L[ℝ] E) (hB : Integrable B μ)
    (hpos : ∀ᵐ y ∂μ, ∀ z ∈ C.carrier, B y z ∈ C.carrier)
    (S : Set Y) (hS : MeasurableSet S) (z : E) (hz : z ∈ C.carrier)
    (hp : 0 < C.mass (cellOperator μ B S z)) :
    (C.mass (cellOperator μ B S z))⁻¹ • cellOperator μ B S z ∈ C.base := by
  refine ⟨C.smul_mem (inv_pos.mpr hp).le (cellOperator_positive C μ B hB hpos S hS z hz),?_⟩
  simp only [map_smul,smul_eq_mul,inv_mul_cancel₀ (ne_of_gt hp)]

section Model
variable {A : Type*} [FiniteDimensional ℝ E] [MeasurableSpace E] [BorelSpace E]
variable (D : ContinuousInstrument.DensityInstrument (A := A) C μ)

/-- A cell probability is the literal event probability of the continuous kernel. -/
theorem kernel_cell_probability (a : A) (z : ContinuousInstrument.DensityInstrument.State C)
    (S : Set Y) (hS : MeasurableSet S) :
    (D.kernel a z).real S = C.mass (cellOperator μ (D.op a) S z.1) := by
  rw [D.kernel_event_real a z S hS,cellOperator_apply μ (D.op a) (D.integrable_op a) S z.1]
  exact (ContinuousInstrument.massCLM C).integral_comp_comm (D.applied_integrable a z.1).integrableOn

omit [CompleteSpace E] [IsProbabilityMeasure μ] [FiniteDimensional ℝ E] [MeasurableSpace E] [BorelSpace E] in
/-- The same measurable update used by the instrument, including its fixed
fallback, has the exact density-weighted cell average. -/
theorem kernel_cell_posterior_average (a : A) (fallback z : ContinuousInstrument.DensityInstrument.State C)
    (S : Set Y) :
    (C.mass (cellOperator μ (D.op a) S z.1))⁻¹ • cellOperator μ (D.op a) S z.1 =
      (C.mass (cellOperator μ (D.op a) S z.1))⁻¹ •
        ∫ y in S, D.density a y z.1 • (D.update fallback a z y).1 ∂μ := by
  congr 1
  rw [cellOperator_apply μ (D.op a) (D.integrable_op a) S z.1]
  symm
  apply integral_congr_ae
  filter_upwards [ae_restrict_of_ae (D.positive a),ae_restrict_of_ae (D.update_eq_ae fallback a z)] with y hy hu
  by_cases hp : 0 < D.density a y z.1
  · rw [hu hp,smul_smul,mul_inv_cancel₀ hp.ne',one_smul]
  · have hn : 0 ≤ D.density a y z.1 := C.mass_nonneg (hy z.1 z.2.1)
    have he : D.density a y z.1=0 := le_antisymm (le_of_not_gt hp) hn
    have hz : D.op a y z.1=0 := (C.mass_zero_iff (hy z.1 z.2.1)).mp he
    rw [he,zero_smul,hz]

end Model

section Words
variable {A : Type*}
omit [Fintype I]

/-- The cell history, rather than an unobserved within-cell value, selects each
next operator. Thus this construction permits exactly bin-measurable policies. -/
noncomputable def cellWordMap (B : List (A × I) → A → Y → E →L[ℝ] E)
    (S : I → Set Y) : List (A × I) → List (A × I) → E →L[ℝ] E
  | _, [] => ContinuousLinearMap.id ℝ E
  | h, s::w => (cellWordMap B S (h++[s]) w).comp (cellOperator μ (B h s.1) (S s.2))

/-- Literal chronological repeated integration of the operator density over
the observed cells, with no representative-point substitution. -/
noncomputable def iteratedCellVector (B : List (A × I) → A → Y → E →L[ℝ] E)
    (S : I → Set Y) : List (A × I) → List (A × I) → E → E
  | _, [], z => z
  | h, s::w, z => ∫ y in S s.2, iteratedCellVector B S (h++[s]) w (B h s.1 y z) ∂μ

omit [IsProbabilityMeasure μ] in
theorem iteratedCellVector_eq (B : List (A × I) → A → Y → E →L[ℝ] E)
    (hB : ∀ h a,Integrable (B h a) μ) (S : I → Set Y)
    (h w : List (A × I)) (z : E) :
    iteratedCellVector μ B S h w z=cellWordMap μ B S h w z := by
  induction w generalizing h z with
  | nil => rfl
  | cons s w ih =>
    simp only [iteratedCellVector,cellWordMap,ContinuousLinearMap.comp_apply]
    simp_rw [ih]
    have hint : Integrable (fun y => B h s.1 y z) (μ.restrict (S s.2)) :=
      ((ContinuousLinearMap.apply ℝ E z).integrable_comp (hB h s.1)).integrableOn
    rw [(cellWordMap μ B S (h++[s]) w).integral_comp_comm hint]
    rw [← cellOperator_apply μ (B h s.1) (hB h s.1) (S s.2) z]

omit [CompleteSpace E] [IsProbabilityMeasure μ] in
theorem cellWordMap_recordState (B : List (A × I) → A → Y → E →L[ℝ] E)
    (S : I → Set Y) (n : ℕ) (h : List (A × I)) (z : E)
    (w : ObservationTree.Record (A × I) n) :
    cellWordMap μ B S h (ObservationTree.recordList w) z =
      ObservationTree.recordState
        (fun h s => (cellOperator μ (B h s.1) (S s.2)).toLinearMap) n h z w := by
  induction n generalizing h z with
  | zero => rfl
  | succ n ih =>
    exact ih (h++[w.1]) (cellOperator μ (B h w.1.1) (S w.1.2) z) w.2

omit [IsProbabilityMeasure μ] in
/-- The finite event law has the exact repeated-integral interpretation at
every horizon and every bin history. -/
theorem iterated_cell_record_probability (B : List (A × I) → A → Y → E →L[ℝ] E)
    (hB : ∀ h a,Integrable (B h a) μ) (S : I → Set Y)
    (n : ℕ) (h : List (A × I)) (z : E) (w : ObservationTree.Record (A × I) n) :
    C.mass (iteratedCellVector μ B S h (ObservationTree.recordList w) z) =
      ObservationTree.recordLaw C
        (fun h s => (cellOperator μ (B h s.1) (S s.2)).toLinearMap) n h z w := by
  rw [iteratedCellVector_eq μ B hB S h (ObservationTree.recordList w) z,
    cellWordMap_recordState μ B S n h z w]
  rfl

end Words

end Komorebi.LSM.ContinuousBins
