/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.CanonicalProductMultiplicity
import Mathlib.Analysis.Meromorphic.NormalForm

namespace Komorebi.PaperIV
noncomputable section
open Set Filter

def canonicalProductQuotient (f : ℂ → ℂ) : ℂ → ℂ :=
  toMeromorphicNFOn (f / fullCanonicalProduct f) univ

theorem rawCanonicalProductQuotient_meromorphic {f : ℂ → ℂ} (hf : Differentiable ℂ f)
    (hs : ZeroPowerSummable f 1) : MeromorphicOn (f / fullCanonicalProduct f) univ := by
  intro z _
  exact (hf.analyticAt z).meromorphicAt.div ((fullCanonicalProduct_entire hs).analyticAt z).meromorphicAt

theorem rawCanonicalProductQuotient_order_zero {f : ℂ → ℂ} (hf : Differentiable ℂ f)
    (hs : ZeroPowerSummable f 1) (hf0 : f 0 ≠ 0) (z : ℂ) :
    meromorphicOrderAt (f / fullCanonicalProduct f) z = 0 := by
  rw [meromorphicOrderAt_div (hf.analyticAt z).meromorphicAt
    ((fullCanonicalProduct_entire hs).analyticAt z).meromorphicAt,
    (hf.analyticAt z).meromorphicOrderAt_eq, ((fullCanonicalProduct_entire hs).analyticAt z).meromorphicOrderAt_eq,
    fullCanonicalProduct_same_orders hf hs hf0,
    ← Nat.cast_analyticOrderNatAt (entire_analyticOrderAt_ne_top (fun w => hf.analyticAt w) hf0 z),
    ENat.map_natCast]
  norm_cast
  simp

theorem canonicalProductQuotient_entire {f : ℂ → ℂ} (hf : Differentiable ℂ f)
    (hs : ZeroPowerSummable f 1) (hf0 : f 0 ≠ 0) : Differentiable ℂ (canonicalProductQuotient f) := by
  intro z
  have hn := meromorphicNFOn_toMeromorphicNFOn (f / fullCanonicalProduct f) univ (mem_univ z)
  apply (hn.meromorphicOrderAt_nonneg_iff_analyticAt.mp ?_).differentiableAt
  rw [meromorphicOrderAt_toMeromorphicNFOn (rawCanonicalProductQuotient_meromorphic hf hs) (mem_univ z),
    rawCanonicalProductQuotient_order_zero hf hs hf0]

theorem canonicalProductQuotient_ne_zero {f : ℂ → ℂ} (hf : Differentiable ℂ f)
    (hs : ZeroPowerSummable f 1) (hf0 : f 0 ≠ 0) (z : ℂ) : canonicalProductQuotient f z ≠ 0 := by
  have hn := meromorphicNFOn_toMeromorphicNFOn (f / fullCanonicalProduct f) univ (mem_univ z)
  apply hn.meromorphicOrderAt_eq_zero_iff.mp
  rw [meromorphicOrderAt_toMeromorphicNFOn (rawCanonicalProductQuotient_meromorphic hf hs) (mem_univ z),
    rawCanonicalProductQuotient_order_zero hf hs hf0]

theorem canonicalProductQuotient_eq_div {f : ℂ → ℂ} (hf : Differentiable ℂ f)
    (hs : ZeroPowerSummable f 1) {z : ℂ} (hz : fullCanonicalProduct f z ≠ 0) :
    canonicalProductQuotient f z = f z / fullCanonicalProduct f z := by
  unfold canonicalProductQuotient
  rw [toMeromorphicNFOn_eq_toMeromorphicNFAt (rawCanonicalProductQuotient_meromorphic hf hs) (mem_univ z)]
  rw [toMeromorphicNFAt_eq_self.mpr
    (((hf.analyticAt z).div ((fullCanonicalProduct_entire hs).analyticAt z) hz).meromorphicNFAt)]
  rfl

/-- Equality up to an explicitly constructed, entire, nowhere-zero factor.
Constancy of this factor remains the growth-theoretic Hadamard step. -/
theorem fullCanonicalProduct_times_quotient {f : ℂ → ℂ} (hf : Differentiable ℂ f)
    (hs : ZeroPowerSummable f 1) (hf0 : f 0 ≠ 0) (z : ℂ) :
    fullCanonicalProduct f z * canonicalProductQuotient f z = f z := by
  by_cases hz : fullCanonicalProduct f z = 0
  · rw [hz, zero_mul, (fullCanonicalProduct_zero_iff hf hs hf0 z).mp hz]
  · rw [canonicalProductQuotient_eq_div hf hs hz]
    field_simp

theorem canonicalProductQuotient_zero {f : ℂ → ℂ} (hf : Differentiable ℂ f)
    (hs : ZeroPowerSummable f 1) : canonicalProductQuotient f 0 = f 0 := by
  rw [canonicalProductQuotient_eq_div hf hs (by rw [fullCanonicalProduct_zero]; exact one_ne_zero),
    fullCanonicalProduct_zero, div_one]

theorem entireReducedDenominator_product_quotient {N : ℕ} (hN : 2 ≤ N) :
    Differentiable ℂ (canonicalProductQuotient (entireReducedDenominator N)) ∧
    (∀ z, canonicalProductQuotient (entireReducedDenominator N) z ≠ 0) ∧
    canonicalProductQuotient (entireReducedDenominator N) 0 = 1 ∧
    (∀ z, fullCanonicalProduct (entireReducedDenominator N) z *
      canonicalProductQuotient (entireReducedDenominator N) z = entireReducedDenominator N z) := by
  have hf : Differentiable ℂ (entireReducedDenominator N) :=
    fun z => (analyticAt_entireReducedDenominator (by omega) z).differentiableAt
  have hs := entireReducedDenominator_reciprocal_zeros_summable hN
  have h0 : entireReducedDenominator N 0 ≠ 0 := by rw [entireReducedDenominator_zero]; exact one_ne_zero
  refine ⟨canonicalProductQuotient_entire hf hs h0, canonicalProductQuotient_ne_zero hf hs h0, ?_,
    fullCanonicalProduct_times_quotient hf hs h0⟩
  rw [canonicalProductQuotient_zero hf hs, entireReducedDenominator_zero]

end
end Komorebi.PaperIV
