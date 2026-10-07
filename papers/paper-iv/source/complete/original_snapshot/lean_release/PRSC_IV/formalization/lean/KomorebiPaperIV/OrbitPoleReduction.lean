/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.LeadingPoleBounds

namespace Komorebi.PaperIV
noncomputable section
open Set Filter
open scoped Topology Classical

def leadingZeroWeight (N r m : ℕ) (ρ : ℂ) : ℂ :=
  ((-ρ * deriv (canonicalSignedDenominator N) ρ) ^ r)⁻¹ * ρ⁻¹ ^ m

theorem leadingZeroWeight_rotation {N : ℕ} (hN : 0 < N) {u : ℂ} (hu : u ^ N = 1)
    (r n : ℕ) (ρ : ℂ) : leadingZeroWeight N r (N*n) (u*ρ) = leadingZeroWeight N r (N*n) ρ := by
  have hd := canonicalSignedDenominator_derivative_rotation hN hu ρ
  have he : -(u*ρ) * deriv (canonicalSignedDenominator N) (u*ρ) =
      -ρ * deriv (canonicalSignedDenominator N) ρ := by
    calc
      _ = -ρ * (deriv (canonicalSignedDenominator N) (u*ρ) * u) := by ring
      _ = _ := by rw [hd]
  have hp : u ^ (N*n) = 1 := by rw [pow_mul, hu, one_pow]
  unfold leadingZeroWeight
  rw [he, inv_pow, mul_pow u ρ, hp, one_mul, ← inv_pow ρ]

theorem leadingPoleCoefficient_eq_zero_weights (S : Finset ℂ) (N r m : ℕ) :
    leadingPoleCoefficient S (canonicalPoleCoefficient (canonicalSignedDenominator N) r) r m =
      ((m+r-1).choose (r-1) : ℂ) * ∑ ρ ∈ S, leadingZeroWeight N r m ρ := by
  simp only [leadingPoleCoefficient, canonicalPoleCoefficient_leading, leadingZeroWeight]

/-- An equivalence records exactly the chosen representatives and all N
distinct rotations of each representative. -/
theorem leading_zero_sum_orbit_reduction {N : ℕ} (hN : 0 < N) {ω : ℂ}
    (hω : IsPrimitiveRoot ω N) (S T : Finset ℂ) (e : (T × Fin N) ≃ S)
    (he : ∀ p : T × Fin N, (e p).val = ω ^ p.2.val * p.1.val) (r n : ℕ) :
    (∑ ρ ∈ S, leadingZeroWeight N r (N*n) ρ) =
      (N : ℂ) * ∑ τ ∈ T, leadingZeroWeight N r (N*n) τ := by
  calc
    _ = ∑ ρ : S, leadingZeroWeight N r (N*n) ρ.val := (Finset.sum_coe_sort S _).symm
    _ = ∑ p : T × Fin N, leadingZeroWeight N r (N*n) (e p).val := (Equiv.sum_comp e _).symm
    _ = ∑ p : T × Fin N, leadingZeroWeight N r (N*n) p.1.val := by
      apply Finset.sum_congr rfl
      intro p _
      rw [he]
      apply leadingZeroWeight_rotation hN
      rw [← pow_mul, Nat.mul_comm p.2.val N, pow_mul, hω.pow_eq_one, one_pow]
    _ = (N : ℂ) * ∑ τ : T, leadingZeroWeight N r (N*n) τ.val := by
      rw [Fintype.sum_prod_type]
      simp [Finset.mul_sum, nsmul_eq_mul]
    _ = _ := by rw [Finset.sum_coe_sort]

/-- Corollary 13.3: the orbit-reduced main term has exactly N times the
representative sum; both proved error bounds are unchanged. -/
theorem reciprocalCoeff_orbit_leading_bound {N : ℕ} (hN : 0 < N) {ω : ℂ}
    (hω : IsPrimitiveRoot ω N) (S T : Finset ℂ) (e : (T × Fin N) ≃ S)
    (he : ∀ p : T × Fin N, (e p).val = ω ^ p.2.val * p.1.val)
    {R Rstar R₂ : ℝ} (hR : 0 < R) (hRR : R < Rstar) (hR₂ : Rstar < R₂)
    (hS : ∀ ρ ∈ S, ‖ρ‖ = R) (hroot : ∀ ρ ∈ S, canonicalSignedDenominator N ρ = 0)
    (hsimple : ∀ ρ ∈ S, deriv (canonicalSignedDenominator N) ρ ≠ 0)
    (hzeros : ∀ z : ℂ, ‖z‖ < R₂ → canonicalSignedDenominator N z = 0 → z ∈ S)
    {r : ℕ} (hr : 0 < r) :
    ∃ C : ℝ, ∀ n : ℕ, 1 ≤ n →
      ‖reciprocalCoeff N n (r : ℂ) - (N : ℂ) * ((N*n).factorial : ℂ) *
        ((N*n+r-1).choose (r-1) : ℂ) * ∑ τ ∈ T, leadingZeroWeight N r (N*n) τ‖ ≤
      lowerPrincipalConstant S (canonicalPoleCoefficient (canonicalSignedDenominator N) r) r *
        ((N*n).factorial : ℝ) * (N*n : ℝ) ^ (r-2) * R⁻¹ ^ (N*n) +
      C * ((N*n).factorial : ℝ) * Rstar⁻¹ ^ (N*n) := by
  obtain ⟨C, hC⟩ := reciprocalCoeff_leading_bound hN hR hRR hR₂ hS hroot hsimple hzeros hr
  refine ⟨C, fun n hn => ?_⟩
  have h := hC n hn
  rw [leadingPoleCoefficient_eq_zero_weights, leading_zero_sum_orbit_reduction hN hω S T e he] at h
  simpa only [mul_assoc, mul_comm, mul_left_comm] using h

end
end Komorebi.PaperIV
