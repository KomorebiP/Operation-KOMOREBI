/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.EntireBridge
import KomorebiPaperIV.FiniteModels

/-!
# Matrix exponential and entire signed sections

These results identify the first column and the diagonal of the matrix
exponential by convergent sums. They do not assume ODE uniqueness, a
characteristic polynomial, or a determinant-of-exponential formula.
-/

namespace Komorebi.PaperIV
open scoped PowerSeries
noncomputable section

/-- The scalar series for any entry of the actual matrix exponential. -/
theorem hasSum_signedFundamentalMatrix_entry (N : ℕ) (z : ℂ) (p q : Fin N) :
    HasSum (fun m => (m.factorial : ℂ)⁻¹ * z ^ m *
        (signedShiftMatrix (R := ℂ) N ^ m) p q)
      (signedFundamentalMatrix N z p q) := by
  let h := by
    open scoped Matrix.Norms.Operator in
    exact NormedSpace.exp_series_hasSum_exp' (𝕂 := ℂ) (z • signedShiftMatrix (R := ℂ) N)
  have he := Pi.hasSum.mp (Pi.hasSum.mp h p) q
  simp only [smul_pow, Matrix.smul_apply, smul_eq_mul] at he
  convert he using 1 <;> try rfl
  funext m
  ring

/-- The first column is exactly the analytic signed-section vector. -/
theorem signedFundamentalMatrix_first_column {N : ℕ} (hN : 0 < N)
    {omega rho : ℂ} (homega : IsPrimitiveRoot omega N) (hrho : rho ^ N = -1)
    (z : ℂ) (p : Fin N) :
    signedFundamentalMatrix N z p ⟨0, hN⟩ = entireSigned N p.val omega rho z := by
  have h := hasSum_signedFundamentalMatrix_entry N z p ⟨0, hN⟩
  apply h.unique
  convert hasSum_entireSigned hN p.isLt homega hrho z using 1
  funext m
  rw [signedShiftMatrix_pow_apply N m hN, coeff_signedSection]
  simp only [Nat.zero_add, signedSectionCoeff]
  by_cases he : p.val = m % N
  · simp [he, mul_comm, mul_assoc]
  · simp [he, Ne.symm he]

private theorem signedShift_diagonal_power (N m : ℕ) (hN : 0 < N) (p : Fin N) :
    (signedShiftMatrix (R := ℂ) N ^ m) p p =
      if m % N = 0 then (-1 : ℂ) ^ (m / N) else 0 := by
  rw [signedShiftMatrix_pow_apply N m hN]
  have hp := p.isLt
  have he : p.val = (p.val + m) % N ↔ m % N = 0 := by
    have hm := Nat.mod_lt m hN
    rw [Nat.add_mod, Nat.mod_eq_of_lt hp]
    by_cases hs : p.val + m % N < N
    · rw [Nat.mod_eq_of_lt hs]
      omega
    · rw [Nat.mod_eq_sub_mod (by omega), Nat.mod_eq_of_lt (by omega)]
      omega
  by_cases hm : m % N = 0
  · have hd : (p.val + m) / N = m / N := by
      have hm' : m = N * (m / N) := by
        simpa [hm] using (Nat.div_add_mod m N).symm
      conv_lhs => rw [hm']
      rw [Nat.add_mul_div_left p.val (m / N) hN, Nat.div_eq_of_lt hp, zero_add]
    simp only [ite_eq_left (he.mpr hm), ite_eq_left hm, hd]
  · simp only [ite_eq_right hm, ite_eq_right (he.not.mpr hm)]

/-- Every diagonal entry is the distinguished signed denominator. -/
theorem signedFundamentalMatrix_diagonal {N : ℕ} (hN : 0 < N)
    {omega rho : ℂ} (homega : IsPrimitiveRoot omega N) (hrho : rho ^ N = -1)
    (z : ℂ) (p : Fin N) :
    signedFundamentalMatrix N z p p = entireSigned N 0 omega rho z := by
  have h := hasSum_signedFundamentalMatrix_entry N z p p
  apply h.unique
  convert hasSum_entireSigned hN hN homega hrho z using 1
  funext m
  rw [signedShift_diagonal_power N m hN, coeff_signedSection]
  simp only [signedSectionCoeff]
  split_ifs <;> simp [mul_comm, mul_assoc]

/-- The trace formula in Theorem 6.4, with no spectral certificate premise. -/
theorem signedFundamentalMatrix_trace {N : ℕ} (hN : 0 < N)
    {omega rho : ℂ} (homega : IsPrimitiveRoot omega N) (hrho : rho ^ N = -1)
    (z : ℂ) :
    Matrix.trace (signedFundamentalMatrix N z) =
      (N : ℂ) * entireSigned N 0 omega rho z := by
  classical
  simp [Matrix.trace, Matrix.diag, signedFundamentalMatrix_diagonal hN homega hrho]

end
end Komorebi.PaperIV
