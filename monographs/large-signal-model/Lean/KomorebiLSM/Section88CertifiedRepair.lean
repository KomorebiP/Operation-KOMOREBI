import KomorebiLSM.Section88ProposedDirectPosOrientation
import KomorebiLSM.Section88ProposedDirectPosGap
import KomorebiLSM.Section88ProposedDirectNegOrientation
import KomorebiLSM.Section88ProposedDirectNegGap
import KomorebiLSM.Section88ProposedRotatedPosOrientation
import KomorebiLSM.Section88ProposedRotatedPosGap
import KomorebiLSM.Section88ProposedRotatedNegOrientation
import KomorebiLSM.Section88ProposedRotatedNegGap
import KomorebiLSM.Section88ComparisonDirectPosOrientation
import KomorebiLSM.Section88ComparisonDirectPosGap
import KomorebiLSM.Section88ComparisonDirectNegOrientation
import KomorebiLSM.Section88ComparisonDirectNegGap
import KomorebiLSM.Section88ComparisonRotatedPosOrientation
import KomorebiLSM.Section88ComparisonRotatedPosGap
import KomorebiLSM.Section88ComparisonRotatedNegOrientation
import KomorebiLSM.Section88ComparisonRotatedNegGap
import KomorebiLSM.Section88ComparisonBudget
import KomorebiLSM.MeasureTVCalculus

/-! Full Section 88 repair: the recorded finite witnesses certify both domains,
the declared output uncertainty is retained, and the comparison law bound is
charged the actual reset cost. No empirical coverage assertion is made. -/
set_option autoImplicit false
set_option maxHeartbeats 1200000
namespace Komorebi.LSM.Section88CertifiedRepair
open scoped BigOperators
open LorentzCylinder RobustOrientedMargin RationalBernsteinMargin RationalLorentzMatrix
open PerturbedOperatorFixture ContinuousInstrument MeasureTheory UniformIntervalMoments
noncomputable section

def proposedCertificate (a : Bool) : Certificate (nominalProposed a) (1/16) where
  orientationWitness left := by
    cases a <;> cases left
    · exact Section88ProposedDirectPosOrientation.certifiedWitness
    · exact Section88ProposedDirectNegOrientation.certifiedWitness
    · exact Section88ProposedRotatedPosOrientation.certifiedWitness
    · exact Section88ProposedRotatedNegOrientation.certifiedWitness
  squareGapWitness left := by
    cases a <;> cases left
    · exact Section88ProposedDirectPosGap.certifiedWitness
    · exact Section88ProposedDirectNegGap.certifiedWitness
    · exact Section88ProposedRotatedPosGap.certifiedWitness
    · exact Section88ProposedRotatedNegGap.certifiedWitness

theorem proposed_moment_mass (a : Bool) (z : State ℂ) :
    probabilityCone.mass ((∑ k : Fin 3,moment k • matrixOperator (nominalProposed a k)) z)=
      probabilityCone.mass z := by
  apply Section88ComparisonBudget.moment_mass_of_rows (nominalProposed a) (11/32) (63/32) _ _ (by norm_num) z
  · intro j
    cases a <;> fin_cases j <;> norm_num [Matrix.cons_val_two]
  · intro j
    cases a <;> fin_cases j <;> norm_num [Matrix.cons_val_two]

def proposedInstrument : DensityInstrument (A := Bool) (probabilityCone (V := ℂ)) measure :=
  certifiedInstrument nominalProposed (1/16) proposedCertificate (by norm_num) proposed_moment_mass

theorem proposed_margin (a : Bool) (u : ℝ) (hu : u∈Set.Icc (-1 : ℝ) 1) :
    (1/16 : ℝ)≤sigma (proposedInstrument.op a u) := by
  have h := (proposedCertificate a).margin u hu
  norm_num at h
  exact h

