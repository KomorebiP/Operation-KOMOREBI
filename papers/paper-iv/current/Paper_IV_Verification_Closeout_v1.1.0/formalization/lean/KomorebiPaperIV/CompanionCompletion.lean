/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.CompanionBridge
import KomorebiPaperIV.Wronskians

/-! # Complete companion entry and determinant bridges

The matrix exponential is identified with the transpose of the actual
derivative matrix. Its determinant is then obtained from the proved Wronskian,
without assuming a determinant-of-exponential formula.
-/

namespace Komorebi.PaperIV
open scoped PowerSeries
noncomputable section

/-- Taylor expansion of every derivative of a finite exponential sum. -/
theorem hasSum_exponentialSumJet (N : ℕ) (w a : ℕ → ℂ) (k : ℕ) (z : ℂ) :
    HasSum (fun m => (m.factorial : ℂ)⁻¹ *
      exponentialSumJet N w a (m + k) 0 * z ^ m)
      (exponentialSumJet N w a k z) := by
  have h := hasSum_sum (s := Finset.range N) (fun l _ =>
    (NormedSpace.expSeries_div_hasSum_exp (a l * z)).mul_left (w l * a l ^ k))
  rw [← Complex.exp_eq_exp_ℂ] at h
  apply h.congr_fun
  intro m
  simp only [exponentialSumJet, mul_zero, Complex.exp_zero, mul_one,
    Finset.mul_sum, Finset.sum_mul, pow_add, mul_pow, div_eq_mul_inv]
  apply Finset.sum_congr rfl
  intro l _
  ring

/-- All Taylor coefficients of a signed section's analytic derivatives. -/
theorem entireSigned_derivative_at_zero {N j : ℕ} (hN : 0 < N) (hj : j < N)
    {omega rho : ℂ} (homega : IsPrimitiveRoot omega N) (hrho : rho ^ N = -1)
    (k : ℕ) :
    deriv^[k] (entireSigned N j omega rho) 0 =
      (k.factorial : ℂ) * PowerSeries.coeff k (signedSection (R := ℂ) N j) := by
  rw [entireSigned_derivative_eq_scaled_transfer,
    entireTransfer_derivative_at_zero hN hj homega,
    signedSection_eq_inv_pow_mul_transferSection hN hj hrho,
    PowerSeries.coeff_C_mul]
  ring

/-- Convergent derivative series, with the manuscript's factorial scaling. -/
theorem hasSum_entireSigned_derivative {N j : ℕ} (hN : 0 < N) (hj : j < N)
    {omega rho : ℂ} (homega : IsPrimitiveRoot omega N) (hrho : rho ^ N = -1)
    (k : ℕ) (z : ℂ) :
    HasSum (fun m => (m.factorial : ℂ)⁻¹ * ((m + k).factorial : ℂ) *
      PowerSeries.coeff (m + k) (signedSection (R := ℂ) N j) * z ^ m)
      (deriv^[k] (entireSigned N j omega rho) z) := by
  have h := hasSum_exponentialSumJet N
    (fun l => (rho ^ j)⁻¹ * (N : ℂ)⁻¹ * ((omega ^ j)⁻¹) ^ l)
    (fun l => rho * omega ^ l) k z
  rw [entireSigned_eq_exponentialSum, iteratedDeriv_exponentialSum]
  apply h.congr_fun
  intro m
  have hd := entireSigned_derivative_at_zero hN hj homega hrho (m + k)
  rw [entireSigned_eq_exponentialSum, iteratedDeriv_exponentialSum] at hd
  rw [hd]
  ring

/-- Each matrix entry is an actual derivative, not a formal series symbol. -/
theorem signedFundamentalMatrix_entry_eq_derivative {N : ℕ} (hN : 0 < N)
    {omega rho : ℂ} (homega : IsPrimitiveRoot omega N) (hrho : rho ^ N = -1)
    (z : ℂ) (p q : Fin N) :
    signedFundamentalMatrix N z p q =
      deriv^[q.val] (entireSigned N p.val omega rho) z := by
  apply (hasSum_signedFundamentalMatrix_entry N z p q).unique
  convert hasSum_entireSigned_derivative hN p.isLt homega hrho q.val z using 1
  funext m
  rw [signedShiftMatrix_pow_apply N m hN, coeff_signedSection]
  simp only [signedSectionCoeff, Nat.add_comm m q.val]
  have hf : ((q.val + m).factorial : ℂ) ≠ 0 := by
    exact_mod_cast (q.val + m).factorial_ne_zero
  by_cases he : p.val = (q.val + m) % N
  · simp only [he, ite_true, map_div₀, map_one, map_natCast]
    field_simp
  · simp [he, Ne.symm he]

