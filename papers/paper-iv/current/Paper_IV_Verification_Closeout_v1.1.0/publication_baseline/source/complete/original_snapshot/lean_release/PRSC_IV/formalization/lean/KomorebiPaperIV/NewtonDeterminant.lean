/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.ReciprocalCompletion
import Mathlib.LinearAlgebra.Matrix.Block
import Mathlib.Data.Nat.Factorial.BigOperators

namespace Komorebi.PaperIV
noncomputable section
open Matrix Finset
variable {K : Type*} [Field K] [CharZero K]

/-- Newton's lower Hessenberg matrix, including its negative superdiagonal. -/
def newtonHessenberg (p : ℕ → K) (n : ℕ) : Matrix (Fin n) (Fin n) K :=
  fun i j => (if j.val ≤ i.val then p (i.val+1-j.val) else 0) -
    (if j.val = i.val+1 then (i.val+1 : K) else 0)

omit [CharZero K] in
private theorem newton_column_sum (p b : ℕ → K) (n : ℕ)
    (hb : ∀ i, ∑ j ∈ range (i+1), b j * p (i+1-j) = (i+1 : K)*b (i+1))
    (i : Fin (n+1)) :
    (∑ j : Fin (n+1), b j.val * newtonHessenberg p (n+1) i j) =
      if i = Fin.last n then (n+1 : K)*b (n+1) else 0 := by
  have hi : i.val+1 ≤ n+1 := i.isLt
  simp only [newtonHessenberg, mul_sub, sum_sub_distrib]
  rw [Fin.sum_univ_eq_sum_range (f := fun j => b j * (if j ≤ i.val then p (i.val+1-j) else 0)),
    Fin.sum_univ_eq_sum_range (f := fun j => b j * (if j = i.val+1 then (i.val+1 : K) else 0))]
  have hl : (∑ j ∈ range (n+1), b j * (if j ≤ i.val then p (i.val+1-j) else 0)) =
      ∑ j ∈ range (i.val+1), b j*p (i.val+1-j) := by
    symm
    calc
      _ = ∑ j ∈ range (i.val+1), b j * (if j ≤ i.val then p (i.val+1-j) else 0) := by
        apply sum_congr rfl
        intro j hj
        simp only [show j ≤ i.val by have := mem_range.mp hj; omega, ite_true]
      _ = _ := sum_subset (range_mono hi) (by
        intro j _ hj
        simp only [show ¬ j ≤ i.val by simpa using hj, ite_false, mul_zero])
  rw [hl, hb]
  by_cases hiLast : i = Fin.last n
  · subst i
    simp only [Fin.val_last, ite_true]
    have hz : (∑ j ∈ range (n+1), b j * (if j = n+1 then (n+1 : K) else 0)) = 0 := by
      apply sum_eq_zero
      intro j hj
      simp only [show j ≠ n+1 by have := mem_range.mp hj; omega, ite_false, mul_zero]
    rw [hz, sub_zero]
  · have hil : i.val+1 < n+1 := by
      have hn : i.val ≠ n := by intro h; apply hiLast; exact Fin.ext h
      omega
    rw [sum_eq_single (i.val+1)]
    · simp [hiLast, mul_comm]
    · intro j _ hj
      simp only [hj, ite_false, mul_zero]
    · exact fun h => (h (mem_range.mpr hil)).elim

