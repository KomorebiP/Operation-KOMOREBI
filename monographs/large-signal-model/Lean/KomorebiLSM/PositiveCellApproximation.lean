import KomorebiLSM.ContinuousBins
import KomorebiLSM.BaseNormIntegration
import KomorebiLSM.CellDistance
import Mathlib.MeasureTheory.Integral.Prod

/-! P58: positive approximations are literal normalized Bochner cell averages.
The approximation, its exact event operators, and its resolution error all use
one actual reference measure and the positive-decomposition base norm. -/
set_option autoImplicit false
namespace Komorebi.LSM.PositiveCellApproximation
open MeasureTheory ContinuousInstrument ContinuousBins
open scoped BigOperators
variable {E A Y I : Type*} [MeasurableSpace Y] [Fintype I]

/-- A finite partition modulo a reference null set, with positive cell masses.
This includes literal partitions and interval partitions of a supported measure. -/
structure CellPartition (μ : Measure Y) (I : Type*) [Fintype I] where
  cell : I → Set Y
  measurable : ∀ i,MeasurableSet (cell i)
  disjoint : Pairwise (fun i j => Disjoint (cell i) (cell j))
  cover : ∀ᵐ y∂μ,∃ i,y∈cell i
  mass_positive : ∀ i,0<μ.real (cell i)

namespace CellPartition
variable {μ : Measure Y} (P : CellPartition μ I)

theorem restrict_union : μ.restrict (⋃ i,P.cell i)=μ :=
  Measure.restrict_eq_self_of_ae_mem (by simpa only [Set.mem_iUnion] using P.cover)

theorem total_mass [IsProbabilityMeasure μ] : ∑ i,μ.real (P.cell i)=1 := by
  rw [← measureReal_iUnion_fintype P.disjoint P.measurable]
  have h := congrArg (fun ν : Measure Y => ν.real Set.univ) P.restrict_union
  simpa using h

theorem integral_partition {F : Type*} [NormedAddCommGroup F] [NormedSpace ℝ F]
    (f : Y → F) (hf : Integrable f μ) :
    (∫ y,f y∂μ)=∑ i,∫ y in P.cell i,f y∂μ := by
  rw [← integral_iUnion_fintype P.measurable P.disjoint (fun _ => hf.integrableOn),P.restrict_union]

end CellPartition

variable [NormedAddCommGroup E] [NormedSpace ℝ E] [FiniteDimensional ℝ E]
variable [MeasurableSpace E] [BorelSpace E]
variable {C : BaseNorm.ProbabilityCone E} {μ : Measure Y} [IsProbabilityMeasure μ]
/-- The induced norm is the actual supremum over the unit ball of the
positive-decomposition base norm. -/
noncomputable def inducedNorm (T : E →L[ℝ] E) : ℝ :=
  sSup {r | ∃ z : E,C.value z≤1 ∧ r=C.value (T z)}

omit [MeasurableSpace E] [BorelSpace E] in
theorem inducedNorm_bdd (T : E →L[ℝ] E) :
    BddAbove {r | ∃ z : E,C.value z≤1 ∧ r=C.value (T z)} := by
  obtain ⟨K,hK,hKv⟩ := C.value_le_const_mul_norm
  obtain ⟨R,hR,hRv⟩ := C.exists_norm_le_value
  refine ⟨K*(‖T‖*R),?_⟩
  rintro r ⟨z,hz,rfl⟩
  calc
    C.value (T z) ≤ K*‖T z‖ := hKv _
    _ ≤ K*(‖T‖*‖z‖) := mul_le_mul_of_nonneg_left (T.le_opNorm z) hK.le
    _ ≤ K*(‖T‖*(R*C.value z)) :=
      mul_le_mul_of_nonneg_left (mul_le_mul_of_nonneg_left (hRv z) (norm_nonneg T)) hK.le
    _ ≤ K*(‖T‖*(R*1)) :=
      mul_le_mul_of_nonneg_left (mul_le_mul_of_nonneg_left
        (mul_le_mul_of_nonneg_left hz hR.le) (norm_nonneg T)) hK.le
    _ = _ := by rw [mul_one]

