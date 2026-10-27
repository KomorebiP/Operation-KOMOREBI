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
    field_simp [hs]
    nlinarith [hsq]
  unfold fourierScale
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
    Complex.star_def, Complex.conj_ofReal]
  rw [← AddChar.map_neg_eq_conj, neg_neg, mul_comm j i]
  ring

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
    _ = _ := by
      field_simp
      simp only [Finset.mul_sum, mul_assoc]

theorem fourier_unitary :
    (fourierMatrix n)ᴴ * fourierMatrix n = 1 ∧
    fourierMatrix n * (fourierMatrix n)ᴴ = 1 := by
  have hnorm := fourier_scale_normalization (n := n)
  constructor
  · apply Matrix.ext_iff_mulVec.mpr
    intro x
    rw [← Matrix.mulVec_mulVec, fourier_action, fourier_adjoint_action,
      _root_.map_smul, LinearEquiv.symm_apply_apply, smul_smul, Matrix.one_mulVec]
    have hh : (fourierScale n * (n:ℂ)) * fourierScale n = 1 := by
      calc
        _ = (fourierScale n * fourierScale n) * (n:ℂ) := by ring
        _ = 1 := hnorm
    rw [hh, one_smul]
  · apply Matrix.ext_iff_mulVec.mpr
    intro x
    rw [← Matrix.mulVec_mulVec, fourier_adjoint_action, fourier_action,
      _root_.map_smul, LinearEquiv.apply_symm_apply, smul_smul, Matrix.one_mulVec]
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
  refine Fintype.sum_equiv (Equiv.subRight j) _ _ ?_
  intro a
  simp only [Equiv.subRight_apply]
  have hchar : ZMod.stdAddChar (-((a-j)*k)) * ZMod.stdAddChar (-(j*k)) =
      ZMod.stdAddChar (-(a*k)) := by
    rw [← AddChar.map_add_eq_mul]
    congr 1
    ring
  calc
    _ = (ZMod.stdAddChar (-((a-j)*k)) * ZMod.stdAddChar (-(j*k))) * (c (a-j)*x j) := by
      rw [hchar]
    _ = _ := by ring


/-- The diagonal intertwining identity precedes reconstruction. -/
theorem fourier_circulant_intertwine (c : ZMod n → ℂ) :
    fourierMatrix n * Matrix.circulant c = Matrix.diagonal (ZMod.dft c) * fourierMatrix n := by
  apply Matrix.ext_iff_mulVec.mpr
  intro x
  rw [← Matrix.mulVec_mulVec, ← Matrix.mulVec_mulVec, fourier_action, dft_circulant,
    fourier_action]
  ext k
  simp [Matrix.mulVec_diagonal, Pi.smul_apply]
  ring

theorem circulant_spectral_dft (c : ZMod n → ℂ) :
    Matrix.circulant c = (fourierMatrix n)ᴴ * Matrix.diagonal (ZMod.dft c) * fourierMatrix n := by
  calc
    _ = ((fourierMatrix n)ᴴ * fourierMatrix n) * Matrix.circulant c := by
      rw [(fourier_unitary (n := n)).1, Matrix.one_mul]
    _ = _ := by rw [Matrix.mul_assoc, fourier_circulant_intertwine, ← Matrix.mul_assoc]

theorem normalized_fourier_eigenvalues (c : ZMod n → ℂ) :
    (Real.sqrt (n:ℝ) : ℂ) • (fourierMatrix n *ᵥ c) = ZMod.dft c := by
  rw [fourier_action, smul_smul, fourier_scale_sqrt, one_smul]

/-- Exactly the normalized Fourier-matrix formula in the manuscript. -/
theorem circulant_spectral_representation (c : ZMod n → ℂ) :
    Matrix.circulant c = (fourierMatrix n)ᴴ *
      Matrix.diagonal ((Real.sqrt (n:ℝ) : ℂ) • (fourierMatrix n *ᵥ c)) * fourierMatrix n := by
  rw [normalized_fourier_eigenvalues, circulant_spectral_dft]

theorem circulant_fourier_application (c x : ZMod n → ℂ) :
    Matrix.circulant c *ᵥ x = (fourierMatrix n)ᴴ *ᵥ
      (fun k => ZMod.dft c k * (fourierMatrix n *ᵥ x) k) := by
  rw [circulant_spectral_dft, ← Matrix.mulVec_mulVec, ← Matrix.mulVec_mulVec]
  congr 1
  funext k
  exact Matrix.mulVec_diagonal _ _ _

end KomorebiPaperVIII

-- FINAL AXIOM AUDITS
#print axioms KomorebiPaperVIII.fourier_scale_normalization
#print axioms KomorebiPaperVIII.fourier_scale_sqrt
#print axioms KomorebiPaperVIII.fourier_matrix_exponential
#print axioms KomorebiPaperVIII.fourier_action
#print axioms KomorebiPaperVIII.fourier_adjoint_entry
#print axioms KomorebiPaperVIII.fourier_adjoint_action
#print axioms KomorebiPaperVIII.fourier_unitary
#print axioms KomorebiPaperVIII.dft_circulant
#print axioms KomorebiPaperVIII.fourier_circulant_intertwine
#print axioms KomorebiPaperVIII.circulant_spectral_dft
#print axioms KomorebiPaperVIII.normalized_fourier_eigenvalues
#print axioms KomorebiPaperVIII.circulant_spectral_representation
#print axioms KomorebiPaperVIII.circulant_fourier_application

#print axioms KomorebiPaperVIII.fourierMatrix
