module
public import Mathlib.LinearAlgebra.Matrix.Circulant
public import Mathlib.Algebra.BigOperators.Fin
public import Mathlib.Tactic

/-!
Author: Komorebi P. Paper VIII 4.4.
Actual zero-padding and the actual circulant of length n+n. The diagonal
uses c[0]; r[0] is unused. No symmetry or Hermiticity is required.
-/
@[expose] public section
set_option autoImplicit false
namespace KomorebiPaperVIII
open Matrix
open scoped BigOperators
variable {n : ℕ} [NeZero n]

def toeplitzMatrix (c r : Fin n → ℂ) : Matrix (Fin n) (Fin n) ℂ :=
  fun i j => if j.val ≤ i.val then c (Fin.ofNat n (i.val-j.val))
    else r (Fin.ofNat n (j.val-i.val))

def toeplitzGenerator (c r : Fin n → ℂ) (k : Fin (n+n)) : ℂ :=
  if k.val < n then c (Fin.ofNat n k.val)
  else if k.val = n then 0 else r (Fin.ofNat n (n+n-k.val))

def zeroPad (x : Fin n → ℂ) : Fin (n+n) → ℂ := Fin.addCases x (fun _ => 0)

theorem toeplitz_circulant_block (c r : Fin n → ℂ) (i j : Fin n) :
    Matrix.circulant (toeplitzGenerator c r) (Fin.castAdd n i) (Fin.castAdd n j) =
      toeplitzMatrix c r i j := by
  unfold Matrix.circulant toeplitzMatrix
  simp only [Matrix.of_apply]
  by_cases h : j.val ≤ i.val
  · have hj : Fin.castAdd n j ≤ Fin.castAdd n i := h
    have hd : i.val - j.val < n := lt_of_le_of_lt (Nat.sub_le _ _) i.isLt
    simp [toeplitzGenerator, Fin.sub_val_of_le hj, hd, h]
  · have hj : Fin.castAdd n i < Fin.castAdd n j := lt_of_not_ge h
    have hv := Fin.coe_sub_iff_lt.mpr hj
    have hlow : ¬ n+n+i.val-j.val < n := by omega
    have hneq : n+n+i.val-j.val ≠ n := by omega
    have hsub : n+n-(n+n+i.val-j.val) = j.val-i.val := by omega
    simp [toeplitzGenerator, hv, hlow, hneq, hsub, h]

omit [NeZero n] in
theorem zero_pad_left (x : Fin n → ℂ) (i : Fin n) :
    zeroPad x (Fin.castAdd n i) = x i := by
  simp [zeroPad]

omit [NeZero n] in
theorem zero_pad_right (x : Fin n → ℂ) (i : Fin n) :
    zeroPad x (Fin.natAdd n i) = 0 := by
  exact Fin.addCases_right _ _ _

theorem toeplitz_embedding_action (c r x : Fin n → ℂ) (i : Fin n) :
    (Matrix.circulant (toeplitzGenerator c r) *ᵥ zeroPad x) (Fin.castAdd n i) =
      (toeplitzMatrix c r *ᵥ x) i := by
  simp only [Matrix.mulVec, dotProduct, Fin.sum_univ_add, zero_pad_left, zero_pad_right,
    mul_zero, Finset.sum_const_zero, add_zero, toeplitz_circulant_block]

theorem toeplitz_generator_first_half (c r : Fin n → ℂ) (i : Fin n) :
    toeplitzGenerator c r (Fin.castAdd n i) = c i := by
  simp [toeplitzGenerator, i.isLt, Fin.ofNat_eq_cast]

theorem toeplitz_generator_middle (c r : Fin n → ℂ) :
    toeplitzGenerator c r ⟨n, by have := NeZero.pos n; omega⟩ = 0 := by
  simp [toeplitzGenerator]

end KomorebiPaperVIII

-- FINAL AXIOM AUDITS
#print axioms KomorebiPaperVIII.toeplitz_circulant_block
#print axioms KomorebiPaperVIII.zero_pad_left
#print axioms KomorebiPaperVIII.zero_pad_right
#print axioms KomorebiPaperVIII.toeplitz_embedding_action
#print axioms KomorebiPaperVIII.toeplitz_generator_first_half
#print axioms KomorebiPaperVIII.toeplitz_generator_middle
