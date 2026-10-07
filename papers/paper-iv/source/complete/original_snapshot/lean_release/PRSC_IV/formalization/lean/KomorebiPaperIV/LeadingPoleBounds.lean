/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.NearestPoleExpansion
import KomorebiPaperIV.SimplePoleParts

namespace Komorebi.PaperIV
noncomputable section
open Set Filter
open scoped Topology Classical

def principalCoefficientSum (S : Finset ℂ) (a : ℂ → ℕ → ℂ) (r m : ℕ) : ℂ :=
  ∑ ρ ∈ S, ∑ k ∈ Finset.range r, a ρ (k+1) * ((m+k).choose k : ℂ) * ρ⁻¹ ^ m

def leadingPoleCoefficient (S : Finset ℂ) (a : ℂ → ℕ → ℂ) (r m : ℕ) : ℂ :=
  ((m+r-1).choose (r-1) : ℂ) * ∑ ρ ∈ S, a ρ r * ρ⁻¹ ^ m

def lowerPrincipalConstant (S : Finset ℂ) (a : ℂ → ℕ → ℂ) (r : ℕ) : ℝ :=
  ∑ ρ ∈ S, ∑ k ∈ Finset.range (r-1), ‖a ρ (k+1)‖ * (k+1 : ℝ) ^ k

theorem lowerPrincipalConstant_nonneg (S : Finset ℂ) (a : ℂ → ℕ → ℂ) (r : ℕ) :
    0 ≤ lowerPrincipalConstant S a r := by unfold lowerPrincipalConstant; positivity

@[simp] theorem lowerPrincipalConstant_one (S : Finset ℂ) (a : ℂ → ℕ → ℂ) :
    lowerPrincipalConstant S a 1 = 0 := by simp [lowerPrincipalConstant]

theorem principalCoefficientSum_split (S : Finset ℂ) (a : ℂ → ℕ → ℂ) {r : ℕ} (hr : 0 < r) (m : ℕ) :
    principalCoefficientSum S a r m - leadingPoleCoefficient S a r m =
      ∑ ρ ∈ S, ∑ k ∈ Finset.range (r-1), a ρ (k+1) * ((m+k).choose k : ℂ) * ρ⁻¹ ^ m := by
  obtain ⟨s, rfl⟩ := Nat.exists_eq_succ_of_ne_zero hr.ne'
  simp only [principalCoefficientSum, leadingPoleCoefficient, Nat.succ_sub_one,
    Nat.add_succ_sub_one, Finset.sum_range_succ, Finset.sum_add_distrib, Finset.mul_sum]
  have he : (∑ ρ ∈ S, a ρ (s+1) * ((m+s).choose s : ℂ) * ρ⁻¹ ^ m) =
      ∑ ρ ∈ S, ((m+s).choose s : ℂ) * (a ρ (s+1) * ρ⁻¹ ^ m) := by
    apply Finset.sum_congr rfl
    intro ρ _
    ring
  rw [he, add_sub_cancel_right]

