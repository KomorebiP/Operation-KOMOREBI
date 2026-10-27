import KomorebiLSM.ContinuousRecords
import KomorebiLSM.ContinuousReferenceChange

/-! P52 reference cancellation for actual complete finite record measures,
including arbitrary common measurable randomized policies. -/
set_option autoImplicit false
namespace Komorebi.LSM.ContinuousRecordReference
open MeasureTheory ProbabilityTheory ContinuousInstrument ContinuousRecords
open scoped ENNReal
variable {X : Type*} [MeasurableSpace X]

noncomputable def referenceWeight (f : X → ℝ≥0∞) : (n : ℕ) → History X n → ℝ≥0∞
  | 0, _ => 1
  | n+1, h => referenceWeight f n h.1*f h.2

noncomputable def realWeight (r : X → ℝ) : (n : ℕ) → History X n → ℝ
  | 0, _ => 1
  | n+1, h => realWeight r n h.1*r h.2

theorem referenceWeight_measurable (f : X → ℝ≥0∞) (hf : Measurable f) :
    (n : ℕ) → Measurable (referenceWeight f n)
  | 0 => measurable_const
  | n+1 => ((referenceWeight_measurable f hf n).comp measurable_fst).mul (hf.comp measurable_snd)

theorem realWeight_measurable (r : X → ℝ) (hr : Measurable r) :
    (n : ℕ) → Measurable (realWeight r n)
  | 0 => measurable_const
  | n+1 => ((realWeight_measurable r hr n).comp measurable_fst).mul (hr.comp measurable_snd)

/-- Changing every factor of the actual finite product reference multiplies
its density by the literal product of the reference densities. -/
theorem reference_withDensity (ν : Measure X) [IsFiniteMeasure ν]
    (r : X → ℝ) (hr : Measurable r) : (n : ℕ) →
    reference (ν.withDensity (fun x => ENNReal.ofReal (r x))) n=
      (reference ν n).withDensity (referenceWeight (fun x => ENNReal.ofReal (r x)) n)
  | 0 => by simp [reference,referenceWeight]
  | n+1 => by
    rw [reference,reference,reference_withDensity ν r hr n]
    exact prod_withDensity (referenceWeight_measurable _ hr.ennreal_ofReal n) hr.ennreal_ofReal

/-- All scalar factors are positive on one product-reference full-measure set. -/
theorem weight_valid_ae (ν : Measure X) [IsFiniteMeasure ν]
    (r : X → ℝ) (hr : Measurable r) (hp : ∀ᵐ x∂ν,0<r x) : (n : ℕ) →
    ∀ᵐ h∂reference ν n,
      referenceWeight (fun x => ENNReal.ofReal (r x)) n h=ENNReal.ofReal (realWeight r n h) ∧
        0<realWeight r n h
  | 0 => by simp [referenceWeight,realWeight]
  | n+1 => by
    change ∀ᵐ h∂(reference ν n).prod ν,_
    have hm : MeasurableSet {h : History X (n+1) |
        referenceWeight (fun x => ENNReal.ofReal (r x)) (n+1) h=
          ENNReal.ofReal (realWeight r (n+1) h) ∧ 0<realWeight r (n+1) h} :=
      (measurableSet_eq_fun (referenceWeight_measurable _ hr.ennreal_ofReal (n+1))
        (realWeight_measurable r hr (n+1)).ennreal_ofReal).inter
          (measurableSet_lt measurable_const (realWeight_measurable r hr (n+1)))
    apply (Measure.ae_prod_iff_ae_ae hm).mpr
    filter_upwards [weight_valid_ae ν r hr hp n] with h hh
    filter_upwards [hp] with x hx
    exact ⟨by rw [referenceWeight,realWeight,hh.1,ENNReal.ofReal_mul hh.2.le],mul_pos hh.2 hx⟩

variable {E A Y : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E]
variable [FiniteDimensional ℝ E] [MeasurableSpace E] [BorelSpace E]
variable [MeasurableSpace Y] [MeasurableSpace A] [Fintype A] [MeasurableSingletonClass A]
variable {C : BaseNorm.ProbabilityCone E} {μ : Measure Y}
variable (D : DensityInstrument (A := A) C μ) (R : ReferenceDensity μ)

omit [MeasurableSpace E] [BorelSpace E] [MeasurableSpace A] [Fintype A]
  [MeasurableSingletonClass A] in
/-- The actual operator product carries the reciprocal product reference factor. -/
theorem run_reweighted (z : E) : (n : ℕ) → ∀ h : History (A × Y) n,
    run (D.reweighted R) z n h=
      (realWeight (fun s : A × Y => R.weight s.2) n h)⁻¹ • run D z n h
  | 0, _ => by simp [run,realWeight]
  | n+1, h => by
    change (R.weight h.2.2)⁻¹ • D.op h.2.1 h.2.2 (run (D.reweighted R) z n h.1)=_
    rw [run_reweighted z n h.1]
    simp only [map_smul,smul_smul,realWeight,run,mul_inv_rev]

