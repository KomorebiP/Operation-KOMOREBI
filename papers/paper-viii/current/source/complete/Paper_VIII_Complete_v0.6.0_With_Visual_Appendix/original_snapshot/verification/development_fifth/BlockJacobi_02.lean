module
public import Mathlib.Analysis.Matrix.Order
public import Mathlib.Analysis.Real.Sqrt
public import Mathlib.Tactic

/-!
Author: Komorebi P. Paper VIII items 7.4 and 7.6.
The normalization uses the actual positive matrix square root and actual inverse.
Condition number is the product of Euclidean operator norms. The PCG result
compares the classical convergence factors; it does not reprove the CG algorithm.
-/
public section
set_option autoImplicit false
namespace KomorebiPaperVIII
open scoped BigOperators Matrix Matrix.Norms.L2Operator ComplexOrder MatrixOrder

section Ring
variable {R : Type*} [NormedRing R] [NormOneClass R]

theorem inverse_near_one_bound (E B : R) (hB : (1+E)*B=1)
    (η : ℝ) (hE : ‖E‖ ≤ η) (hη : η < 1) : ‖B‖ ≤ 1/(1-η) := by
  have heq : B = 1-E*B := by
    apply eq_sub_iff_add_eq.mpr
    simpa only [add_mul,one_mul] using hB
  have hb : ‖B‖ ≤ 1+η*‖B‖ := by
    calc
      ‖B‖ = ‖1-E*B‖ := congrArg norm heq
      _ ≤ ‖(1:R)‖+‖E*B‖ := norm_sub_le _ _
      _ ≤ 1+‖E‖*‖B‖ := by
        simpa only [norm_one] using
          (add_le_add (le_refl ‖(1:R)‖) (norm_mul_le E B))
      _ ≤ 1+η*‖B‖ := by
        gcongr
  apply (le_div_iff₀ (by linarith : 0 < 1-η)).mpr
  nlinarith

theorem near_one_condition_bound (E B : R) (hB : (1+E)*B=1)
    (η : ℝ) (hE : ‖E‖ ≤ η) (hη : η < 1) :
    ‖1+E‖*‖B‖ ≤ (1+η)/(1-η) := by
  have hη0 : 0 ≤ η := (norm_nonneg E).trans hE
  have hn : ‖1+E‖ ≤ 1+η := by
    have hadd := norm_add_le (1:R) E
    rw [norm_one] at hadd
    linarith
  have hb := inverse_near_one_bound E B hB η hE hη
  calc
    ‖1+E‖*‖B‖ ≤ (1+η)*(1/(1-η)) :=
      mul_le_mul hn hb (norm_nonneg B) (by linarith)
    _ = (1+η)/(1-η) := by ring
end Ring

section Matrix
variable {X : Type*} [Fintype X] [DecidableEq X] [Nonempty X]

noncomputable def invSqrt (D : Matrix X X ℂ) : Matrix X X ℂ := (CFC.sqrt D)⁻¹

noncomputable def matrixCondition (A : Matrix X X ℂ) : ℝ := ‖A‖*‖A⁻¹‖

theorem invSqrt_isUnit (D : Matrix X X ℂ) (hD : D.PosDef) : IsUnit (invSqrt D) := by
  unfold invSqrt
  apply Matrix.isUnit_nonsing_inv_iff.mpr
  exact (CFC.isUnit_sqrt_iff D hD.posSemidef.nonneg).mpr hD.isUnit

/-- The actual positive inverse square root whitens D. -/
theorem invSqrt_normalizes (D : Matrix X X ℂ) (hD : D.PosDef) :
    invSqrt D*D*invSqrt D = 1 := by
  have hroot : IsUnit (CFC.sqrt D) :=
    (CFC.isUnit_sqrt_iff D hD.posSemidef.nonneg).mpr hD.isUnit
  have hd := (Matrix.isUnit_iff_isUnit_det _).mp hroot
  have hs := CFC.sqrt_mul_sqrt_self D hD.posSemidef.nonneg
  unfold invSqrt
  calc
    (CFC.sqrt D)⁻¹*D*(CFC.sqrt D)⁻¹ =
        (CFC.sqrt D)⁻¹*(CFC.sqrt D*CFC.sqrt D)*(CFC.sqrt D)⁻¹ :=
      congrArg (fun M => (CFC.sqrt D)⁻¹*M*(CFC.sqrt D)⁻¹) hs.symm
    _ = ((CFC.sqrt D)⁻¹*CFC.sqrt D)*(CFC.sqrt D*(CFC.sqrt D)⁻¹) := by
      simp only [Matrix.mul_assoc]
    _ = 1 := by rw [Matrix.nonsing_inv_mul _ hd,Matrix.mul_nonsing_inv _ hd,one_mul]