def comparisonCertificate (a : Bool) : Certificate (nominalComparison a) (1/16) where
  orientationWitness left := by
    cases a <;> cases left
    · exact Section88ComparisonDirectPosOrientation.certifiedWitness
    · exact Section88ComparisonDirectNegOrientation.certifiedWitness
    · exact Section88ComparisonRotatedPosOrientation.certifiedWitness
    · exact Section88ComparisonRotatedNegOrientation.certifiedWitness
  squareGapWitness left := by
    cases a <;> cases left
    · exact Section88ComparisonDirectPosGap.certifiedWitness
    · exact Section88ComparisonDirectNegGap.certifiedWitness
    · exact Section88ComparisonRotatedPosGap.certifiedWitness
    · exact Section88ComparisonRotatedNegGap.certifiedWitness

theorem comparison_moment_mass (a : Bool) (z : State ℂ) :
    probabilityCone.mass ((∑ k : Fin 3,moment k • matrixOperator (nominalComparison a k)) z)=
      probabilityCone.mass z := by
  apply Section88ComparisonBudget.moment_mass_of_rows (nominalComparison a) (11/32) (63/32) _ _ (by norm_num) z
  · intro j
    cases a <;> fin_cases j <;> norm_num [Matrix.cons_val_two]
  · intro j
    cases a <;> fin_cases j <;> norm_num [Matrix.cons_val_two]

def comparisonInstrument : DensityInstrument (A := Bool) (probabilityCone (V := ℂ)) measure :=
  certifiedInstrument nominalComparison (1/16) comparisonCertificate (by norm_num) comparison_moment_mass

theorem comparison_margin (a : Bool) (u : ℝ) (hu : u∈Set.Icc (-1 : ℝ) 1) :
    (1/16 : ℝ)≤sigma (comparisonInstrument.op a u) := by
  have h := (comparisonCertificate a).margin u hu
  norm_num at h
  exact h

/-- The supplied physical center has the same normalized center image in both atlases. -/
theorem initial_atlases :
    matrixOperator proposedTransform (1,(⟨1/2,1/2⟩ : ℂ))=(1,0) ∧
    matrixOperator comparisonTransform (1,(⟨1/2,1/2⟩ : ℂ))=(1,0) := by
  constructor <;> apply coordinate_ext <;> intro i
  all_goals rw [coordinate_matrixOperator]
  all_goals fin_cases i <;>
    norm_num [proposedTransform,comparisonTransform,coordinate,Fin.sum_univ_succ,Matrix.cons_val_two]

theorem initial_mem : (1,(0 : ℂ))∈probabilityCone.base := by
  rw [mem_base]
  constructor <;> norm_num

/-- Complete replay implies all-horizon internal validity, including the actual center. -/
theorem nominal_record_probability (policy : ContinuousRecords.Policy (A := Bool) (Y := ℝ)) (N : ℕ) :
    IsProbabilityMeasure (ContinuousRecords.recordLaw proposedInstrument policy (1,0) N) :=
  ContinuousRecords.recordLaw_probability proposedInstrument policy ⟨(1,0),initial_mem⟩ N

/-- The declared output budgets leave the exact residual slack 3/64. -/
theorem robust_residual (Delta : State ℂ →L[ℝ] State ℂ) (a : Bool) (u : ℝ)
    (hu : u∈Set.Icc (-1 : ℝ) 1)
    (h0 : ∀ v : ℂ,‖v‖≤1 → |(Delta (1,v)).1|≤1/128)
    (h1 : ∀ v : ℂ,‖v‖≤1 → ‖(Delta (1,v)).2‖≤1/128) :
    (3/64 : ℝ)≤sigma (proposedInstrument.op a u+Delta) := by
  have h := residual_margin _ Delta (1/16) (1/128) (1/128)
    (proposed_margin a u hu) h0 h1
  norm_num at h ⊢
  exact h

theorem uncertaintyCertificate
    (E : Bool → Fin 3 → State ℂ →L[ℝ] State ℂ)
    (h0 : ∀ a u,u∈Set.Icc (-1 : ℝ) 1 → ∀ v : ℂ,‖v‖≤1 →
      |(PolynomialGram.operatorPolynomial (E a) u (1,v)).1|≤1/128)
    (h1 : ∀ a u,u∈Set.Icc (-1 : ℝ) 1 → ∀ v : ℂ,‖v‖≤1 →
      ‖(PolynomialGram.operatorPolynomial (E a) u (1,v)).2‖≤1/128) :
    MarginCertificate (fun a k => matrixOperator (nominalProposed a k)) E
      (fun _ _ => 1/16) (fun _ _ => 1/128) (fun _ _ => 1/128) where
  margin := proposed_margin
  mass_error := h0
  spatial_error := h1
  cover := by intros; norm_num

