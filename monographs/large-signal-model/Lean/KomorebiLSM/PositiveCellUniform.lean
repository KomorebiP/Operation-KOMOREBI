import KomorebiLSM.PositiveCellResolution

/-! The sharper P58 bound uses actual double-distance integrals in the fixed
uniform reference on [-1,1], not a postulated numerical averaging constant. -/
set_option autoImplicit false
namespace Komorebi.LSM.PositiveCellApproximation
open MeasureTheory ContinuousInstrument ContinuousBins
open scoped BigOperators
variable {I : Type*} [Fintype I]
variable (P : CellPartition UniformIntervalMoments.measure I)

noncomputable def cellDistance (i : I) (y : ℝ) : ℝ :=
  ∫ v in P.cell i,dist y v∂UniformIntervalMoments.measure

noncomputable def resolution : ℝ :=
  ∑ i,(UniformIntervalMoments.measure.real (P.cell i))⁻¹*
    ∫ y in P.cell i,cellDistance P i y∂UniformIntervalMoments.measure

theorem cellDistance_nonneg (i : I) (y : ℝ) : 0≤cellDistance P i y :=
  integral_nonneg (fun _ => dist_nonneg)

theorem cellDistance_stronglyMeasurable (i : I) : StronglyMeasurable (cellDistance P i) := by
  have hm : StronglyMeasurable (fun p : ℝ × ℝ => dist p.1 p.2) :=
    (continuous_fst.dist continuous_snd).stronglyMeasurable
  exact hm.integral_prod_right

theorem cellDistance_le {h : ℝ} (hd : CellDiameter P h)
    (i : I) (y : ℝ) (hy : y∈P.cell i) :
    cellDistance P i y≤UniformIntervalMoments.measure.real (P.cell i)*h := by
  calc
    _ ≤ ∫ _ in P.cell i,h∂UniformIntervalMoments.measure := by
      apply integral_mono_ae (distance_integrable_cell P hd i y hy) (integrable_const h)
      filter_upwards [ae_restrict_mem (P.measurable i)] with v hv
      exact hd i y hy v hv
    _ = _ := by rw [setIntegral_const,smul_eq_mul]

theorem cellDistance_integrable {h : ℝ} (hd : CellDiameter P h) (i : I) :
    IntegrableOn (cellDistance P i) (P.cell i) UniformIntervalMoments.measure := by
  apply (integrable_const (UniformIntervalMoments.measure.real (P.cell i)*h)).mono'
    (cellDistance_stronglyMeasurable P i).aestronglyMeasurable
  filter_upwards [ae_restrict_mem (P.measurable i)] with y hy
  rw [Real.norm_eq_abs,abs_of_nonneg (cellDistance_nonneg P i y)]
  exact cellDistance_le P hd i y hy