theorem normalized_decomposition (D K : Matrix X X ℂ) (hD : D.PosDef) :
    invSqrt D*(D+K)*invSqrt D = 1+invSqrt D*K*invSqrt D := by
  rw [Matrix.mul_add,Matrix.add_mul,invSqrt_normalizes D hD]

/-- Actual condition bound. Hermiticity of the perturbation is not needed by this stronger estimate. -/
theorem block_jacobi_condition (D K : Matrix X X ℂ)
    (hD : D.PosDef) (hA : (D+K).PosDef) (η : ℝ)
    (hE : ‖invSqrt D*K*invSqrt D‖ ≤ η) (hη : η < 1) :
    matrixCondition (invSqrt D*(D+K)*invSqrt D) ≤ (1+η)/(1-η) := by
  have hunit := ((invSqrt_isUnit D hD).mul hA.isUnit).mul (invSqrt_isUnit D hD)
  have hdet := (Matrix.isUnit_iff_isUnit_det _).mp hunit
  have hinv := Matrix.mul_nonsing_inv (invSqrt D*(D+K)*invSqrt D) hdet
  rw [normalized_decomposition D K hD] at hinv ⊢
  exact near_one_condition_bound _ _ hinv η hE hη

theorem matrix_condition_ge_one (A : Matrix X X ℂ) (hA : IsUnit A) :
    1 ≤ matrixCondition A := by
  have hn := norm_mul_le A A⁻¹
  rw [Matrix.mul_nonsing_inv _ ((Matrix.isUnit_iff_isUnit_det _).mp hA),norm_one] at hn
  exact hn
end Matrix

noncomputable def cgFactor (κ : ℝ) : ℝ := (Real.sqrt κ-1)/(Real.sqrt κ+1)

theorem cgFactor_mono {κ κmax : ℝ} (h : κ ≤ κmax) : cgFactor κ ≤ cgFactor κmax := by
  have hs := Real.sqrt_le_sqrt h
  have hκ := Real.sqrt_nonneg κ
  have hκmax := Real.sqrt_nonneg κmax
  unfold cgFactor
  apply (div_le_div_iff₀ (by linarith) (by linarith)).mpr
  nlinarith

theorem cgFactor_nonneg {κ : ℝ} (h : 1 ≤ κ) : 0 ≤ cgFactor κ := by
  have hs := Real.one_le_sqrt.mpr h
  unfold cgFactor
  positivity

theorem cgFactor_lt_one (κ : ℝ) : cgFactor κ < 1 := by
  have hs := Real.sqrt_nonneg κ
  unfold cgFactor
  apply (div_lt_one (by linarith)).mpr
  linarith

/-- Item 7.6 compares the actual normalized matrix condition-number factor. -/
theorem certified_packet_factor {X : Type*} [Fintype X] [DecidableEq X] [Nonempty X]
    (D K : Matrix X X ℂ) (hD : D.PosDef) (hA : (D+K).PosDef)
    (η : ℝ) (hE : ‖invSqrt D*K*invSqrt D‖ ≤ η) (hη : η < 1) :
    cgFactor (matrixCondition (invSqrt D*(D+K)*invSqrt D)) ≤
      cgFactor ((1+η)/(1-η)) :=
  cgFactor_mono (block_jacobi_condition D K hD hA η hE hη)

/-- Explicit propagation of an already established classical energy-error estimate. -/
theorem certified_energy_error {κ κmax e0 em : ℝ} (m : ℕ)
    (hκ : 1 ≤ κ) (hbound : κ ≤ κmax) (he0 : 0 ≤ e0)
    (hCG : em ≤ 2*(cgFactor κ)^m*e0) :
    em ≤ 2*(cgFactor κmax)^m*e0 := by
  have hp : (cgFactor κ)^m ≤ (cgFactor κmax)^m :=
    pow_le_pow_left₀ (cgFactor_nonneg hκ) (cgFactor_mono hbound) m
  exact hCG.trans (mul_le_mul_of_nonneg_right
    (mul_le_mul_of_nonneg_left hp (by norm_num)) he0)

end KomorebiPaperVIII
