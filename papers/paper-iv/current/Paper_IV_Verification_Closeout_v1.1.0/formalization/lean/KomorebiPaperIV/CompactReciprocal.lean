/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.ReciprocalCompletion

namespace Komorebi.PaperIV
noncomputable section
variable {K : Type*} [Field K] [CharZero K]

private theorem ordinary_low_equations (N : ℕ) (r : K) :
    reciprocalOrdCoeff N 1 r = r / (N.factorial : K) ∧
    2 * reciprocalOrdCoeff N 2 r =
      r * (r + 1) / (N.factorial : K)^2 - 2*r / ((2*N).factorial : K) ∧
    6 * reciprocalOrdCoeff N 3 r =
      r*(r+1)*(r+2)/(N.factorial : K)^3 -
      6*r*(r+1)/((N.factorial : K)*((2*N).factorial : K)) +
      6*r/((3*N).factorial : K) := by
  have h0 := reciprocalOrdCoeff_parameter_equation N 0 r
  have h1 := reciprocalOrdCoeff_parameter_equation N 1 r
  have h2 := reciprocalOrdCoeff_parameter_equation N 2 r
  have hb : reciprocalOrdCoeff N 0 r = 1 := by simp [reciprocalOrdCoeff]
  norm_num [Finset.Nat.antidiagonal_succ, Finset.Nat.antidiagonal_zero,
    coeff_reducedDenominator, hb, eq_ratCast, Nat.mul_comm N] at h0 h1 h2
  constructor
  · linear_combination h0
  constructor
  · linear_combination h1 + (r+1)/(N.factorial : K)*h0
  · linear_combination 2*h2 + (r+2)/(N.factorial : K)*h1 +
      ((r+1)*(r+2)/(N.factorial : K)^2 - (4*r+2)/((2*N).factorial : K))*h0

theorem reciprocalCoeff_two_compact {N : ℕ} (hN : 0 < N) (r : K) :
    reciprocalCoeff N 2 r =
      r * (((2*N).choose N : K) / 2 * (r+1) - 1) := by
  have h := (ordinary_low_equations N r).2.1
  change 2 * PowerSeries.coeff 2 (reciprocalSeries N r) = _ at h
  rw [reciprocalCoeff, blockCoeff, Nat.mul_comm N 2,
    Nat.cast_choose K (show N ≤ 2*N by omega), show 2*N-N=N by omega]
  have hf : ((2*N).factorial : K) ≠ 0 := by exact_mod_cast (2*N).factorial_ne_zero
  have hg : (N.factorial : K) ≠ 0 := by exact_mod_cast N.factorial_ne_zero
  field_simp at h ⊢
  linear_combination h

theorem reciprocalCoeff_three_compact {N : ℕ} (hN : 0 < N) (r : K) :
    reciprocalCoeff N 3 r =
      r * (((3*N).factorial : K)/(6*(N.factorial : K)^3)*(r+1)*(r+2) -
        ((3*N).choose N : K)*(r+1)+1) := by
  have h := (ordinary_low_equations N r).2.2
  change 6 * PowerSeries.coeff 3 (reciprocalSeries N r) = _ at h
  rw [reciprocalCoeff, blockCoeff, Nat.mul_comm N 3,
    Nat.cast_choose K (show N ≤ 3*N by omega), show 3*N-N=2*N by omega]
  have hf : ((3*N).factorial : K) ≠ 0 := by exact_mod_cast (3*N).factorial_ne_zero
  have hg : (N.factorial : K) ≠ 0 := by exact_mod_cast N.factorial_ne_zero
  have hh : ((2*N).factorial : K) ≠ 0 := by exact_mod_cast (2*N).factorial_ne_zero
  field_simp at h ⊢
  linear_combination h

end
end Komorebi.PaperIV
