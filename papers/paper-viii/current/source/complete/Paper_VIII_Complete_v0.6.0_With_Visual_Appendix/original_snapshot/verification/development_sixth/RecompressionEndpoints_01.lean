module
public import SmallCoreRecompression
import all SmallCoreNorms
import all SmallCoreTransfer
import all CompactTruncation
import all DiagonalTruncation
import all SmallCoreRecompression
public import Mathlib.Tactic
/-! Author: Komorebi P. Constructed SVD certificates and truncation endpoints.
This supplies nonvacuous zero/diagonal instances, not a general SVD algorithm. -/
public section
set_option autoImplicit false
namespace KomorebiPaperVIII.SmallCore
open scoped BigOperators Matrix Classical
variable {m n r s : Type*} [Fintype m] [Fintype n] [Fintype r] [Fintype s]
  [DecidableEq m] [DecidableEq n] [DecidableEq r] [DecidableEq s] {d : ℕ}

noncomputable def diagonalSVD (σ : Fin d → ℝ) (hσ : ∀ i, 0 ≤ σ i)
    (hsort : Antitone σ) : OrderedThinSVD (diag σ) d where
  left := 1
  right := 1
  values := σ
  left_isometry := by simp
  right_isometry := by simp
  nonnegative := hσ
  sorted := hsort
  reconstruction := by simp [lift]

omit [DecidableEq r] [DecidableEq s] in
noncomputable def zeroSVD (G : Matrix r s ℂ) (hG : G=0) : OrderedThinSVD G 0 where
  left := 0
  right := 0
  values := Fin.elim0
  left_isometry := by ext i; exact i.elim0
  right_isometry := by ext i; exact i.elim0
  nonnegative := fun i => i.elim0
  sorted := by intro i; exact i.elim0
  reconstruction := by simp [lift,hG]

theorem kept_zero (σ : Fin d → ℝ) : kept σ 0=0 := by
  funext i
  simp [kept]

theorem kept_all (σ : Fin d → ℝ) (k : ℕ) (hk : d ≤ k) : kept σ k=σ := by
  funext i
  have hi : i.val<k := lt_of_lt_of_le i.isLt hk
  simp [kept,hi]

theorem tailEnergy_zero_of_full (σ : Fin d → ℝ) (k : ℕ) (hk : d ≤ k) :
    tailEnergy σ k=0 := by
  unfold tailEnergy
  apply Finset.sum_eq_zero
  intro i _
  have hi : i.val<k := lt_of_lt_of_le i.isLt hk
  simp [discarded,hi]

theorem nextSingular_zero_of_full (σ : Fin d → ℝ) (k : ℕ) (hk : d ≤ k) :
    nextSingular σ k=0 := by simp [nextSingular,not_lt_of_ge hk]

omit [Fintype m] [Fintype n] [DecidableEq m] [DecidableEq n]
    [DecidableEq r] [DecidableEq s] in
theorem recompression_rank_zero (Q : Matrix m r ℂ) (V : Matrix n s ℂ)
    {G : Matrix r s ℂ} (svd : OrderedThinSVD G d) :
    recompressLeft Q svd 0*(recompressRight V svd 0)ᴴ = 0 := by
  rw [recompressed_product,kept_zero]
  simp [lift,diag]

omit [Fintype m] [Fintype n] [DecidableEq m] [DecidableEq n]
    [DecidableEq r] [DecidableEq s] in
theorem recompression_full (Q : Matrix m r ℂ) (V : Matrix n s ℂ)
    {G : Matrix r s ℂ} (svd : OrderedThinSVD G d) (k : ℕ) (hk : d ≤ k) :
    recompressLeft Q svd k*(recompressRight V svd k)ᴴ = lift Q V G := by
  rw [recompressed_product,kept_all _ k hk,←lift_comp]
  exact congrArg (lift Q V) svd.reconstruction.symm

end KomorebiPaperVIII.SmallCore
