import KomorebiLSM.ObservableMomentConditional
import KomorebiLSM.FiniteMomentIdentification
import KomorebiLSM.RegressionGeometry

/-! Actual basis moments, exact coefficient inversion and directional
confidence propagation for P82. -/
set_option autoImplicit false
namespace Komorebi.LSM.ObservableMoments
open MeasureTheory Matrix FiniteMomentIdentification
open scoped BigOperators Matrix

section Moments
variable {E A Y : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E]
variable [FiniteDimensional ℝ E] [MeasurableSpace E] [BorelSpace E]
variable [MeasurableSpace Y] {C : BaseNorm.ProbabilityCone E} {ν : Measure Y}
variable (D : ContinuousInstrument.DensityInstrument (A := A) C ν) {p : ℕ}

/-- The known integration matrix of the specified test and observation bases. -/
noncomputable def basisMomentMatrix (g ψ : Fin p → Y → ℝ) : Matrix (Fin p) (Fin p) ℝ :=
  fun j k => ∫ y,g j y*ψ k y∂ν

omit [FiniteDimensional ℝ E] [MeasurableSpace E] [BorelSpace E] in
/-- Finite basis-product integrability supplies the actual weighted operator
integrals rather than presuming the moment equation. -/
theorem weighted_operator_integrable (B : A → Fin p → E →L[ℝ] E) (ψ : Fin p → Y → ℝ)
    (hB : ∀ a y,D.op a y=∑ k,ψ k y • B a k)
    (g : Y → ℝ) (hgψ : ∀ k,Integrable (fun y => g y*ψ k y) ν) (a : A) :
    Integrable (fun y => g y • D.op a y) ν := by
  have hi (k : Fin p) : Integrable (fun y => (g y*ψ k y) • B a k) ν :=
    (hgψ k).smul_const (B a k)
  have hsum : Integrable (fun y => ∑ k : Fin p,(g y*ψ k y) • B a k) ν :=
    integrable_finsetSum (f := fun k : Fin p => fun y : Y => (g y*ψ k y) • B a k)
      (Finset.univ) (fun k _ => hi k)
  have he : (fun y => g y • D.op a y)=
      (fun y => ∑ k : Fin p,(g y*ψ k y) • B a k) := by
    funext y
    rw [hB a y,Finset.smul_sum]
    simp only [smul_smul]
  rw [he]
  exact hsum

omit [MeasurableSpace E] [BorelSpace E] in
/-- Integrating the submitted finite observation expansion gives the literal
moment mixing equation coefficient by coefficient. -/
theorem momentOperator_mixing (B : A → Fin p → E →L[ℝ] E)
    (g ψ : Fin p → Y → ℝ) (hB : ∀ a y,D.op a y=∑ k,ψ k y • B a k)
    (hgψ : ∀ j k,Integrable (fun y => g j y*ψ k y) ν) (a : A) :
    (fun j => momentOperator D (g j) a)=mix (basisMomentMatrix (ν := ν) g ψ) (B a) := by
  funext j
  unfold momentOperator mix basisMomentMatrix
  have he : (fun y => g j y • D.op a y)=
      (fun y => ∑ k : Fin p,(g j y*ψ k y) • B a k) := by
    funext y
    rw [hB a y,Finset.smul_sum]
    simp only [smul_smul]
  rw [he,integral_finsetSum _ (fun k _ => (hgψ j k).smul_const (B a k))]
  apply Finset.sum_congr rfl
  intro k _
  exact integral_smul_const _ _

/-- The actual inverse matrix reconstructs any finite family in a real vector
space; invertibility is an explicit condition on the known integration matrix. -/
theorem inverse_mix {F : Type*} [AddCommGroup F] [Module ℝ F]
    (W : Matrix (Fin p) (Fin p) ℝ) (hW : IsUnit W) (B : Fin p → F) :
    mix W⁻¹ (mix W B)=B := by
  rw [mix_mul,Matrix.nonsing_inv_mul W ((Matrix.isUnit_iff_isUnit_det W).mp hW),mix_one]

