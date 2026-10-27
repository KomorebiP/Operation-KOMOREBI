module
public import Mathlib.Analysis.Fourier.ZMod
public import Mathlib.LinearAlgebra.Matrix.Circulant
public import Mathlib.Tactic

/-!
Author: Komorebi P. Paper VIII 4.3.
The actual unitary-normalized Fourier matrix diagonalizes the actual circulant.
The standard character is explicitly linked to the complex exponential.
-/
@[expose] public section
set_option autoImplicit false
namespace KomorebiPaperVIII
open Matrix ZMod
open scoped BigOperators
variable {n : ℕ} [NeZero n]

noncomputable def fourierScale (n : ℕ) : ℂ := ((Real.sqrt (n:ℝ))⁻¹ : ℝ)
noncomputable def fourierMatrix (n : ℕ) [NeZero n] : Matrix (ZMod n) (ZMod n) ℂ :=
  fun i j => fourierScale n * ZMod.stdAddChar (-(i*j))

theorem fourier_scale_normalization :
    fourierScale n * fourierScale n * (n:ℂ) = 1 := by
  have hn : (0:ℝ) < n := Nat.cast_pos.mpr (NeZero.pos n)
  have hsq : Real.sqrt (n:ℝ) * Real.sqrt (n:ℝ) = n := Real.mul_self_sqrt hn.le
  have hs : Real.sqrt (n:ℝ) ≠ 0 := (Real.sqrt_pos.mpr hn).ne'
  have h : (Real.sqrt (n:ℝ))⁻¹ * (Real.sqrt (n:ℝ))⁻¹ * (n:ℝ) = 1 := by
    rw [← hsq]
    field_simp
  exact_mod_cast h

theorem fourier_scale_sqrt : (Real.sqrt (n:ℝ) : ℂ) * fourierScale n = 1 := by
  have hs : Real.sqrt (n:ℝ) ≠ 0 := (Real.sqrt_pos.mpr (Nat.cast_pos.mpr (NeZero.pos n))).ne'
  unfold fourierScale
  norm_cast
  exact mul_inv_cancel₀ hs

theorem fourier_matrix_exponential (i j : ZMod n) :
    fourierMatrix n i j = fourierScale n *
      Complex.exp (-(2 * Real.pi * Complex.I * (i.val:ℂ) * (j.val:ℂ) / (n:ℂ))) := by
  unfold fourierMatrix
  have heq : ((-((i.val:ℤ)*(j.val:ℤ)) : ℤ) : ZMod n) = -(i*j) := by simp
  rw [← heq, ZMod.stdAddChar_coe]
  congr 2
  push_cast
  ring

theorem fourier_action (x : ZMod n → ℂ) :
    fourierMatrix n *ᵥ x = fourierScale n • ZMod.dft x := by
  ext k
  simp only [fourierMatrix, Matrix.mulVec, dotProduct, Pi.smul_apply,
    ZMod.dft_apply, smul_eq_mul, Finset.mul_sum]
  apply Finset.sum_congr rfl
  intro i _
  rw [mul_comm i k]
  ring

theorem fourier_adjoint_entry (i j : ZMod n) :
    (fourierMatrix n)ᴴ i j = fourierScale n * ZMod.stdAddChar (i*j) := by
  simp only [Matrix.conjTranspose_apply, fourierMatrix, star_mul, fourierScale,
    Complex.star_def, map_mul, Complex.conj_ofReal]
  rw [← AddChar.map_neg_eq_conj, neg_neg, mul_comm j i]

theorem fourier_adjoint_action (x : ZMod n → ℂ) :
    (fourierMatrix n)ᴴ *ᵥ x = (fourierScale n * (n:ℂ)) • ZMod.dft.symm x := by
  have hn : (n:ℂ) ≠ 0 := by exact_mod_cast NeZero.ne n
  ext k
  simp only [Matrix.mulVec, dotProduct, fourier_adjoint_entry, Pi.smul_apply,
    ZMod.invDFT_apply, smul_eq_mul, Finset.mul_sum]
  calc
    _ = fourierScale n * ∑ j, ZMod.stdAddChar (j*k) * x j := by
      rw [Finset.mul_sum]
      apply Finset.sum_congr rfl
      intro j _
      rw [mul_comm k j]
      ring
    _ = _ := by field_simp

theorem fourier_unitary :
    (fourierMatrix n)ᴴ * fourierMatrix n = 1 ∧
    fourierMatrix n * (fourierMatrix n)ᴴ = 1 := by
  have hnorm := fourier_scale_normalization (n := n)
  constructor
  · apply Matrix.ext_iff_mulVec.mpr
    intro x
    rw [← Matrix.mulVec_mulVec, fourier_action, fourier_adjoint_action,
      map_smul, LinearEquiv.symm_apply_apply, smul_smul, Matrix.one_mulVec]
    have hh : (fourierScale n * (n:ℂ)) * fourierScale n = 1 := by nlinarith [hnorm]
    rw [hh, one_smul]
  · apply Matrix.ext_iff_mulVec.mpr
    intro x
    rw [← Matrix.mulVec_mulVec, fourier_adjoint_action, fourier_action,
      map_smul, LinearEquiv.apply_symm_apply, smul_smul, Matrix.one_mulVec]
    have hh : fourierScale n * (fourierScale n * (n:ℂ)) = 1 := by rw [← mul_assoc, hnorm]
    rw [hh, one_smul]

/-- The convolution theorem uses an explicit bijective change of finite index. -/
theorem dft_circulant (c x : ZMod n → ℂ) :
    ZMod.dft (Matrix.circulant c *ᵥ x) = fun k => ZMod.dft c k * ZMod.dft x k := by
  funext k
  simp only [ZMod.dft_apply, Matrix.mulVec, dotProduct, Matrix.circulant_apply,
    smul_eq_mul, Finset.mul_sum, Finset.sum_mul]
  rw [Finset.sum_comm]
  apply Finset.sum_congr rfl
  intro j _
  rw [Finset.sum_comm]
  sorry

end KomorebiPaperVIII