/-- The companion determinant is exactly one for every complex parameter. -/
theorem signedFundamentalMatrix_det {N : ℕ} (hN : 1 < N)
    {omega rho : ℂ} (homega : IsPrimitiveRoot omega N) (hrho : rho ^ N = -1)
    (z : ℂ) :
    (signedFundamentalMatrix N z).det = 1 := by
  have hm : signedFundamentalMatrix N z =
      (Matrix.of (fun k j : Fin N =>
        deriv^[k.val] (entireSigned N j.val omega rho) z)).transpose := by
    ext p q
    exact signedFundamentalMatrix_entry_eq_derivative (by omega) homega hrho z p q
  rw [hm, Matrix.det_transpose]
  exact signedWronskian_eq_one hN homega hrho z

/-- The residue of the displacement from column q to row p. -/
def companionDisplacement {N : ℕ} (p q : Fin N) : ℕ :=
  if q.val ≤ p.val then p.val - q.val else N + p.val - q.val

theorem companionDisplacement_lt {N : ℕ} (p q : Fin N) :
    companionDisplacement p q < N := by
  unfold companionDisplacement
  have hp := p.isLt
  have hq := q.isLt
  split_ifs <;> omega

/-- Whether the displacement crosses the signed edge. -/
def companionEntrySign {N : ℕ} (p q : Fin N) : ℂ :=
  if q.val ≤ p.val then 1 else -1

/-- Closed packet form of every power entry, including its wraparound sign. -/
theorem signedShiftMatrix_pow_entry_packet {N : ℕ} (hN : 0 < N)
    (p q : Fin N) (m : ℕ) :
    (signedShiftMatrix (R := ℂ) N ^ m) p q =
      companionEntrySign p q *
        (if m % N = companionDisplacement p q then (-1 : ℂ) ^ (m / N) else 0) := by
  rw [signedShiftMatrix_pow_apply N m hN]
  have hp := p.isLt
  have hq := q.isLt
  have hm := Nat.mod_lt m hN
  have hmod : (q.val + m) % N = (q.val + m % N) % N := by
    simp only [Nat.add_mod, Nat.mod_mod]
  have hdiv : (q.val + m) / N = (q.val + m % N) / N + m / N := by
    conv_lhs => rw [← Nat.mod_add_div m N]
    rw [← Nat.add_assoc, Nat.add_mul_div_left _ _ hN]
  rw [hmod, hdiv]
  unfold companionEntrySign companionDisplacement
  by_cases hqp : q.val ≤ p.val
  · simp only [ite_eq_left hqp, one_mul]
    by_cases he : m % N = p.val - q.val
    · have hsum : q.val + m % N = p.val := by omega
      rw [hsum]
      simp only [Nat.mod_eq_of_lt hp, Nat.div_eq_of_lt hp, ite_true, zero_add, he]
    · have hne : p.val ≠ (q.val + m % N) % N := by
        by_cases hs : q.val + m % N < N
        · rw [Nat.mod_eq_of_lt hs]
          omega
        · rw [Nat.mod_eq_sub_mod (by omega), Nat.mod_eq_of_lt (by omega)]
          omega
      simp only [ite_eq_right he, ite_eq_right hne]
  · simp only [ite_eq_right hqp]
    by_cases he : m % N = N + p.val - q.val
    · have hsum : q.val + m % N = N + p.val := by omega
      have hd : (N + p.val) / N = 1 := by
        simpa [Nat.div_eq_of_lt hp, Nat.add_comm] using Nat.add_mul_div_left p.val 1 hN
      rw [hsum]
      simp only [Nat.add_mod_left, Nat.mod_eq_of_lt hp, ite_true, hd, he]
      rw [pow_add]
      simp
    · have hne : p.val ≠ (q.val + m % N) % N := by
        by_cases hs : q.val + m % N < N
        · rw [Nat.mod_eq_of_lt hs]
          omega
        · rw [Nat.mod_eq_sub_mod (by omega), Nat.mod_eq_of_lt (by omega)]
          omega
      simp only [ite_eq_right he, ite_eq_right hne, mul_zero]

/-- Corollary 6.5: every entry of exp(z J) is the stated signed section. -/
theorem signedFundamentalMatrix_entry {N : ℕ} (hN : 0 < N)
    {omega rho : ℂ} (homega : IsPrimitiveRoot omega N) (hrho : rho ^ N = -1)
    (z : ℂ) (p q : Fin N) :
    signedFundamentalMatrix N z p q =
      companionEntrySign p q * entireSigned N (companionDisplacement p q) omega rho z := by
  apply (hasSum_signedFundamentalMatrix_entry N z p q).unique
  have hs := (hasSum_entireSigned hN (companionDisplacement_lt p q) homega hrho z).mul_left
    (companionEntrySign p q)
  apply hs.congr_fun
  intro m
  rw [signedShiftMatrix_pow_entry_packet hN, coeff_signedSection]
  simp only [signedSectionCoeff, map_div₀, map_one, map_natCast]
  split_ifs <;> ring

end
end Komorebi.PaperIV