/-- The uncertainty family is a normalized probability model only with its exact mass constraint. -/
def uncertainInstrument
    (E : Bool → Fin 3 → State ℂ →L[ℝ] State ℂ)
    (h0 : ∀ a u,u∈Set.Icc (-1 : ℝ) 1 → ∀ v : ℂ,‖v‖≤1 →
      |(PolynomialGram.operatorPolynomial (E a) u (1,v)).1|≤1/128)
    (h1 : ∀ a u,u∈Set.Icc (-1 : ℝ) 1 → ∀ v : ℂ,‖v‖≤1 →
      ‖(PolynomialGram.operatorPolynomial (E a) u (1,v)).2‖≤1/128)
    (hm : ∀ a z,probabilityCone.mass ((∑ k : Fin 3,moment k • E a k) z)=0) :
    DensityInstrument (A := Bool) (probabilityCone (V := ℂ)) measure :=
  RobustOrientedMargin.uncertainInstrument _ E _ _ _ (uncertaintyCertificate E h0 h1) (by
    intro a z
    simp only [smul_add,Finset.sum_add_distrib,add_apply,map_add]
    rw [proposed_moment_mass,hm]
    ring)

/-- Every degree-two matrix-entry perturbation in the declared box obeys those output budgets. -/
theorem coefficient_box_output (E : Bool → Fin 3 → ComplexCoefficientBox.RealMatrix)
    (hE : ∀ a k i j,|E a k i j|≤1/4096) (a : Bool) (u : ℝ) (hu : u∈Set.Icc (-1 : ℝ) 1)
    (v : ℂ) (hv : ‖v‖≤1) :
    |(PolynomialGram.operatorPolynomial (fun k => ComplexCoefficientBox.matrixOperator (E a k)) u (1,v)).1|≤1/128 ∧
    ‖(PolynomialGram.operatorPolynomial (fun k => ComplexCoefficientBox.matrixOperator (E a k)) u (1,v)).2‖≤1/128 := by
  have h := ComplexCoefficientBox.polynomial_output_bounds (E a) (fun _ => 1/4096) (hE a) u hu v hv
  norm_num [Fin.sum_univ_succ] at h
  constructor <;> linarith [h.1,h.2]

theorem uncertain_record_probability
    (E : Bool → Fin 3 → State ℂ →L[ℝ] State ℂ)
    (h0 : ∀ a u,u∈Set.Icc (-1 : ℝ) 1 → ∀ v : ℂ,‖v‖≤1 →
      |(PolynomialGram.operatorPolynomial (E a) u (1,v)).1|≤1/128)
    (h1 : ∀ a u,u∈Set.Icc (-1 : ℝ) 1 → ∀ v : ℂ,‖v‖≤1 →
      ‖(PolynomialGram.operatorPolynomial (E a) u (1,v)).2‖≤1/128)
    (hm : ∀ a z,probabilityCone.mass ((∑ k : Fin 3,moment k • E a k) z)=0)
    (policy : ContinuousRecords.Policy (A := Bool) (Y := ℝ)) (N : ℕ) :
    IsProbabilityMeasure (ContinuousRecords.recordLaw (uncertainInstrument E h0 h1 hm) policy (1,0) N) :=
  ContinuousRecords.recordLaw_probability _ policy ⟨(1,0),initial_mem⟩ N


/-- The exact coefficient box, intersected with its mass affine subspace, is an actual all-horizon model family. -/
def coefficientBoxInstrument (E : Bool → Fin 3 → ComplexCoefficientBox.RealMatrix)
    (hE : ∀ a k i j,|E a k i j|≤1/4096)
    (hm : ∀ a z,probabilityCone.mass ((∑ k : Fin 3,moment k •
      ComplexCoefficientBox.matrixOperator (E a k)) z)=0) :
    DensityInstrument (A := Bool) (probabilityCone (V := ℂ)) measure :=
  uncertainInstrument (fun a k => ComplexCoefficientBox.matrixOperator (E a k))
    (fun a u hu v hv => (coefficient_box_output E hE a u hu v hv).1)
    (fun a u hu v hv => (coefficient_box_output E hE a u hu v hv).2) hm

