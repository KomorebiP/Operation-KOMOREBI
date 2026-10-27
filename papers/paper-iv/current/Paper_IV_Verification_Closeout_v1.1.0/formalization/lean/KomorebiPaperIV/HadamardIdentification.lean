/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.EntireQuotientGrowth
import KomorebiPaperIV.CanonicalProductGrowth

namespace Komorebi.PaperIV
noncomputable section
open Set Filter
open scoped Topology

/-- The actual quotient is identically one. No growth certificate is assumed:
the zero-power bounds, product estimate and Jensen-Poisson estimate prove it. -/
theorem entireReducedDenominator_quotient_eq_one {N : ℕ} (hN : 2 ≤ N) :
    canonicalProductQuotient (entireReducedDenominator N) = 1 := by
  obtain ⟨hQ, hn, h0, he⟩ := entireReducedDenominator_product_quotient hN
  obtain ⟨g, hg, hg0, hgexp⟩ := entire_normalized_exists_log hQ hn h0
  obtain ⟨C, hC, hbound⟩ := entireReducedDenominator_and_product_growth hN
  have hf : Differentiable ℂ (entireReducedDenominator N) :=
    fun z => (analyticAt_entireReducedDenominator (by omega) z).differentiableAt
  have hP := fullCanonicalProduct_entire (entireReducedDenominator_reciprocal_zeros_summable hN)
  have hgz : g = 0 := entire_sublinear_factor_rigidity hf hP hg
    (fullCanonicalProduct_zero _) hg0 (fun z => by rw [hgexp]; exact he z)
    hC (by norm_num : (3 / 4 : ℝ) < 1) hbound
  funext z
  rw [← hgexp z, hgz]
  exact Complex.exp_zero

/-- The complete genus-zero Hadamard product for every N ≥ 2, including all
exceptional zeros repeated according to their analytic multiplicities. -/
theorem entireReducedDenominator_eq_fullCanonicalProduct {N : ℕ} (hN : 2 ≤ N) :
    entireReducedDenominator N = fullCanonicalProduct (entireReducedDenominator N) := by
  funext z
  have he := (entireReducedDenominator_product_quotient hN).2.2.2 z
  rw [entireReducedDenominator_quotient_eq_one hN, Pi.one_apply, mul_one] at he
  exact he.symm

/-- Full statement of Theorem 12.1: equality and convergence uniformly on
each compact subset for the product over the entire zero multiset. -/
theorem entireReducedDenominator_hadamard_uniform {N : ℕ} (hN : 2 ≤ N)
    {K : Set ℂ} (hK : IsCompact K) :
    HasProdUniformlyOn
      (fun (i : ZeroMultiplicityIndex (entireReducedDenominator N)) w => 1 - w / indexedZero i)
      (entireReducedDenominator N) K := by
  simpa only [← entireReducedDenominator_eq_fullCanonicalProduct hN] using
    fullCanonicalProduct_uniform_on_compact
      (entireReducedDenominator_reciprocal_zeros_summable hN) hK

theorem canonicalSignedDenominator_hadamard {N : ℕ} (hN : 2 ≤ N) (z : ℂ) :
    canonicalSignedDenominator N z =
      ∏' i : ZeroMultiplicityIndex (entireReducedDenominator N), (1 - z ^ N / indexedZero i) := by
  calc
    _ = entireReducedDenominator N (z ^ N) := canonicalSignedDenominator_eq_reduced_power (by omega) z
    _ = fullCanonicalProduct (entireReducedDenominator N) (z ^ N) :=
      congrFun (entireReducedDenominator_eq_fullCanonicalProduct hN) _
    _ = _ := rfl

end
end Komorebi.PaperIV
