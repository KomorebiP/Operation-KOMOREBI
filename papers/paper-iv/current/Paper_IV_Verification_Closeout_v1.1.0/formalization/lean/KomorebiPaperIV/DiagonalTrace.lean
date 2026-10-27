/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.DiagonalNuclear

namespace Komorebi.PaperIV
noncomputable section
open InnerProductSpace
open scoped InnerProductSpace Classical ENNReal
set_option maxHeartbeats 800000

theorem hilbertBasis_hasSum_squared_coordinates {ι E : Type*} [NormedAddCommGroup E]
    [InnerProductSpace ℂ E] (b : HilbertBasis ι ℂ E) (x : E) :
    HasSum (fun i => ‖⟪b i, x⟫_ℂ‖ ^ 2) (‖x‖ ^ 2) := by
  have h := lp.hasSum_norm (by norm_num : (0 : ℝ) < (2 : ℝ≥0∞).toReal) (b.repr x)
  simpa only [ENNReal.toReal_ofNat, Real.rpow_two, b.repr_apply_apply, b.repr.norm_map] using h

theorem diagonal_trace_double_summable {ι κ : Type} {a : ι → ℂ}
    (ha : Summable (fun i => ‖a i‖)) (b : HilbertBasis κ ℂ (lp (fun _ : ι => ℂ) 2)) :
    Summable (fun p : ι × κ => a p.1 * ⟪b p.2, diagonalHilbertBasis ι p.1⟫_ℂ *
      ⟪diagonalHilbertBasis ι p.1, b p.2⟫_ℂ) := by
  apply Summable.of_norm
  have hn (i : ι) (j : κ) :
      ‖a i * ⟪b j, diagonalHilbertBasis ι i⟫_ℂ * ⟪diagonalHilbertBasis ι i, b j⟫_ℂ‖ =
        ‖a i‖ * ‖⟪b j, diagonalHilbertBasis ι i⟫_ℂ‖ ^ 2 := by
    rw [norm_mul, norm_mul, norm_inner_symm]
    ring
  simp_rw [hn]
  apply (summable_prod_of_nonneg (fun p => by positivity)).mpr
  constructor
  · intro i
    simpa only using! (hilbertBasis_hasSum_squared_coordinates b (diagonalHilbertBasis ι i)).summable.mul_left ‖a i‖
  · simpa [tsum_mul_left, (hilbertBasis_hasSum_squared_coordinates b _).tsum_eq] using ha

def hilbertBasisTrace {ι E : Type*} [NormedAddCommGroup E] [InnerProductSpace ℂ E]
    (b : HilbertBasis ι ℂ E) (T : E →L[ℂ] E) : ℂ := ∑' i, ⟪b i, T (b i)⟫_ℂ

theorem diagonalOperator_trace_in_any_basis {ι κ : Type} {a : ι → ℂ}
    (ha : Summable (fun i => ‖a i‖)) (b : HilbertBasis κ ℂ (lp (fun _ : ι => ℂ) 2)) :
    HasSum (fun j => ⟪b j, diagonalOperator a (b j)⟫_ℂ) (∑' i, a i) := by
  have hsum := diagonal_trace_double_summable ha b
  have hj (j : κ) : HasSum (fun i => a i * ⟪b j, diagonalHilbertBasis ι i⟫_ℂ *
      ⟪diagonalHilbertBasis ι i, b j⟫_ℂ) ⟪b j, diagonalOperator a (b j)⟫_ℂ := by
    have h := (hasSum_apply (diagonalRankOne_summable ha).hasSum (b j)).mapL (innerSL ℂ (b j))
    simpa [diagonalOperator, diagonalRankOne, rankOne_apply, inner_smul_right, mul_comm, mul_left_comm, mul_assoc] using! h
  have hi (i : ι) : (∑' j, a i * ⟪b j, diagonalHilbertBasis ι i⟫_ℂ *
      ⟪diagonalHilbertBasis ι i, b j⟫_ℂ) = a i := by
    calc
      _ = a i * ∑' j, ⟪diagonalHilbertBasis ι i, b j⟫_ℂ * ⟪b j, diagonalHilbertBasis ι i⟫_ℂ := by
        rw [← tsum_mul_left]
        apply tsum_congr
        intro j
        ring
      _ = a i := by
        rw [b.tsum_inner_mul_inner, inner_self_eq_norm_sq_to_K, diagonalHilbertBasis_norm]
        simp
  have hs : Summable (fun j => ∑' i, a i * ⟪b j, diagonalHilbertBasis ι i⟫_ℂ *
      ⟪diagonalHilbertBasis ι i, b j⟫_ℂ) := hsum.prod_symm.prod
  have he : (∑' j, ∑' i, a i * ⟪b j, diagonalHilbertBasis ι i⟫_ℂ *
      ⟪diagonalHilbertBasis ι i, b j⟫_ℂ) = ∑' i, a i := by
    have ht : (∑' i, ∑' j, a i * ⟪b j, diagonalHilbertBasis ι i⟫_ℂ *
        ⟪diagonalHilbertBasis ι i, b j⟫_ℂ) =
        ∑' j, ∑' i, a i * ⟪b j, diagonalHilbertBasis ι i⟫_ℂ *
        ⟪diagonalHilbertBasis ι i, b j⟫_ℂ := hsum.prod_symm.tsum_comm
    exact ht.symm.trans (tsum_congr hi)
  have hh : HasSum (fun j => ∑' i, a i * ⟪b j, diagonalHilbertBasis ι i⟫_ℂ *
      ⟪diagonalHilbertBasis ι i, b j⟫_ℂ) (∑' i, a i) := by
    rw [← he]
    exact hs.hasSum
  simpa only [(hj _).tsum_eq] using hh

theorem diagonalOperator_trace_eq {ι κ : Type} {a : ι → ℂ}
    (ha : Summable (fun i => ‖a i‖)) (b : HilbertBasis κ ℂ (lp (fun _ : ι => ℂ) 2)) :
    hilbertBasisTrace b (diagonalOperator a) = ∑' i, a i :=
  (diagonalOperator_trace_in_any_basis ha b).tsum_eq

theorem diagonalOperator_pow_eq {ι : Type} {a : ι → ℂ}
    (ha : Summable (fun i => ‖a i‖)) (m : ℕ) (hm : Summable (fun i => ‖a i ^ m‖)) :
    diagonalOperator a ^ m = diagonalOperator (fun i => a i ^ m) := by
  ext x j
  rw [diagonalOperator_pow_apply ha, diagonalOperator_apply hm]

theorem diagonalOperator_pow_trace {ι κ : Type} {a : ι → ℂ}
    (ha : Summable (fun i => ‖a i‖)) (m : ℕ) (hm : Summable (fun i => ‖a i ^ m‖))
    (b : HilbertBasis κ ℂ (lp (fun _ : ι => ℂ) 2)) :
    hilbertBasisTrace b (diagonalOperator a ^ m) = ∑' i, a i ^ m := by
  rw [diagonalOperator_pow_eq ha m hm, diagonalOperator_trace_eq hm]

end
end Komorebi.PaperIV