omit [MeasurableSpace E] [BorelSpace E] in
/-- P82's coefficient formula follows from actual moment integration and the
known invertible basis matrix, not from an assumed reconstruction relation. -/
theorem coefficient_from_moments (B : A → Fin p → E →L[ℝ] E)
    (g ψ : Fin p → Y → ℝ) (hB : ∀ a y,D.op a y=∑ k,ψ k y • B a k)
    (hgψ : ∀ j k,Integrable (fun y => g j y*ψ k y) ν)
    (hW : IsUnit (basisMomentMatrix (ν := ν) g ψ)) (a : A) :
    B a=mix (basisMomentMatrix (ν := ν) g ψ)⁻¹ (fun j => momentOperator D (g j) a) := by
  rw [momentOperator_mixing D B g ψ hB hgψ a,inverse_mix _ hW]

end Moments

section Directional
variable {p r : ℕ}

theorem mixed_row_apply (W : Matrix (Fin p) (Fin p) ℝ)
    (M : Fin p → Matrix (Fin r) (Fin r) ℝ) (k : Fin p) (i : Fin r) (x : Fin r → ℝ) :
    (mix W M k *ᵥ x) i=∑ j,W k j*(M j *ᵥ x) i := by
  simp only [mix,Matrix.mulVec,dotProduct,Matrix.sum_apply,Matrix.smul_apply,
    smul_eq_mul,Finset.sum_mul,Finset.mul_sum]
  rw [Finset.sum_comm]
  apply Finset.sum_congr rfl
  intro j _
  apply Finset.sum_congr rfl
  intro l _
  ring

/-- Genuine weighted Cauchy--Schwarz propagates row ellipsoids through the
known inverse linear map in every submitted direction. -/
theorem mixed_directional_error (W : Matrix (Fin p) (Fin p) ℝ)
    (Mhat M : Fin p → Matrix (Fin r) (Fin r) ℝ) (V : Matrix (Fin r) (Fin r) ℝ)
    (hV : V.PosDef) (β : Fin p → Fin r → ℝ)
    (hb : ∀ j i,RegressionConfidence.weightedNorm V (fun l => Mhat j i l-M j i l)≤β j i)
    (k : Fin p) (i : Fin r) (x : Fin r → ℝ) :
    |(mix W Mhat k *ᵥ x) i-(mix W M k *ᵥ x) i|≤
      ∑ j,|W k j| * β j i*RegressionConfidence.weightedNorm V⁻¹ x := by
  have he : (mix W Mhat k *ᵥ x) i-(mix W M k *ᵥ x) i=
      ∑ j,W k j*((fun l => Mhat j i l-M j i l) ⬝ᵥ x) := by
    rw [mixed_row_apply,mixed_row_apply,← Finset.sum_sub_distrib]
    apply Finset.sum_congr rfl
    intro j _
    rw [← mul_sub]
    congr 1
    simp only [Matrix.mulVec,dotProduct,sub_mul,Finset.sum_sub_distrib]
  rw [he]
  calc
    _ ≤ ∑ j,|W k j*((fun l => Mhat j i l-M j i l) ⬝ᵥ x)| :=
      Finset.abs_sum_le_sum_abs _ _
    _ ≤ _ := by
      apply Finset.sum_le_sum
      intro j _
      rw [abs_mul]
      have hcs := RegressionConfidence.weighted_cauchy_schwarz hV
        (fun l => Mhat j i l-M j i l) x
      have hh := hcs.trans (mul_le_mul_of_nonneg_right (hb j i) (Real.sqrt_nonneg _))
      exact (mul_le_mul_of_nonneg_left hh (abs_nonneg _)).trans_eq (mul_assoc _ _ _).symm

end Directional
end Komorebi.LSM.ObservableMoments