omit [Fintype A] [MeasurableSingletonClass A] in
theorem stepReference_reweighted [SFinite μ] :
    stepReference (A := A) R.measure=
      (stepReference (A := A) μ).withDensity (fun s => ENNReal.ofReal (R.weight s.2)) := by
  exact prod_withDensity_right R.measurable_weight.ennreal_ofReal

omit [Fintype A] [MeasurableSingletonClass A] in
theorem step_weight_positive_ae [SFinite μ] :
    ∀ᵐ s∂stepReference (A := A) μ,0<R.weight s.2 := by
  apply (Measure.ae_prod_iff_ae_ae
    (measurableSet_lt measurable_const (R.measurable_weight.comp measurable_snd))).mpr
  exact Filter.Eventually.of_forall (fun _ => R.positive)

/-- Every future event has the same probability after reciprocal reference
rescaling, for the same arbitrary measurable history policy. -/
theorem recordLaw_reweighted [IsProbabilityMeasure μ]
    (π : Policy (A := A) (Y := Y)) (z : E) (n : ℕ) :
    recordLaw (D.reweighted R) π z n=recordLaw D π z n := by
  simp only [recordLaw]
  rw [stepReference_reweighted R,reference_withDensity (stepReference (A := A) μ)
    (fun s : A × Y => R.weight s.2) (R.measurable_weight.comp measurable_snd) n]
  have hf : Measurable (referenceWeight (fun s : A × Y => ENNReal.ofReal (R.weight s.2)) n) :=
    referenceWeight_measurable (fun s : A × Y => ENNReal.ofReal (R.weight s.2))
      (R.measurable_weight.comp measurable_snd).ennreal_ofReal n
  rw [← withDensity_mul _ hf (recordDensity_measurable (D.reweighted R) π z n)]
  apply withDensity_congr_ae
  filter_upwards [weight_valid_ae (stepReference (A := A) μ)
    (fun s : A × Y => R.weight s.2) (R.measurable_weight.comp measurable_snd)
    (step_weight_positive_ae R) n] with h hh
  change referenceWeight _ n h*(π.weight n h*ENNReal.ofReal (C.mass (run (D.reweighted R) z n h)))=_
  rw [run_reweighted D R z n h,map_smul,smul_eq_mul,hh.1]
  rw [mul_left_comm,← ENNReal.ofReal_mul hh.2.le]
  rw [← mul_assoc,mul_inv_cancel₀ hh.2.ne',one_mul]
  rfl

omit [MeasurableSpace E] [BorelSpace E] [MeasurableSpace A] [Fintype A]
  [MeasurableSingletonClass A] in
theorem observationRun_reweighted (actions : ℕ → A) (z : E) :
    (n : ℕ) → ∀ h : History Y n,
    observationRun (D.reweighted R) actions z n h=
      (realWeight R.weight n h)⁻¹ • observationRun D actions z n h
  | 0, _ => by simp [observationRun,realWeight]
  | n+1, h => by
    change (R.weight h.2)⁻¹ • D.op (actions n) h.2
      (observationRun (D.reweighted R) actions z n h.1)=_
    rw [observationRun_reweighted actions z n h.1]
    simp only [map_smul,smul_smul,realWeight,observationRun,mul_inv_rev]

omit [MeasurableSpace A] [Fintype A] [MeasurableSingletonClass A] in
/-- The prescribed-action full observation law also stays exactly unchanged. -/
theorem observationLaw_reweighted [IsProbabilityMeasure μ]
    (actions : ℕ → A) (z : E) (n : ℕ) :
    observationLaw (D.reweighted R) actions z n=observationLaw D actions z n := by
  simp only [observationLaw]
  change (reference (μ.withDensity (fun y => ENNReal.ofReal (R.weight y))) n).withDensity _=_
  rw [reference_withDensity μ R.weight R.measurable_weight n]
  rw [← withDensity_mul _
    (referenceWeight_measurable _ R.measurable_weight.ennreal_ofReal n)
    (observationDensity_measurable (D.reweighted R) actions z n)]
  apply withDensity_congr_ae
  filter_upwards [weight_valid_ae μ R.weight R.measurable_weight R.positive n] with h hh
  change referenceWeight _ n h*ENNReal.ofReal
    (C.mass (observationRun (D.reweighted R) actions z n h))=_
  rw [observationRun_reweighted D R actions z n h,map_smul,smul_eq_mul,hh.1]
  rw [← ENNReal.ofReal_mul hh.2.le,← mul_assoc,mul_inv_cancel₀ hh.2.ne',one_mul]
  rfl

end Komorebi.LSM.ContinuousRecordReference
