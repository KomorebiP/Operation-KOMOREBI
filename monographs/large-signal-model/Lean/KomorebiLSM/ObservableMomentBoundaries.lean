import KomorebiLSM.ObservableMomentConfidence
import KomorebiLSM.BaseNormModels

/-! Actual instrument, basis and weighted-norm boundaries for P82. -/
set_option autoImplicit false
namespace Komorebi.LSM.ObservableMoments.Boundaries
open MeasureTheory Matrix RegressionConfidence
open scoped BigOperators Matrix

abbrev Vec2 := Fin 2 → ℝ
noncomputable def simplexCone : BaseNorm.ProbabilityCone Vec2 := BaseNorm.orthant (Fin 2)
noncomputable def onePointReference : Measure Unit := Measure.dirac ()
instance onePointReference_probability : IsProbabilityMeasure onePointReference := by
  unfold onePointReference
  infer_instance

noncomputable def identityInstrument :
    ContinuousInstrument.DensityInstrument (A := Unit) simplexCone onePointReference where
  op _ _ := ContinuousLinearMap.id ℝ Vec2
  measurable_op _ := measurable_const
  integrable_op _ := integrable_const _
  positive _ := Filter.Eventually.of_forall (fun _ _ hz => hz)
  mass_preserving _ z := by
    rw [integral_const,probReal_univ,one_smul]
    rfl

noncomputable def leftState : ContinuousInstrument.DensityInstrument.State simplexCone :=
  ⟨![1,0],by
    constructor
    · rw [simplexCone,BaseNorm.orthant_carrier]
      intro i
      fin_cases i <;> norm_num
    · change (∑ i : Fin 2,![1,0] i)=1
      norm_num [Fin.sum_univ_two]⟩

noncomputable def rightState : ContinuousInstrument.DensityInstrument.State simplexCone :=
  ⟨![0,1],by
    constructor
    · rw [simplexCone,BaseNorm.orthant_carrier]
      intro i
      fin_cases i <;> norm_num
    · change (∑ i : Fin 2,![0,1] i)=1
      norm_num [Fin.sum_univ_two]⟩

theorem identity_moment (z : Vec2) : momentOperator identityInstrument (fun _ : Unit => 1) () z=z := by
  change (∫ _ : Unit,(1:ℝ) • ContinuousLinearMap.id ℝ Vec2∂onePointReference) z=z
  rw [one_smul,integral_const,probReal_univ,one_smul]
  rfl

theorem wrong_posterior_mean :
    (∫ _ : Unit,rightState.1∂identityInstrument.kernel () leftState)=rightState.1 := by
  rw [integral_const,probReal_univ,one_smul]

theorem wrong_accessible_posterior_not_mean :
    (∫ _ : Unit,rightState.1∂identityInstrument.kernel () leftState)≠
      momentOperator identityInstrument (fun _ : Unit => 1) () leftState.1 := by
  rw [wrong_posterior_mean,identity_moment]
  intro he
  have h0 := congrFun he 0
  norm_num [leftState,rightState] at h0

noncomputable def firstCoefficients (k : Fin 2) : Vec2 →L[ℝ] Vec2 :=
  if k=0 then ContinuousLinearMap.id ℝ Vec2 else 0
noncomputable def secondCoefficients (k : Fin 2) : Vec2 →L[ℝ] Vec2 :=
  if k=1 then ContinuousLinearMap.id ℝ Vec2 else 0

def repeatedBasis (_ : Fin 2) (_ : Unit) : ℝ := 1

theorem first_expansion (u : Unit) : identityInstrument.op () u=
    ∑ k : Fin 2,repeatedBasis k u • firstCoefficients k := by
  simp [identityInstrument,repeatedBasis,firstCoefficients]

theorem second_expansion (u : Unit) : identityInstrument.op () u=
    ∑ k : Fin 2,repeatedBasis k u • secondCoefficients k := by
  simp [identityInstrument,repeatedBasis,secondCoefficients]

theorem coefficients_distinct : firstCoefficients≠secondCoefficients := by
  intro he
  have h0 := congrArg (fun F : Fin 2 → Vec2 →L[ℝ] Vec2 => F 0 leftState.1 0) he
  norm_num [firstCoefficients,secondCoefficients,leftState] at h0

theorem repeated_moment_matrix :
    basisMomentMatrix (ν := onePointReference) repeatedBasis repeatedBasis=!![1,1;1,1] := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    simp [basisMomentMatrix,repeatedBasis]

theorem repeated_moment_matrix_singular :
    ¬IsUnit (basisMomentMatrix (ν := onePointReference) repeatedBasis repeatedBasis) := by
  rw [repeated_moment_matrix,Matrix.isUnit_iff_isUnit_det]
  norm_num [Matrix.det_fin_two]

noncomputable def smallDesign : Matrix (Fin 1) (Fin 1) ℝ := (1/4:ℝ) • 1
def unitDirection : Fin 1 → ℝ := fun _ => 1

theorem smallDesign_posDef : smallDesign.PosDef := Matrix.PosDef.one.smul (by norm_num)

theorem small_weighted_norm : weightedNorm smallDesign unitDirection=1/2 := by
  norm_num [weightedNorm,smallDesign,unitDirection,Matrix.mulVec,dotProduct,Fin.sum_univ_one]

theorem unit_direction_pairing : |unitDirection ⬝ᵥ unitDirection|=1 := by
  norm_num [unitDirection,dotProduct,Fin.sum_univ_one]

end Komorebi.LSM.ObservableMoments.Boundaries
