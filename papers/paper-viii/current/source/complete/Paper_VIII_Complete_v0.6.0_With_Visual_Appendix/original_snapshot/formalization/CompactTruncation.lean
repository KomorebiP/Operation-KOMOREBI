module
public import DiagonalTruncation
import all SmallCoreNorms
import all DiagonalTruncation
public import Mathlib.Tactic
/-! Author: Komorebi P. Thin square-root factors with exactly min(d,k) columns.
Zero singular values never require division. -/
public section
set_option autoImplicit false
namespace KomorebiPaperVIII.SmallCore
open scoped BigOperators Matrix Classical
variable {m n : Type*} [Fintype m] [Fintype n] {d : ℕ}

abbrev KeptColumn (d k : ℕ) := {i : Fin d // i.val < k}

theorem keptColumn_card (k : ℕ) : Fintype.card (KeptColumn d k) = min d k := by
  simpa only [KeptColumn, Fintype.card_subtype] using (Fin.card_filter_val_lt (n := d) (m := k))

noncomputable def rootMask (σ : Fin d → ℝ) (k : ℕ) :
    Matrix (Fin d) (KeptColumn d k) ℂ :=
  (rootKept σ k).submatrix id Subtype.val

theorem rootKept_tail_zero (σ : Fin d → ℝ) (k : ℕ) (i j : Fin d)
    (hj : ¬ j.val < k) : rootKept σ k i j = 0 := by
  by_cases h : i = j
  · subst i
    simp [rootKept,diag,kept,hj]
  · simp [rootKept,diag,Matrix.diagonal,h]

omit [Fintype m] [Fintype n] in
theorem drop_zero_columns (A : Matrix m (Fin d) ℂ) (B : Matrix n (Fin d) ℂ)
    (k : ℕ) (hA : ∀ i j, ¬ j.val < k → A i j = 0) :
    (A.submatrix id (Subtype.val : KeptColumn d k → Fin d)) *
      (B.submatrix id (Subtype.val : KeptColumn d k → Fin d))ᴴ = A*Bᴴ := by
  ext i j
  simp only [Matrix.mul_apply,Matrix.conjTranspose_apply,Matrix.submatrix_apply,id_eq]
  apply Fintype.sum_of_injective (Subtype.val : KeptColumn d k → Fin d) Subtype.val_injective
  · intro l hl
    have hnot : ¬ l.val < k := by
      intro h
      exact hl ⟨⟨l,h⟩,rfl⟩
    rw [hA i l hnot,zero_mul]
  · intro l
    rfl

theorem rootMask_square (σ : Fin d → ℝ) (hσ : ∀ i, 0 ≤ σ i) (k : ℕ) :
    rootMask σ k * (rootMask σ k)ᴴ = diag (kept σ k) := by
  unfold rootMask
  rw [drop_zero_columns _ _ k (rootKept_tail_zero σ k),rootKept_selfAdjoint,
    rootKept_square σ hσ]

omit [Fintype m] [Fintype n] in
theorem thin_factor_product (U : Matrix m (Fin d) ℂ) (V : Matrix n (Fin d) ℂ)
    (σ : Fin d → ℝ) (hσ : ∀ i, 0 ≤ σ i) (k : ℕ) :
    (U*rootMask σ k)*(V*rootMask σ k)ᴴ = lift U V (diag (kept σ k)) := by
  simp only [Matrix.conjTranspose_mul,Matrix.mul_assoc,lift]
  rw [←Matrix.mul_assoc (rootMask σ k) (rootMask σ k)ᴴ Vᴴ,rootMask_square σ hσ]

end KomorebiPaperVIII.SmallCore

-- SIXTH AXIOM AUDITS
#print axioms KomorebiPaperVIII.SmallCore.keptColumn_card
#print axioms KomorebiPaperVIII.SmallCore.rootKept_tail_zero
#print axioms KomorebiPaperVIII.SmallCore.drop_zero_columns
#print axioms KomorebiPaperVIII.SmallCore.rootMask_square
#print axioms KomorebiPaperVIII.SmallCore.thin_factor_product
#print axioms KomorebiPaperVIII.SmallCore.KeptColumn
#print axioms KomorebiPaperVIII.SmallCore.rootMask