omit [MeasurableSpace E] [BorelSpace E] in
theorem inducedNorm_nonneg (T : E →L[ℝ] E) : 0≤ inducedNorm (C := C) T := by
  apply le_csSup (inducedNorm_bdd T)
  exact ⟨0,by simp,by simp⟩

omit [MeasurableSpace E] [BorelSpace E] in
/-- The supremum genuinely controls every input by homogeneity. -/
theorem value_apply_le_inducedNorm (T : E →L[ℝ] E) (z : E) :
    C.value (T z)≤ inducedNorm (C := C) T*C.value z := by
  by_cases hz : z=0
  · simp [hz]
  have hp : 0<C.value z := lt_of_le_of_ne (C.value_nonneg z)
    (Ne.symm (fun h => hz ((C.value_eq_zero_iff z).mp h)))
  let x := (C.value z)⁻¹ • z
  have hx : C.value x≤1 := by
    change C.value ((C.value z)⁻¹ • z)≤1
    rw [C.value_smul_of_nonneg (inv_nonneg.mpr hp.le),inv_mul_cancel₀ hp.ne']
  have hb : C.value (T x)≤ inducedNorm (C := C) T :=
    le_csSup (inducedNorm_bdd T) ⟨x,hx,rfl⟩
  have he : z=C.value z • x := by simp [x,smul_smul,hp.ne']
  calc
    C.value (T z)=C.value z*C.value (T x) := by
      conv_lhs => rw [he,map_smul,C.value_smul_of_nonneg hp.le]
    _ ≤ C.value z*inducedNorm (C := C) T := mul_le_mul_of_nonneg_left hb hp.le
    _ = _ := mul_comm _ _

variable (D : DensityInstrument (A := A) C μ) (P : CellPartition μ I)

/-- Normalization is by the positive reference mass of the actual cell. -/
noncomputable def cellAverage (a : A) (i : I) : E →L[ℝ] E :=
  (μ.real (P.cell i))⁻¹ • cellOperator μ (D.op a) (P.cell i)

/-- The lifted density is constant on each cell and zero on the exceptional
uncovered null set. No representative point is substituted for the integral. -/
noncomputable def operator (a : A) (y : Y) : E →L[ℝ] E :=
  ∑ i,(P.cell i).indicator (fun _ => cellAverage D P a i) y

omit [MeasurableSpace E] [BorelSpace E] [FiniteDimensional ℝ E] [IsProbabilityMeasure μ] in
theorem operator_on_cell (a : A) (i : I) {y : Y} (hy : y∈P.cell i) :
    operator D P a y=cellAverage D P a i := by
  classical
  unfold operator
  rw [Finset.sum_eq_single i]
  · exact Set.indicator_of_mem hy _
  · intro j _ hji
    have hj : y∉P.cell j := fun hj => Set.disjoint_left.mp (P.disjoint hji) hj hy
    exact Set.indicator_of_notMem hj _
  · simp

omit [MeasurableSpace E] [BorelSpace E] in
theorem cellAverage_positive (a : A) (i : I) {z : E} (hz : z∈C.carrier) :
    cellAverage D P a i z∈C.carrier :=
  C.smul_mem (inv_nonneg.mpr (P.mass_positive i).le)
    (cellOperator_positive C μ (D.op a) (D.integrable_op a) (D.positive a)
      (P.cell i) (P.measurable i) z hz)

omit [MeasurableSpace E] [BorelSpace E] in
theorem operator_positive (a : A) (y : Y) {z : E} (hz : z∈C.carrier) :
    operator D P a y z∈C.carrier := by
  classical
  by_cases hy : ∃ i,y∈P.cell i
  · obtain ⟨i,hi⟩ := hy
    rw [operator_on_cell D P a i hi]
    exact cellAverage_positive D P a i hz
  · have ho : operator D P a y=0 := by
      apply Finset.sum_eq_zero
      intro i _
      exact Set.indicator_of_notMem (fun hi => hy ⟨i,hi⟩) _
    rw [ho]
    exact C.zero_mem

omit [MeasurableSpace E] [BorelSpace E] [IsProbabilityMeasure μ] in
theorem operator_measurable (a : A) : Measurable (operator D P a) :=
  Finset.measurable_fun_sum _ (fun i _ => measurable_const.indicator (P.measurable i))

omit [MeasurableSpace E] [BorelSpace E] [FiniteDimensional ℝ E] in
theorem operator_integrable (a : A) : Integrable (operator D P a) μ := by
  have hi (i : I) : Integrable ((P.cell i).indicator (fun _ : Y => cellAverage D P a i)) μ :=
    (integrable_const (μ := μ) (cellAverage D P a i)).indicator (P.measurable i)
  exact integrable_finsetSum (f := fun i => (P.cell i).indicator
    (fun _ : Y => cellAverage D P a i)) Finset.univ (fun i _ => hi i)

omit [MeasurableSpace E] [BorelSpace E] [IsProbabilityMeasure μ] in
/-- Every cell event operator agrees exactly, despite changing fine densities. -/
theorem exact_cell_operator (a : A) (i : I) :
    cellOperator μ (operator D P a) (P.cell i)=cellOperator μ (D.op a) (P.cell i) := by
  unfold cellOperator
  rw [setIntegral_congr_fun (P.measurable i) (fun y hy => operator_on_cell D P a i hy),setIntegral_const]
  change μ.real (P.cell i) • ((μ.real (P.cell i))⁻¹ • _)=_
  rw [smul_smul,mul_inv_cancel₀ (P.mass_positive i).ne',one_smul]
  rfl

omit [MeasurableSpace E] [BorelSpace E] in
theorem integral_operator (a : A) :
    (∫ y,operator D P a y∂μ)=∫ y,D.op a y∂μ := by
  rw [P.integral_partition _ (operator_integrable D P a),P.integral_partition _ (D.integrable_op a)]
  apply Finset.sum_congr rfl
  intro i _
  exact exact_cell_operator D P a i

/-- Positivity, measurability, integrability and exact integrated mass are
proved for the actual lifted cell average. -/
noncomputable def instrument : DensityInstrument (A := A) C μ where
  op := operator D P
  measurable_op := operator_measurable D P
  integrable_op := operator_integrable D P
  positive a := Filter.Eventually.of_forall (fun y z hz => operator_positive D P a y hz)
  mass_preserving a z := by rw [integral_operator D P a];exact D.mass_preserving a z

omit [MeasurableSpace E] [BorelSpace E] in
/-- Subtracting the true cell average is an actual integral of differences. -/
theorem difference_eq_average (a : A) (i : I) (y : Y) (z : E) :
    D.op a y z-cellAverage D P a i z=
      (μ.real (P.cell i))⁻¹ • ∫ v in P.cell i,D.op a y z-D.op a v z∂μ := by
  rw [integral_sub (integrable_const _).integrableOn (D.applied_integrable a z).integrableOn,
    setIntegral_const]
  rw [smul_sub,smul_smul,inv_mul_cancel₀ (P.mass_positive i).ne',one_smul]
  rw [cellAverage,smul_apply,
    cellOperator_apply μ (D.op a) (D.integrable_op a) (P.cell i) z]

omit [MeasurableSpace E] [BorelSpace E] in
theorem discrepancy_integrable (a : A) (z : E) :
    Integrable (fun y => C.value ((D.op a y-operator D P a y) z)) μ := by
  exact C.integrable_value ((D.applied_integrable a z).sub
    ((ContinuousLinearMap.apply ℝ E z).integrable_comp (operator_integrable D P a)))

/-- Actual integrated base-norm discrepancy for an action and input state. -/
noncomputable def discrepancy (a : A) (z : E) : ℝ :=
  ∫ y,C.value ((D.op a y-operator D P a y) z)∂μ

/-- The supremum over normalized states/actions, with the harmless zero
included to give value zero when that index set is empty. -/
noncomputable def approximationError : ℝ :=
  sSup (insert 0 {r | ∃ a z,z∈C.base ∧ r=discrepancy D P a z})

variable [PseudoMetricSpace Y] [BorelSpace Y]

/-- The source induced-norm Lipschitz assumption, restricted only to pairs
inside the same cells where averaging actually uses it. -/
def CellLipschitz (L : ℝ) : Prop := ∀ a i,∀ y∈P.cell i,∀ v∈P.cell i,
  inducedNorm (C := C) (D.op a y-D.op a v)≤L*dist y v

/-- Operational form of every cell having diameter at most h. -/
def CellDiameter (h : ℝ) : Prop := ∀ i,∀ y∈P.cell i,∀ v∈P.cell i,dist y v≤h

omit [MeasurableSpace E] [BorelSpace E] in
theorem distance_integrable_cell {h : ℝ} (hd : CellDiameter P h)
    (i : I) (y : Y) (hy : y∈P.cell i) :
    IntegrableOn (fun v => dist y v) (P.cell i) μ := by
  have hm : AEStronglyMeasurable (fun v : Y => dist y v) (μ.restrict (P.cell i)) :=
    (continuous_const.dist continuous_id).measurable.aestronglyMeasurable
  apply (integrable_const h).mono' hm
  filter_upwards [ae_restrict_mem (P.measurable i)] with v hv
  rw [Real.norm_eq_abs,abs_of_nonneg dist_nonneg]
  exact hd i y hy v hv

omit [MeasurableSpace E] [BorelSpace E] in
/-- The averaging inequality is derived from the genuine integral triangle
inequality and the induced operator norm, not imposed as a certificate field. -/
theorem point_error_pair_bound {L h : ℝ} (hl : CellLipschitz D P L)
    (hd : CellDiameter P h) (a : A) (i : I) (y : Y) (hy : y∈P.cell i)
    (z : E) (hz : z∈C.base) :
    C.value (D.op a y z-cellAverage D P a i z)≤
      (μ.real (P.cell i))⁻¹*L*(∫ v in P.cell i,dist y v∂μ) := by
  have hf : Integrable (fun v => D.op a y z-D.op a v z) (μ.restrict (P.cell i)) :=
    ((integrable_const _).sub (D.applied_integrable a z)).integrableOn
  have hv : C.value z=1 := (C.value_on_cone hz.1).trans hz.2
  have hb : (∫ v in P.cell i,C.value (D.op a y z-D.op a v z)∂μ)≤
      ∫ v in P.cell i,L*dist y v∂μ := by
    apply integral_mono_ae (C.integrable_value hf) ((distance_integrable_cell P hd i y hy).const_mul L)
    filter_upwards [ae_restrict_mem (P.measurable i)] with v hv'
    have ha := value_apply_le_inducedNorm (C := C) (D.op a y-D.op a v) z
    rw [hv,mul_one] at ha
    exact ha.trans (hl a i y hy v hv')
  rw [difference_eq_average D P a i y z,C.value_smul_of_nonneg
    (inv_nonneg.mpr (P.mass_positive i).le)]
  calc
    _ ≤ (μ.real (P.cell i))⁻¹*(∫ v in P.cell i,C.value (D.op a y z-D.op a v z)∂μ) :=
      mul_le_mul_of_nonneg_left (C.value_integral_le_integral_value hf)
        (inv_nonneg.mpr (P.mass_positive i).le)
    _ ≤ (μ.real (P.cell i))⁻¹*(∫ v in P.cell i,L*dist y v∂μ) :=
      mul_le_mul_of_nonneg_left hb (inv_nonneg.mpr (P.mass_positive i).le)
    _ = _ := by rw [integral_const_mul];ring

end Komorebi.LSM.PositiveCellApproximation