/-- The exact determinant solution of Newton's recurrence. -/
theorem newtonHessenberg_det (p b : ℕ → K) (hb0 : b 0 = 1)
    (hb : ∀ i, ∑ j ∈ range (i+1), b j*p (i+1-j) = (i+1 : K)*b (i+1))
    (n : ℕ) : (newtonHessenberg p n).det = (n.factorial : K)*b n := by
  classical
  cases n with
  | zero => simp [hb0, Matrix.det_isEmpty]
  | succ n =>
    let H := newtonHessenberg p (n+1)
    let C := H.updateCol 0 (fun i => if i = Fin.last n then (n+1 : K)*b (n+1) else 0)
    have hc : C.det = H.det := by
      have h := Matrix.det_updateCol_sum H 0 (fun j => b j.val)
      simp only [Fin.val_zero, hb0, smul_eq_mul, one_mul] at h
      have he : (fun i => if i = Fin.last n then (n+1 : K)*b (n+1) else 0) =
          (fun i => ∑ j, b j.val * H i j) := by
        funext i
        exact (newton_column_sum p b n hb i).symm
      change (H.updateCol 0 _).det = H.det
      rw [he]
      exact h
    have hm : C.submatrix (Fin.last n).succAbove Fin.succ =
        fun i j : Fin n => newtonHessenberg p (n+1) i.castSucc j.succ := by
      ext i j
      simp [C, H, Matrix.submatrix, Matrix.updateCol, Fin.succ_ne_zero]
    have ht : (C.submatrix (Fin.last n).succAbove Fin.succ).IsLowerTriangular := by
      rw [hm]
      intro i j hij
      simp only [newtonHessenberg, Fin.val_castSucc, Fin.val_succ]
      have hij' : i.val < j.val := hij
      simp [show ¬ j.val+1 ≤ i.val by omega, show j.val ≠ i.val by omega]
    have hd : (C.submatrix (Fin.last n).succAbove Fin.succ).det =
        (-1 : K)^n * (n.factorial : K) := by
      rw [Matrix.det_of_isLowerTriangular _ ht, hm]
      simp only [newtonHessenberg, Fin.val_castSucc, Fin.val_succ,
        Nat.not_succ_le_self, ite_false, ite_true, zero_sub]
      rw [Finset.prod_neg]
      simp only [card_univ, Fintype.card_fin]
      congr 1
      rw [Fin.prod_univ_eq_prod_range (f := fun j => (j : K)+1), Nat.factorial_eq_prod_range_add_one, Nat.cast_prod]
      apply prod_congr rfl
      intro j _
      simp
    rw [← hc, Matrix.det_succ_column_zero, sum_eq_single (Fin.last n)]
    · simp only [C, Matrix.updateCol_self, Fin.val_last, ite_true]
      rw [hd, Nat.factorial_succ, Nat.cast_mul, Nat.cast_add, Nat.cast_one]
      have hs : (-1 : K)^n * (-1)^n = 1 := by rw [← mul_pow]; simp
      calc
        _ = ((-1 : K)^n * (-1)^n) * ((n+1 : K)*(n.factorial : K)*b (n+1)) := by ring
        _ = _ := by rw [hs, one_mul]
    · intro i _ hi
      simp [C, hi]
    · simp

/-- The Newton determinant printed in Theorem 7.6. -/
theorem reciprocalOrdCoeff_newton_determinant (N n : ℕ) (r : K) :
    reciprocalOrdCoeff N n r = (n.factorial : K)⁻¹ *
      (newtonHessenberg (fun k => r*kappaCoeff N k) n).det := by
  have hb0 : reciprocalOrdCoeff N 0 r = 1 := by simp [reciprocalOrdCoeff]
  have hb (i : ℕ) : ∑ j ∈ range (i+1), reciprocalOrdCoeff N j r *
      (r*kappaCoeff N (i+1-j)) = (i+1 : K)*reciprocalOrdCoeff N (i+1) r := by
    have h := reciprocalOrdCoeff_newton N r i
    rw [Finset.Nat.sum_antidiagonal_eq_sum_range_succ_mk] at h
    rw [h, mul_sum]
    apply sum_congr rfl
    intro j hj
    have he : i-j+1=i+1-j := by have := mem_range.mp hj; omega
    rw [he]
    ring
  rw [newtonHessenberg_det _ _ hb0 hb]
  have hf : (n.factorial : K) ≠ 0 := by exact_mod_cast n.factorial_ne_zero
  field_simp

end
end Komorebi.PaperIV
