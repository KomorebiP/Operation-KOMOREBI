/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.CompanionCompletion

/-! # Canonical roots and analytic growth bounds -/

namespace Komorebi.PaperIV
noncomputable section

def canonicalPrimitiveRoot (N : ℕ) : ℂ :=
  Complex.exp (2 * (Real.pi : ℂ) * Complex.I / N)

def canonicalSignedRoot (N : ℕ) : ℂ :=
  Complex.exp ((Real.pi : ℂ) * Complex.I / N)

theorem canonicalPrimitiveRoot_isPrimitive {N : ℕ} (hN : 0 < N) :
    IsPrimitiveRoot (canonicalPrimitiveRoot N) N :=
  Complex.isPrimitiveRoot_exp N hN.ne'

theorem canonicalSignedRoot_pow {N : ℕ} (hN : 0 < N) :
    canonicalSignedRoot N ^ N = -1 := by
  unfold canonicalSignedRoot
  rw [← Complex.exp_nat_mul]
  have hn : (N : ℂ) ≠ 0 := by exact_mod_cast hN.ne'
  have he : (N : ℂ) * ((Real.pi : ℂ) * Complex.I / N) = (Real.pi : ℂ) * Complex.I := by
    field_simp
  rw [he, Complex.exp_pi_mul_I]

/-- The determinant statement requires no root witnesses from the caller. -/
theorem signedFundamentalMatrix_det_one {N : ℕ} (hN : 1 < N) (z : ℂ) :
    (signedFundamentalMatrix N z).det = 1 :=
  signedFundamentalMatrix_det hN (canonicalPrimitiveRoot_isPrimitive (by omega))
    (canonicalSignedRoot_pow (by omega)) z

/-- Every root of minus one is on the unit circle. -/
theorem norm_signedRoot {N : ℕ} (hN : 0 < N) {rho : ℂ} (hrho : rho ^ N = -1) :
    ‖rho‖ = 1 := by
  apply Complex.norm_eq_one_of_pow_eq_one (n := N * 2)
  · rw [pow_mul, hrho]
    norm_num
  · omega

/-- The explicit global exponential-type upper bound from Proposition 11.2. -/
theorem norm_entireSigned_zero_le {N : ℕ} (hN : 0 < N)
    {omega rho : ℂ} (homega : IsPrimitiveRoot omega N) (hrho : rho ^ N = -1)
    (z : ℂ) :
    ‖entireSigned N 0 omega rho z‖ ≤ Real.exp ‖z‖ := by
  rw [entireSigned_zero_eq_average, norm_mul, norm_inv, Complex.norm_natCast]
  have homegaNorm : ‖omega‖ = 1 :=
    Complex.norm_eq_one_of_pow_eq_one homega.pow_eq_one hN.ne'
  have ht (l : ℕ) : ‖Complex.exp ((rho * omega ^ l) * z)‖ ≤ Real.exp ‖z‖ := by
    rw [Complex.norm_exp]
    apply Real.exp_le_exp.mpr
    calc
      _ ≤ ‖(rho * omega ^ l) * z‖ := Complex.re_le_norm _
      _ = ‖z‖ := by simp [norm_pow, norm_signedRoot hN hrho, homegaNorm]
  calc
    _ ≤ (N : ℝ)⁻¹ * ∑ l ∈ Finset.range N, ‖Complex.exp ((rho * omega ^ l) * z)‖ :=
      mul_le_mul_of_nonneg_left (norm_sum_le _ _) (by positivity)
    _ ≤ (N : ℝ)⁻¹ * ∑ _l ∈ Finset.range N, Real.exp ‖z‖ :=
      mul_le_mul_of_nonneg_left (Finset.sum_le_sum (fun l _ => ht l)) (by positivity)
    _ = Real.exp ‖z‖ := by simp [hN.ne']

end
end Komorebi.PaperIV
