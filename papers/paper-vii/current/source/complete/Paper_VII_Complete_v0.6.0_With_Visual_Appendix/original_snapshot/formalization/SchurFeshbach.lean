module

public import Mathlib.LinearAlgebra.Matrix.SchurComplement
public import Mathlib.LinearAlgebra.Matrix.NonsingularInverse
public import Mathlib.Tactic.NormNum
public import Mathlib.Basic.Complex.Basic

public section
set_option autoImplicit false

/-! Author: Komorebi P. Literal retained blocks of the full matrix resolvent. -/
namespace KomorebiPaperVII.SchurFeshbach
open Matrix
variable {P Q : Type*} [Fintype P] [Fintype Q] [DecidableEq P] [DecidableEq Q]

noncomputable def schur (App : Matrix P P ℂ) (Apq : Matrix P Q ℂ)
    (Aqp : Matrix Q P ℂ) (Aqq : Matrix Q Q ℂ) (z : ℂ) : Matrix P P ℂ :=
  Matrix.scalar P z-App-Apq*(Matrix.scalar Q z-Aqq)⁻¹*Aqp

theorem resolvent_blocks (App : Matrix P P ℂ) (Apq : Matrix P Q ℂ)
    (Aqp : Matrix Q P ℂ) (Aqq : Matrix Q Q ℂ) (z : ℂ) :
    Matrix.scalar (P ⊕ Q) z-Matrix.fromBlocks App Apq Aqp Aqq =
      Matrix.fromBlocks (Matrix.scalar P z-App) (-Apq) (-Aqp) (Matrix.scalar Q z-Aqq) := by
  ext i j
  cases i <;> cases j <;> simp [Matrix.fromBlocks,Matrix.scalar,Matrix.diagonal]

theorem projected_resolvent (App : Matrix P P ℂ) (Apq : Matrix P Q ℂ)
    (Aqp : Matrix Q P ℂ) (Aqq : Matrix Q Q ℂ) (z : ℂ)
    [Invertible (Matrix.scalar Q z-Aqq)]
    [Invertible (Matrix.scalar (P ⊕ Q) z-Matrix.fromBlocks App Apq Aqp Aqq)] :
    ((Matrix.scalar (P ⊕ Q) z-Matrix.fromBlocks App Apq Aqp Aqq)⁻¹).submatrix
      Sum.inl Sum.inl = (schur App Apq Aqp Aqq z)⁻¹ := by
  let D := Matrix.scalar Q z-Aqq
  let A := Matrix.scalar P z-App
  have he := resolvent_blocks App Apq Aqp Aqq z
  let : Invertible (Matrix.fromBlocks A (-Apq) (-Aqp) D) := Invertible.copy ‹_› _ he.symm
  let : Invertible (A-(-Apq)*⅟D*(-Aqp)) := Matrix.invertibleOfFromBlocks₂₂Invertible A (-Apq) (-Aqp) D
  have hinv := Matrix.invOf_fromBlocks₂₂_eq A (-Apq) (-Aqp) D
  have hs : A-(-Apq)*⅟D*(-Aqp)=schur App Apq Aqp Aqq z := by
    simp only [Matrix.neg_mul,Matrix.mul_neg,neg_neg,Matrix.invOf_eq_nonsing_inv,schur,D,A]
  rw [he,← Matrix.invOf_eq_nonsing_inv,hinv]
  change ⅟(A-(-Apq)*⅟D*(-Aqp))=(schur App Apq Aqp Aqq z)⁻¹
  rw [Matrix.invOf_eq_nonsing_inv]
  congr 1

theorem schur_invertible (App : Matrix P P ℂ) (Apq : Matrix P Q ℂ)
    (Aqp : Matrix Q P ℂ) (Aqq : Matrix Q Q ℂ) (z : ℂ)
    [Invertible (Matrix.scalar Q z-Aqq)] :
    IsUnit (Matrix.scalar (P ⊕ Q) z-Matrix.fromBlocks App Apq Aqp Aqq) ↔
      IsUnit (schur App Apq Aqp Aqq z) := by
  rw [resolvent_blocks, Matrix.isUnit_fromBlocks_iff_of_invertible₂₂]
  simp only [Matrix.neg_mul,Matrix.mul_neg,neg_neg,Matrix.invOf_eq_nonsing_inv,schur]

end KomorebiPaperVII.SchurFeshbach

namespace KomorebiPaperVII.SchurFeshbach
/-- Counterexample to inferring full invertibility from the eliminated block alone.
For z=0 and H=diag(0,-1), the eliminated resolvent block is 1, but z-H is singular. -/
theorem eliminated_invertible_full_singular :
    IsUnit (1 : ℂ) ∧ ¬ IsUnit (!![0, 0; 0, 1] : Matrix (Fin 2) (Fin 2) ℂ) := by
  constructor
  · exact isUnit_one
  · rw [Matrix.isUnit_iff_isUnit_det]
    norm_num [Matrix.det_fin_two]
end KomorebiPaperVII.SchurFeshbach

/-! Exported theorem axiom audit. -/
#print axioms KomorebiPaperVII.SchurFeshbach.resolvent_blocks
#print axioms KomorebiPaperVII.SchurFeshbach.projected_resolvent
#print axioms KomorebiPaperVII.SchurFeshbach.schur_invertible
#print axioms KomorebiPaperVII.SchurFeshbach.eliminated_invertible_full_singular