theorem principalCoefficientSum_leading_error {S : Finset ℂ} {R : ℝ}
    (hR : 0 < R) (hS : ∀ ρ ∈ S, ‖ρ‖ = R) (a : ℂ → ℕ → ℂ)
    {r : ℕ} (hr : 0 < r) {m : ℕ} (hm : 1 ≤ m) :
    ‖principalCoefficientSum S a r m - leadingPoleCoefficient S a r m‖ ≤
      lowerPrincipalConstant S a r * (m : ℝ) ^ (r-2) * R⁻¹ ^ m := by
  rw [principalCoefficientSum_split S a hr m]
  calc
    _ ≤ ∑ ρ ∈ S, ‖∑ k ∈ Finset.range (r-1), a ρ (k+1) * ((m+k).choose k : ℂ) * ρ⁻¹ ^ m‖ := norm_sum_le _ _
    _ ≤ ∑ ρ ∈ S, ∑ k ∈ Finset.range (r-1), ‖a ρ (k+1) * ((m+k).choose k : ℂ) * ρ⁻¹ ^ m‖ :=
      Finset.sum_le_sum (fun ρ _ => norm_sum_le _ _)
    _ ≤ ∑ ρ ∈ S, ∑ k ∈ Finset.range (r-1),
        (‖a ρ (k+1)‖ * (k+1 : ℝ) ^ k) * (m : ℝ) ^ (r-2) * R⁻¹ ^ m := by
      apply Finset.sum_le_sum
      intro ρ hρ
      apply Finset.sum_le_sum
      intro k hk
      have hk' : k+1 < r := by have := Finset.mem_range.mp hk; omega
      have hn : ((m+k).choose k : ℝ) ≤ (k+1 : ℝ) ^ k * (m : ℝ) ^ (r-2) := by
        exact_mod_cast (by simpa using lower_principal_part_choose_bound hm (by omega : 1 ≤ k+1) hk')
      simp only [norm_mul, Complex.norm_natCast, norm_pow, norm_inv, hS ρ hρ]
      have hh := mul_le_mul_of_nonneg_right (mul_le_mul_of_nonneg_left hn (norm_nonneg (a ρ (k+1))))
        (pow_nonneg (inv_nonneg.mpr hR.le) m)
      simpa only [mul_assoc] using hh
    _ = _ := by simp only [lowerPrincipalConstant, Finset.sum_mul]

/-- The lower-order error vanishes identically for simple reciprocal poles. -/
theorem principalCoefficientSum_one (S : Finset ℂ) (a : ℂ → ℕ → ℂ) (m : ℕ) :
    principalCoefficientSum S a 1 m = leadingPoleCoefficient S a 1 m := by
  simpa using (sub_eq_zero.mp (by simpa using principalCoefficientSum_split S a (by norm_num : 0 < 1) m))

/-- Leading-pole expansion, with both error bounds and the r=1 boundary explicit. -/
theorem reciprocalCoeff_leading_bound {N : ℕ} (hN : 0 < N)
    {S : Finset ℂ} {R Rstar R₂ : ℝ} (hR : 0 < R) (hRR : R < Rstar) (hR₂ : Rstar < R₂)
    (hS : ∀ ρ ∈ S, ‖ρ‖ = R) (hroot : ∀ ρ ∈ S, canonicalSignedDenominator N ρ = 0)
    (hsimple : ∀ ρ ∈ S, deriv (canonicalSignedDenominator N) ρ ≠ 0)
    (hzeros : ∀ z : ℂ, ‖z‖ < R₂ → canonicalSignedDenominator N z = 0 → z ∈ S)
    {r : ℕ} (hr : 0 < r) :
    ∃ C : ℝ, ∀ n : ℕ, 1 ≤ n →
      ‖reciprocalCoeff N n (r : ℂ) - ((N*n).factorial : ℂ) *
        leadingPoleCoefficient S (canonicalPoleCoefficient (canonicalSignedDenominator N) r) r (N*n)‖ ≤
      lowerPrincipalConstant S (canonicalPoleCoefficient (canonicalSignedDenominator N) r) r *
        ((N*n).factorial : ℝ) * (N*n : ℝ) ^ (r-2) * R⁻¹ ^ (N*n) +
      C * ((N*n).factorial : ℝ) * Rstar⁻¹ ^ (N*n) := by
  have hf : Differentiable ℂ (canonicalSignedDenominator N) := fun z => (analyticAt_entireSigned ..).differentiableAt
  have hS0 (ρ : ℂ) (hρ : ρ ∈ S) : ρ ≠ 0 := by
    intro he
    have := hS ρ hρ
    rw [he, norm_zero] at this
    linarith
  let a := canonicalPoleCoefficient (canonicalSignedDenominator N) r
  obtain ⟨C, hC⟩ := reciprocalCoeff_nearest_pole_bound hN hS0 a r (hR.trans hRR) hR₂ hzeros
    (fun ρ hρ => canonicalPoleCoefficient_local_bound hf (hS0 ρ hρ) (hroot ρ hρ) (hsimple ρ hρ) r)
  refine ⟨C, fun n hn => ?_⟩
  have hm : 1 ≤ N*n := Nat.mul_pos hN (by omega)
  have he := principalCoefficientSum_leading_error hR hS a hr hm
  have hsplit : reciprocalCoeff N n (r : ℂ) - ((N*n).factorial : ℂ) * leadingPoleCoefficient S a r (N*n) =
      ((N*n).factorial : ℂ) * (principalCoefficientSum S a r (N*n) - leadingPoleCoefficient S a r (N*n)) +
      (reciprocalCoeff N n (r : ℂ) - ((N*n).factorial : ℂ) * principalCoefficientSum S a r (N*n)) := by ring
  rw [hsplit]
  apply (norm_add_le _ _).trans
  rw [norm_mul, Complex.norm_natCast]
  have hh := add_le_add (mul_le_mul_of_nonneg_left he (show (0 : ℝ) ≤ (N*n).factorial by positivity)) (hC n)
  simpa only [principalCoefficientSum, Nat.cast_mul, mul_assoc, mul_comm, mul_left_comm] using hh

end
end Komorebi.PaperIV