theorem coefficient_box_record_probability (E : Bool → Fin 3 → ComplexCoefficientBox.RealMatrix)
    (hE : ∀ a k i j,|E a k i j|≤1/4096)
    (hm : ∀ a z,probabilityCone.mass ((∑ k : Fin 3,moment k •
      ComplexCoefficientBox.matrixOperator (E a k)) z)=0)
    (policy : ContinuousRecords.Policy (A := Bool) (Y := ℝ)) (N : ℕ) :
    IsProbabilityMeasure (ContinuousRecords.recordLaw (coefficientBoxInstrument E hE hm) policy (1,0) N) :=
  ContinuousRecords.recordLaw_probability _ policy ⟨(1,0),initial_mem⟩ N

def resetProfile : InteriorRepair.ResetProfile (A := Bool) where
  density _ _ := 1
  measurable_density _ := measurable_const
  integrable_density _ := integrable_const _
  minimum := 1
  minimum_positive := by norm_num
  lower := by intros; norm_num
  integral_one := by intro a; simp

/-- The comparison certificate checks exactly the declared one-eighth reset of the raw fit. -/
theorem comparison_is_repair (a : Bool) (u : ℝ) :
    comparisonInstrument.op a u=InteriorRepair.repair
      (Section88ComparisonBudget.rawEstimate.op a u) (resetProfile.density a u) (1/8) := by
  apply ContinuousLinearMap.ext
  intro z
  apply coordinate_ext
  intro i
  change coordinate i
    (PolynomialGram.operatorPolynomial (fun k => matrixOperator (nominalComparison a k)) u z)=_
  simp only [InteriorRepair.repair,add_apply,smul_apply,map_add,map_smul,
    Section88ComparisonBudget.rawEstimate,InteriorRepair.EstimateFamily.ofPolynomial,
    PolynomialGram.operatorPolynomial,sum_apply,smul_apply,map_sum,map_smul]
  simp only [coordinate_matrixOperator]
  cases a <;> fin_cases i <;>
    norm_num [InteriorRepair.resetOperator,resetProfile,
      InteriorRepair.centerReset_apply,Fin.sum_univ_succ,coordinate,Matrix.cons_val_two] <;> ring

/-- The exact comparison discrepancy keeps both the raw error and the reset charge. -/
theorem comparison_integrated_error (a : Bool) (z : State ℂ) (hz : z∈probabilityCone.base) :
    (∫ u,probabilityCone.value (comparisonInstrument.op a u z-Section88Reference.instrument.op a u z)∂measure)≤
      81687/320000 := by
  have h := InteriorRepair.repair_integrated_error Section88Reference.instrument
    Section88ComparisonBudget.rawEstimate resetProfile (1/8) (by norm_num) (by norm_num)
      (241/40000) a z hz (Section88ComparisonBudget.integrated_raw_error a z hz)
  simp only [← comparison_is_repair] at h
  norm_num at h ⊢
  exact h

/-- Full P79 finite-horizon law bound for the nominal repaired model and unchanged reference. -/
theorem comparison_law_bound (policy : ContinuousRecords.Policy (A := Bool) (Y := ℝ))
    (z : DensityInstrument.State (probabilityCone (V := ℂ))) (N : ℕ) :
    SequentialLowerCertificate.lawTV
      (TimeRecords.recordLaw (fun _ => comparisonInstrument) policy z.1 N)
      (TimeRecords.recordLaw (fun _ => Section88Reference.instrument) policy z.1 N)≤
        min 1 (81687*(N : ℝ)/640000) := by
  have h := InteriorRepair.common_policy_law_error Section88Reference.instrument comparisonInstrument
    Section88ComparisonBudget.rawEstimate resetProfile (1/8) (by norm_num) (by norm_num)
      (241/40000) comparison_is_repair Section88ComparisonBudget.integrated_raw_error policy z N
  convert h using 1
  congr 1
  ring

end
end Komorebi.LSM.Section88CertifiedRepair
