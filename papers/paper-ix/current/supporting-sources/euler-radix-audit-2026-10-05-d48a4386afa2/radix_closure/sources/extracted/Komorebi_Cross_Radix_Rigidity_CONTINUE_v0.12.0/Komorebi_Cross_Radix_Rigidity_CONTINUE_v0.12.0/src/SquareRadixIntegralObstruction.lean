import Mathlib.Tactic.Ring

namespace KomorebiCrossRadix

/-- Coefficients of `(B*n+s)^2` in the saturated integer-valued quadratic
basis `(1, n, binom(n,2))` are `(s^2, B^2+2Bs, 2B^2)`. The linear functional
`2*x₁-x₂` therefore evaluates to `4Bs`. -/
theorem square_section_hyperplane_identity (B s : ℤ) :
    2 * (B ^ 2 + 2 * B * s) - 2 * B ^ 2 = 4 * B * s := by
  ring

/-- Every divisor of the section width `B` divides the hyperplane defect
`2*x₁-x₂` of a positive-depth square section. -/
theorem divisor_annihilates_square_section_defect
    (p B s : ℤ) (hp : p ∣ B) :
    p ∣ (2 * (B ^ 2 + 2 * B * s) - 2 * B ^ 2) := by
  rw [square_section_hyperplane_identity]
  rcases hp with ⟨c, rfl⟩
  refine ⟨4 * c * s, ?_⟩
  ring

/-- In particular, at radix `p`, every positive-depth section width `p^e`
(`e>=1`, represented here as `p*C`) satisfies the same congruence obstruction. -/
theorem radix_factor_annihilates_square_section_defect
    (p C s : ℤ) :
    p ∣ (2 * ((p * C) ^ 2 + 2 * (p * C) * s) - 2 * (p * C) ^ 2) := by
  exact divisor_annihilates_square_section_defect p (p * C) s ⟨C, rfl⟩

/-- The depth-zero square packet `(0,1,2)` lies on the same hyperplane. -/
theorem square_source_hyperplane : (2 : ℤ) * 1 - 2 = 0 := by norm_num

/-- The saturated binomial packet `(0,0,1)` does not lie on that hyperplane:
its defect is `-1`, so it remains nonzero modulo every prime. -/
theorem binomial2_escapes_hyperplane : (2 : ℤ) * 0 - 1 = -1 := by norm_num

end KomorebiCrossRadix

#print axioms KomorebiCrossRadix.square_section_hyperplane_identity
#print axioms KomorebiCrossRadix.divisor_annihilates_square_section_defect
#print axioms KomorebiCrossRadix.radix_factor_annihilates_square_section_defect
#print axioms KomorebiCrossRadix.binomial2_escapes_hyperplane
