import KomorebiLSM.PositiveCellApproximation

/-! P58 resolution bounds for the literal positive cell-average density. -/
set_option autoImplicit false
namespace Komorebi.LSM.PositiveCellApproximation
open MeasureTheory ContinuousInstrument ContinuousBins
open scoped BigOperators
variable {E A I : Type*} [Fintype I]
variable [NormedAddCommGroup E] [NormedSpace ℝ E] [FiniteDimensional ℝ E]
variable [MeasurableSpace E] [BorelSpace E]
variable {C : BaseNorm.ProbabilityCone E}

section Metric
variable {Y : Type*} [MeasurableSpace Y] [PseudoMetricSpace Y] [BorelSpace Y]
variable {μ : Measure Y} [IsProbabilityMeasure μ]
variable (D : DensityInstrument (A := A) C μ) (P : CellPartition μ I)

omit [MeasurableSpace E] [BorelSpace E] in
theorem point_error_diameter {L h : ℝ} (hL : 0≤L) (hl : CellLipschitz D P L)
    (hd : CellDiameter P h) (a : A) (i : I) (y : Y) (hy : y∈P.cell i)
    (z : E) (hz : z∈C.base) :
    C.value (D.op a y z-cellAverage D P a i z)≤L*h := by
  have hb : (∫ v in P.cell i,dist y v∂μ)≤μ.real (P.cell i)*h := by
    calc
      _ ≤ ∫ _ in P.cell i,h∂μ := by
        apply integral_mono_ae (distance_integrable_cell P hd i y hy) (integrable_const h)
        filter_upwards [ae_restrict_mem (P.measurable i)] with v hv
        exact hd i y hy v hv
      _ = _ := by rw [setIntegral_const,smul_eq_mul]
  calc
    _ ≤ (μ.real (P.cell i))⁻¹*L*(∫ v in P.cell i,dist y v∂μ) :=
      point_error_pair_bound D P hl hd a i y hy z hz
    _ ≤ (μ.real (P.cell i))⁻¹*L*(μ.real (P.cell i)*h) :=
      mul_le_mul_of_nonneg_left hb (mul_nonneg (inv_nonneg.mpr (P.mass_positive i).le) hL)
    _ = _ := by field_simp [(P.mass_positive i).ne']

omit [MeasurableSpace E] [BorelSpace E] in
/-- Integrating the pointwise diameter estimate uses the actual probability
reference and actual base-norm discrepancy. -/
theorem discrepancy_le_diameter {L h : ℝ} (hL : 0≤L) (hl : CellLipschitz D P L)
    (hd : CellDiameter P h) (a : A) (z : E) (hz : z∈C.base) :
    discrepancy D P a z≤L*h := by
  unfold discrepancy
  calc
    _ ≤ ∫ _ : Y,L*h∂μ := by
      apply integral_mono_ae (discrepancy_integrable D P a z) (integrable_const _)
      filter_upwards [P.cover] with y hy
      obtain ⟨i,hi⟩ := hy
      rw [operator_on_cell D P a i hi]
      exact point_error_diameter D P hL hl hd a i y hi z hz
    _ = _ := by simp

omit [PseudoMetricSpace Y] [BorelSpace Y] [MeasurableSpace E] [BorelSpace E]
  [FiniteDimensional ℝ E] [IsProbabilityMeasure μ] in
theorem approximationError_le {r : ℝ} (hr : 0≤r)
    (hb : ∀ a z,z∈C.base → discrepancy D P a z≤r) : approximationError D P≤r := by
  apply csSup_le ⟨0,Set.mem_insert _ _⟩
  rintro q (rfl | ⟨a,z,hz,rfl⟩)
  · exact hr
  · exact hb a z hz

omit [PseudoMetricSpace Y] [BorelSpace Y] [MeasurableSpace E] [BorelSpace E]
  [FiniteDimensional ℝ E] [IsProbabilityMeasure μ] in
/-- Whenever normalized action/state inputs exist, inserting zero does not
change the ordinary source supremum, since every actual discrepancy is nonnegative. -/
theorem approximationError_eq_sup (hn : ∃ _a : A,∃ z : E,z∈C.base)
    (hb : BddAbove {r | ∃ a z,z∈C.base ∧ r=discrepancy D P a z}) :
    approximationError D P=sSup {r | ∃ a z,z∈C.base ∧ r=discrepancy D P a z} := by
  let S : Set ℝ := {r | ∃ a z,z∈C.base ∧ r=discrepancy D P a z}
  change sSup (insert 0 S)=sSup S
  obtain ⟨a,z,hz⟩ := hn
  have hm : discrepancy D P a z∈S := ⟨a,z,hz,rfl⟩
  have hs : S.Nonempty := ⟨_,hm⟩
  have hnonneg : 0≤sSup S :=
    (integral_nonneg (fun y => C.value_nonneg ((D.op a y-operator D P a y) z))).trans
      (le_csSup hb hm)
  have hb' : BddAbove (insert 0 S) := by
    obtain ⟨r,hr⟩ := hb
    refine ⟨max 0 r,?_⟩
    rintro q (rfl | hq)
    · exact le_max_left _ _
    · exact (hr hq).trans (le_max_right _ _)
  apply le_antisymm
  · apply csSup_le ⟨0,Set.mem_insert _ _⟩
    rintro q (rfl | hq)
    · exact hnonneg
    · exact le_csSup hb hq
  · apply csSup_le hs
    intro q hq
    exact le_csSup hb' (Set.mem_insert_of_mem 0 hq)

omit [MeasurableSpace E] [BorelSpace E] in
/-- The full supremum in P58 is bounded by L times the cell diameter. -/
theorem approximationError_le_diameter {L h : ℝ} (hL : 0≤L) (hh : 0≤h)
    (hl : CellLipschitz D P L) (hd : CellDiameter P h) :
    approximationError D P≤L*h :=
  approximationError_le D P (mul_nonneg hL hh)
    (fun a z hz => discrepancy_le_diameter D P hL hl hd a z hz)

end Metric
end Komorebi.LSM.PositiveCellApproximation
