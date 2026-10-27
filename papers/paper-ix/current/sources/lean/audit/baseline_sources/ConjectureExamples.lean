module
public import NishibuchiCompletion
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPaperIX.ConjectureExamples
open NishibuchiCompletion GlobalEulerBoundary Mahler

/-- The four degree-four coefficients are obtained from the original general recurrence. -/
theorem four_first_coefficients :
    Congruential.coeff 4 0 1 = -1 ∧ Congruential.coeff 4 1 1 = -1/5 ∧
    Congruential.coeff 4 2 1 = -1/15 ∧ Congruential.coeff 4 3 1 = -1/35 := by
  repeat' constructor
  all_goals
    rw [Congruential.coefficient_recurrence 4 _ (by decide : 0<1)]
    norm_num [Finset.sum_range_succ,Nat.choose]

/-- Multiplying by j!, rather than silently changing the external normalization. -/
theorem four_first_unnormalized :
    Congruential.unnormalized 4 0 1 = -1 ∧ Congruential.unnormalized 4 1 1 = -1/5 ∧
    Congruential.unnormalized 4 2 1 = -2/15 ∧ Congruential.unnormalized 4 3 1 = -6/35 := by
  obtain ⟨h0,h1,h2,h3⟩ := four_first_coefficients
  norm_num [Congruential.unnormalized,h0,h1,h2,h3,Nat.factorial]

theorem dyadic_nonzero_address_error :
    Congruential.unnormalized 4 1 1 - Congruential.unnormalized 4 1 0 = -6/5 := by
  rw [four_first_unnormalized.2.1]
  norm_num [Congruential.unnormalized]

/-- Exact valuation one at this example; no universal extra power is claimed. -/
theorem dyadic_nonzero_address_valuation :
    padicValRat 2 (Congruential.unnormalized 4 1 1 - Congruential.unnormalized 4 1 0)=1 := by
  rw [dyadic_nonzero_address_error]
  norm_num [padicValRat_def,padicValInt]
  rw [show (6:ℕ)=2*3 by decide,
    padicValNat.mul (by decide : (2:ℕ)≠0) (by decide : (3:ℕ)≠0)]
  norm_num [padicValNat.eq_zero_of_not_dvd]

/-- Instantiate the new omitted branch at every precision and every valid address. -/
theorem dyadic_all_residues (j r n:ℕ) (hj:j<4) (hr:0<r) (hn:r≤n) :
    precision 2 (r:ℤ)
      (generalizedEuler 4 (by decide) j (4*n+2^(r+1))-
       generalizedEuler 4 (by decide) j (4*n)) := by
  have H := full_period_degree 2 2 j r n (by decide) hj (Or.inr rfl) hr hn
  simpa [displacementFactor,pow_succ,mul_comm] using H

/-- The dyadic m=1 branch still uses q=2; it must not be assigned q=p-1=1. -/
theorem dyadic_modulus_two (j r n:ℕ) (hj:j<2) (hr:0<r) (hn:r≤n) :
    precision 2 (r:ℤ)
      (generalizedEuler 2 (by decide) j (2*n+2^(r+1))-
       generalizedEuler 2 (by decide) j (2*n)) := by
  have H := full_period_degree 2 1 j r n (by decide) hj (Or.inl (one_dvd _)) hr hn
  simpa [displacementFactor,pow_succ,mul_comm] using H

/-- A singular odd-prime address is preserved by the combined external formulation. -/
theorem odd_singular_address (r n:ℕ) (hr:0<r) (hn:r≤n) :
    precision 3 (r:ℤ)
      (generalizedEuler 6 (by decide) 3 (6*n+2*3^r)-
       generalizedEuler 6 (by decide) 3 (6*n)) := by
  have H := full_period_degree 3 2 3 r n (by decide) (by decide) (Or.inr rfl) hr hn
  simpa [displacementFactor] using H

end KomorebiPaperIX.ConjectureExamples
