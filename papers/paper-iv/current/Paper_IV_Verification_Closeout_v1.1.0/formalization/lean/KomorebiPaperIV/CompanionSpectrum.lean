/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.FiniteModels
import Mathlib.LinearAlgebra.Matrix.Charpoly.Basic
import Mathlib.Algebra.Polynomial.Degree.IsMonicOfDegree
import Mathlib.LinearAlgebra.Matrix.Charpoly.Eigs
import Mathlib.Analysis.Complex.Polynomial.Basic
import Mathlib.FieldTheory.Separable

/-! # The exact characteristic polynomial of the signed companion

The first column detects every coefficient of a polynomial of degree below N.
Together with Cayley--Hamilton this derives the characteristic polynomial.
-/

namespace Komorebi.PaperIV
noncomputable section
open Polynomial

/-- The first column of a polynomial in J retains all coefficients below N. -/
theorem aeval_signedShiftMatrix_first_column {N : ℕ} (hN : 0 < N)
    (P : ℂ[X]) (hP : P.natDegree < N) (p : Fin N) :
    aeval (signedShiftMatrix (R := ℂ) N) P p ⟨0, hN⟩ = P.coeff p.val := by
  rw [aeval_eq_sum_range' hP]
  simp only [Matrix.sum_apply, Matrix.smul_apply, smul_eq_mul]
  rw [Finset.sum_eq_single p.val]
  · rw [signedShiftMatrix_pow_apply N p.val hN]
    simp [Nat.mod_eq_of_lt p.isLt, Nat.div_eq_of_lt p.isLt]
  · intro m hm hmp
    have hmN : m < N := Finset.mem_range.mp hm
    rw [signedShiftMatrix_pow_apply N m hN]
    simp [Nat.mod_eq_of_lt hmN, Ne.symm hmp]
  · simp [p.isLt]

/-- No nonzero polynomial of degree below N annihilates the signed shift. -/
theorem signedShiftMatrix_no_small_annihilator {N : ℕ} (hN : 0 < N)
    (P : ℂ[X]) (hP : P.natDegree < N)
    (hzero : aeval (signedShiftMatrix (R := ℂ) N) P = 0) : P = 0 := by
  ext m
  by_cases hm : m < N
  · have h := aeval_signedShiftMatrix_first_column hN P hP ⟨m, hm⟩
    rw [hzero] at h
    simpa using h.symm
  · simp [coeff_eq_zero_of_natDegree_lt (show P.natDegree < m by omega)]

/-- The signed relation is an actual annihilating polynomial. -/
theorem aeval_signedShiftMatrix_X_pow_add_one {N : ℕ} (hN : 0 < N) :
    aeval (signedShiftMatrix (R := ℂ) N) (X ^ N + 1 : ℂ[X]) = 0 := by
  simp only [map_add, map_pow, aeval_X, map_one, signedShiftMatrix_pow_order N hN]
  exact neg_add_cancel 1

/-- The companion characteristic polynomial is exactly X^N + 1. -/
theorem signedShiftMatrix_charpoly {N : ℕ} (hN : 0 < N) :
    (signedShiftMatrix (R := ℂ) N).charpoly = (X ^ N + 1 : ℂ[X]) := by
  let P := (signedShiftMatrix (R := ℂ) N).charpoly
  have hp : P.IsMonicOfDegree N := by
    exact ⟨by simp [P], Matrix.charpoly_monic _⟩
  have hq : (X ^ N + 1 : ℂ[X]).IsMonicOfDegree N := by
    exact ⟨by simp, by simpa using monic_X_pow_add_C (1 : ℂ) hN.ne'⟩
  have hdeg := hp.natDegree_sub_lt hN.ne' hq
  apply sub_eq_zero.mp
  apply signedShiftMatrix_no_small_annihilator hN _ hdeg
  rw [map_sub, Matrix.aeval_self_charpoly, aeval_signedShiftMatrix_X_pow_add_one hN,
    sub_self]

/-- The spectrum consists of precisely the Nth roots of minus one. -/
theorem signedShiftMatrix_mem_spectrum_iff {N : ℕ} (hN : 0 < N) (eta : ℂ) :
    eta ∈ spectrum ℂ (signedShiftMatrix (R := ℂ) N) ↔ eta ^ N = -1 := by
  rw [Matrix.mem_spectrum_iff_isRoot_charpoly, signedShiftMatrix_charpoly hN]
  simp [IsRoot.def, add_eq_zero_iff_eq_neg]

/-- Every characteristic root is simple. -/
theorem signedShiftMatrix_charpoly_separable {N : ℕ} (hN : 0 < N) :
    (signedShiftMatrix (R := ℂ) N).charpoly.Separable := by
  rw [signedShiftMatrix_charpoly hN]
  simpa using separable_X_pow_sub_C (-1 : ℂ)
    (by exact_mod_cast hN.ne') (by norm_num)

/-- There are exactly N characteristic roots, counted with multiplicity. -/
theorem signedShiftMatrix_charpoly_roots_card {N : ℕ} (hN : 0 < N) :
    (signedShiftMatrix (R := ℂ) N).charpoly.roots.card = N := by
  rw [signedShiftMatrix_charpoly hN,
    (IsAlgClosed.splits _).natDegree_eq_card_roots.symm]
  simp

/-- The root multiset has no repeated elements. -/
theorem signedShiftMatrix_charpoly_roots_nodup {N : ℕ} (hN : 0 < N) :
    (signedShiftMatrix (R := ℂ) N).charpoly.roots.Nodup :=
  Polynomial.nodup_roots (signedShiftMatrix_charpoly_separable hN)

end
end Komorebi.PaperIV