/-- The factor h/3 is calculated from the actual uniform cell measure. -/
theorem resolution_equal_intervals (a b : I → ℝ) (h : ℝ) (hh : 0<h)
    (hc : ∀ i,P.cell i=Set.Ioc (a i) (b i))
    (ha : ∀ i,-1≤a i) (hb : ∀ i,b i≤1) (hw : ∀ i,b i-a i=h) :
    resolution P=h/3 := by
  have hab (i : I) : a i<b i := by linarith [hw i]
  have hm (i : I) : UniformIntervalMoments.measure.real (P.cell i)=h/2 := by
    rw [hc i,CellDistance.uniform_cell_mass (a i) (b i) (ha i) (hb i) (hab i).le,hw i]
  have hd (i : I) : (∫ y in P.cell i,cellDistance P i y∂UniformIntervalMoments.measure)=h^3/12 := by
    unfold cellDistance
    simp only [hc i]
    rw [CellDistance.uniform_cell_double_distance (a i) (b i) (ha i) (hb i) (hab i).le,hw i]
  calc
    resolution P=∑ i,UniformIntervalMoments.measure.real (P.cell i)*h/3 := by
      unfold resolution
      apply Finset.sum_congr rfl
      intro i _
      rw [hm i,hd i]
      field_simp [hh.ne']; ring
    _ = (∑ i,UniformIntervalMoments.measure.real (P.cell i))*h/3 := by
      simp only [div_eq_mul_inv,Finset.sum_mul]
    _ = h/3 := by rw [P.total_mass,one_mul]

theorem diameter_equal_intervals (a b : I → ℝ) (h : ℝ)
    (hc : ∀ i,P.cell i=Set.Ioc (a i) (b i)) (hw : ∀ i,b i-a i=h) :
    CellDiameter P h := by
  intro i y hy v hv
  rw [hc i] at hy hv
  rw [Real.dist_eq]
  apply abs_le.mpr
  constructor <;> linarith [hw i,hy.1,hy.2,hv.1,hv.2]

variable {E A : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E]
variable [FiniteDimensional ℝ E] [MeasurableSpace E] [BorelSpace E]
variable {C : BaseNorm.ProbabilityCone E}
variable (D : DensityInstrument (A := A) C UniformIntervalMoments.measure)

omit [MeasurableSpace E] [BorelSpace E] in
theorem cell_error_pair_integral {L h : ℝ} (hl : CellLipschitz D P L) (hd : CellDiameter P h)
    (a : A) (i : I) (z : E) (hz : z∈C.base) :
    (∫ y in P.cell i,C.value ((D.op a y-operator D P a y) z)∂UniformIntervalMoments.measure)≤
      (UniformIntervalMoments.measure.real (P.cell i))⁻¹*L*
        (∫ y in P.cell i,cellDistance P i y∂UniformIntervalMoments.measure) := by
  have hb : (∫ y in P.cell i,C.value ((D.op a y-operator D P a y) z)∂UniformIntervalMoments.measure)≤
      ∫ y in P.cell i,(UniformIntervalMoments.measure.real (P.cell i))⁻¹*L*cellDistance P i y
        ∂UniformIntervalMoments.measure := by
    apply integral_mono_ae (discrepancy_integrable D P a z).integrableOn
      ((cellDistance_integrable P hd i).const_mul _)
    filter_upwards [ae_restrict_mem (P.measurable i)] with y hy
    rw [operator_on_cell D P a i hy]
    exact point_error_pair_bound D P hl hd a i y hy z hz
  exact hb.trans_eq (integral_const_mul _ _)

omit [MeasurableSpace E] [BorelSpace E] in
theorem discrepancy_le_resolution {L h : ℝ} (hl : CellLipschitz D P L) (hd : CellDiameter P h)
    (a : A) (z : E) (hz : z∈C.base) : discrepancy D P a z≤L*resolution P := by
  unfold discrepancy
  rw [P.integral_partition _ (discrepancy_integrable D P a z)]
  calc
    _ ≤ ∑ i,(UniformIntervalMoments.measure.real (P.cell i))⁻¹*L*
        (∫ y in P.cell i,cellDistance P i y∂UniformIntervalMoments.measure) :=
      Finset.sum_le_sum (fun i _ => cell_error_pair_integral P D hl hd a i z hz)
    _ = _ := by
      unfold resolution
      rw [Finset.mul_sum]
      apply Finset.sum_congr rfl
      intro i _
      ring

omit [MeasurableSpace E] [BorelSpace E] in
/-- Equal intervals in the actual uniform[-1,1] reference have error Lh/3.
The hypotheses are a genuine interval partition and an induced-norm bound on
the interval; the averaging bound and the factor one third are proved. -/
theorem approximationError_le_equal_intervals (a b : I → ℝ) (h L : ℝ)
    (hh : 0<h) (hL : 0≤L) (hc : ∀ i,P.cell i=Set.Ioc (a i) (b i))
    (ha : ∀ i,-1≤a i) (hb : ∀ i,b i≤1) (hw : ∀ i,b i-a i=h)
    (hl : ∀ a,∀ y∈Set.Icc (-1 : ℝ) 1,∀ v∈Set.Icc (-1 : ℝ) 1,
      inducedNorm (C := C) (D.op a y-D.op a v)≤L*dist y v) :
    approximationError D P≤L*h/3 := by
  have hd := diameter_equal_intervals P a b h hc hw
  have hcell : CellLipschitz D P L := by
    intro act i y hy v hv
    rw [hc i] at hy hv
    exact hl act y ⟨le_trans (ha i) hy.1.le,le_trans hy.2 (hb i)⟩
      v ⟨le_trans (ha i) hv.1.le,le_trans hv.2 (hb i)⟩
  apply approximationError_le D P (div_nonneg (mul_nonneg hL hh.le) (by norm_num))
  intro act z hz
  have he := discrepancy_le_resolution P D hcell hd act z hz
  rw [resolution_equal_intervals P a b h hh hc ha hb hw] at he
  nlinarith

end Komorebi.LSM.PositiveCellApproximation
