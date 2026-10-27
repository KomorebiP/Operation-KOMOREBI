module
public import SmallCoreTransfer
import all SmallCoreNorms
import all SmallCoreTransfer
public import Mathlib.Tactic
/-! Author: Komorebi P. Truncated nonnegative diagonal data, exact errors and rank.
Indices are zero-based and all tail values vanish beyond the diagonal length. -/
public section
set_option autoImplicit false
namespace KomorebiPaperVIII.SmallCore
open scoped BigOperators Matrix Classical
variable {d : ℕ}
def kept (σ : Fin d → ℝ) (k : ℕ) (i : Fin d) : ℝ := if i.val < k then σ i else 0
def discarded (σ : Fin d → ℝ) (k : ℕ) (i : Fin d) : ℝ := if i.val < k then 0 else σ i
noncomputable def diag (σ : Fin d → ℝ) : Matrix (Fin d) (Fin d) ℂ :=
  Matrix.diagonal (fun i => (σ i : ℂ))
noncomputable def nextSingular (σ : Fin d → ℝ) (k : ℕ) : ℝ :=
  if h : k < d then σ ⟨k,h⟩ else 0
noncomputable def tailEnergy (σ : Fin d → ℝ) (k : ℕ) : ℝ :=
  ∑ i, (discarded σ k i)^2
noncomputable def rootKept (σ : Fin d → ℝ) (k : ℕ) : Matrix (Fin d) (Fin d) ℂ :=
  diag (fun i => Real.sqrt (kept σ k i))

theorem kept_nonneg (σ : Fin d → ℝ) (hσ : ∀ i, 0 ≤ σ i) (k : ℕ) (i : Fin d) :
    0 ≤ kept σ k i := by unfold kept; split_ifs <;> positivity

theorem discarded_nonneg (σ : Fin d → ℝ) (hσ : ∀ i, 0 ≤ σ i) (k : ℕ) (i : Fin d) :
    0 ≤ discarded σ k i := by unfold discarded; split_ifs <;> positivity

theorem diagonal_residual (σ : Fin d → ℝ) (k : ℕ) :
    diag σ - diag (kept σ k) = diag (discarded σ k) := by
  unfold diag
  rw [←Matrix.diagonal_sub]
  congr 1
  funext i
  by_cases hi : i.val<k <;> simp [kept,discarded,hi]

theorem rank_kept_le (σ : Fin d → ℝ) (k : ℕ) : (diag (kept σ k)).rank ≤ k := by
  unfold diag
  rw [Matrix.rank_diagonal]
  let f : {i : Fin d // (kept σ k i : ℂ) ≠ 0} → Fin k := fun i =>
    ⟨i.val.val,by
      by_contra h
      have he : kept σ k i.val = 0 := by simp [kept,h]
      exact i.property (by rw [he]; rfl)⟩
  have hf : Function.Injective f := by
    intro i j he
    apply Subtype.ext
    apply Fin.ext
    exact congrArg Fin.val he
  simpa only [Fintype.card_fin] using Fintype.card_le_of_injective f hf

theorem rootKept_selfAdjoint (σ : Fin d → ℝ) (k : ℕ) :
    (rootKept σ k)ᴴ = rootKept σ k := by
  simp [rootKept,diag,Matrix.conjTranspose_diagonal]

theorem rootKept_square (σ : Fin d → ℝ) (hσ : ∀ i, 0 ≤ σ i) (k : ℕ) :
    rootKept σ k * rootKept σ k = diag (kept σ k) := by
  unfold rootKept diag
  rw [Matrix.diagonal_mul_diagonal]
  congr 1
  funext i
  norm_cast
  nlinarith [Real.sq_sqrt (kept_nonneg σ hσ k i)]

theorem discarded_le_next (σ : Fin d → ℝ) (hσ : ∀ i, 0 ≤ σ i)
    (hsort : Antitone σ) (k : ℕ) (i : Fin d) : discarded σ k i ≤ nextSingular σ k := by
  by_cases hk : k<d
  · simp only [nextSingular,hk,dif_pos]
    by_cases hi : i.val<k
    · simp only [discarded,hi,ite_true]; exact hσ _
    · simp only [discarded,hi,ite_false]
      exact hsort (by show k ≤ i.val; omega)
  · have hi : i.val<k := by omega
    simp [discarded,hi,nextSingular,hk]

section Operator
open scoped Matrix.Norms.L2Operator

theorem spectral_diagonal_tail (σ : Fin d → ℝ) (hσ : ∀ i, 0 ≤ σ i)
    (hsort : Antitone σ) (k : ℕ) :
    spectralNorm (diag (discarded σ k)) = nextSingular σ k := by
  unfold spectralNorm diag
  rw [Matrix.l2_opNorm_diagonal]
  have hn : 0 ≤ nextSingular σ k := by unfold nextSingular; split_ifs <;> positivity
  apply le_antisymm
  · apply (pi_norm_le_iff_of_nonneg hn).mpr
    intro i
    simpa only [Complex.norm_real,Real.norm_eq_abs,
      abs_of_nonneg (discarded_nonneg σ hσ k i)] using discarded_le_next σ hσ hsort k i
  · by_cases hk : k<d
    · have hb := norm_le_pi_norm (fun i : Fin d => (discarded σ k i : ℂ)) ⟨k,hk⟩
      simpa [nextSingular,hk,discarded,Complex.norm_real,Real.norm_eq_abs,
        abs_of_nonneg (hσ ⟨k,hk⟩)] using hb
    · simp only [nextSingular,hk,dif_neg]; positivity
end Operator

section Frobenius
open scoped Matrix.Norms.Frobenius

theorem frobenius_diagonal_tail (σ : Fin d → ℝ) (k : ℕ) :
    frobeniusNorm (diag (discarded σ k))^2 = tailEnergy σ k := by
  unfold frobeniusNorm diag tailEnergy
  rw [Matrix.frobenius_norm_diagonal,EuclideanSpace.norm_sq_eq]
  simp [Complex.norm_real,Real.norm_eq_abs,sq_abs]
end Frobenius
end KomorebiPaperVIII.SmallCore
