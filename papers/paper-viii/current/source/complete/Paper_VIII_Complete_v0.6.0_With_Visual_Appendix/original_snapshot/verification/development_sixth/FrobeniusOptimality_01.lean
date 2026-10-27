module
public import KernelFrame
public import DiagonalTruncation
import all SmallCoreNorms
import all KernelFrame
import all DiagonalTruncation
import all SmallCoreTransfer
public import Mathlib.Tactic
/-! Author: Komorebi P. Frobenius low-rank lower bound proved from kernel weights.
No Eckart--Young optimality assumption is used in this module. -/
public section
set_option autoImplicit false
namespace KomorebiPaperVIII.SmallCore
open scoped BigOperators Matrix Classical
variable {d : ℕ}

theorem tail_indicator_sum (k : ℕ) (hk : k ≤ d) :
    (∑ i : Fin d, if i.val < k then (0:ℝ) else 1) = (d-k : ℕ) := by
  have htop : (∑ i : Fin d, if i.val < k then (1:ℝ) else 0) = k := by
    rw [←Finset.natCast_card_filter]
    simp [Fin.card_filter_val_lt,Nat.min_eq_right hk]
  have hsplit : (∑ i : Fin d, if i.val < k then (1:ℝ) else 0) +
      (∑ i : Fin d, if i.val < k then (0:ℝ) else 1) = d := by
    rw [←Finset.sum_add_distrib]
    have he : (fun i : Fin d => (if i.val<k then (1:ℝ) else 0)+
        (if i.val<k then (0:ℝ) else 1)) = fun _ => (1:ℝ) := by
      funext i; split_ifs <;> norm_num
    rw [he]
    simp
  rw [htop] at hsplit
  rw [Nat.cast_sub hk]
  linarith

/-- A decreasing nonnegative cost is minimized by placing the available mass at the tail. -/
theorem weighted_tail_lower (a w : Fin d → ℝ) (ha : ∀ i, 0 ≤ a i)
    (hsort : Antitone a) (hw0 : ∀ i, 0 ≤ w i) (hw1 : ∀ i, w i ≤ 1)
    (k : ℕ) (hw : (d-k : ℕ) ≤ ∑ i,w i) :
    (∑ i, if i.val<k then (0:ℝ) else a i) ≤ ∑ i, a i*w i := by
  by_cases hk : k<d
  · let μ := a ⟨k,hk⟩
    have hμ : 0 ≤ μ := ha _
    have hp : ∀ i : Fin d,
        (if i.val<k then 0 else a i) + μ*(w i-(if i.val<k then 0 else 1)) ≤ a i*w i := by
      intro i
      by_cases hi : i.val<k
      · have hle : μ ≤ a i := hsort (by show i.val ≤ k; omega)
        simp only [hi,ite_true,zero_add,sub_zero]
        exact mul_le_mul_of_nonneg_right hle (hw0 i)
      · have hle : a i ≤ μ := hsort (by show k ≤ i.val; omega)
        simp only [hi,ite_false]
        nlinarith [mul_nonneg (sub_nonneg.mpr hle) (sub_nonneg.mpr (hw1 i))]
    have hs := Finset.sum_le_sum (fun i (_ : i ∈ (Finset.univ : Finset (Fin d))) => hp i)
    simp only [Finset.sum_add_distrib,Finset.mul_sum,Finset.sum_sub_distrib] at hs
    have ht := tail_indicator_sum (d:=d) k hk.le
    have hz : 0 ≤ μ*((∑ i,w i)-(d-k : ℕ)) := mul_nonneg hμ (sub_nonneg.mpr hw)
    rw [←Finset.mul_sum,Finset.sum_sub_distrib,ht] at hs
    linarith
  · have he : ∀ i : Fin d, i.val<k := fun i => by omega
    simp only [he,ite_true,Finset.sum_const_zero]
    exact Finset.sum_nonneg (fun i _ => mul_nonneg (ha i) (hw0 i))

section Frobenius
open scoped Matrix.Norms.Frobenius

theorem diagonal_frame_energy {r : Type*} [Fintype r] (σ : Fin d → ℝ)
    (Q : Matrix (Fin d) r ℂ) :
    frobeniusNorm (diag σ * Q)^2 = ∑ i, σ i^2 * rowWeight Q i := by
  unfold frobeniusNorm
  rw [Matrix.frobenius_norm_def]
  simp only [Real.rpow_two,←Real.sqrt_eq_rpow]
  rw [Real.sq_sqrt (Finset.sum_nonneg (fun i _ => Finset.sum_nonneg
    (fun j _ => sq_nonneg ‖(diag σ*Q) i j‖)))]
  simp [diag,Matrix.diagonal_mul,norm_mul,mul_pow,Complex.norm_real,
    Real.norm_eq_abs,sq_abs,rowWeight,Finset.mul_sum]

theorem diagonal_frobenius_lower (σ : Fin d → ℝ) (hσ : ∀ i, 0 ≤ σ i)
    (hsort : Antitone σ) (k : ℕ) (B : Matrix (Fin d) (Fin d) ℂ) (hB : B.rank≤k) :
    tailEnergy σ k ≤ frobeniusNorm (diag σ-B)^2 := by
  let Q := kernelFrame B
  have hQ : Qᴴ*Q=1 := kernelFrame_isometry B
  have hw : (d-k : ℕ) ≤ ∑ i,rowWeight Q i := by
    rw [rowWeight_sum Q hQ]
    simp only [Fintype.card_fin]
    have hn := kernel_rank_nullity B
    simp only [Fintype.card_fin] at hn
    exact_mod_cast (by omega : d-k ≤ kernelDim B)
  have hsort2 : Antitone (fun i => σ i^2) := by
    intro i j hij
    have hle := hsort hij
    nlinarith [hσ i,hσ j]
  have hl := weighted_tail_lower (fun i => σ i^2) (rowWeight Q)
    (fun i => sq_nonneg _) hsort2 (rowWeight_nonneg Q) (rowWeight_le_one Q hQ) k hw
  have he : tailEnergy σ k = ∑ i, if i.val<k then (0:ℝ) else σ i^2 := by
    unfold tailEnergy discarded
    apply Finset.sum_congr rfl
    intro i _
    split_ifs <;> simp
  rw [←he,←diagonal_frame_energy σ Q] at hl
  have hc := frobenius_right_compress_le Q hQ (diag σ-B)
  have hbq : (diag σ-B)*Q=diag σ*Q := by
    rw [Matrix.sub_mul,mul_kernelFrame,sub_zero]
  rw [hbq] at hc
  change ‖diag σ*Q‖^2 ≤ frobeniusNorm (diag σ-B)^2 at hl ⊢
  nlinarith [norm_nonneg (diag σ*Q),norm_nonneg (diag σ-B)]

theorem diagonal_frobenius_best (σ : Fin d → ℝ) (hσ : ∀ i, 0 ≤ σ i)
    (hsort : Antitone σ) (k : ℕ) :
    BestRank frobeniusNorm (diag σ) (diag (kept σ k)) k := by
  refine ⟨rank_kept_le σ k,fun B hB => ?_⟩
  have hl := diagonal_frobenius_lower σ hσ hsort k B hB
  have he := frobenius_diagonal_tail σ k
  rw [←diagonal_residual] at he
  unfold frobeniusNorm at *
  nlinarith [norm_nonneg (diag σ-diag (kept σ k)),norm_nonneg (diag σ-B)]
end Frobenius
end KomorebiPaperVIII.SmallCore
