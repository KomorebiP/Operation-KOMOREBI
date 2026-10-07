/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.WeightedGrowthSummability
import KomorebiPaperIV.CanonicalProductGrowth

namespace Komorebi.PaperIV
noncomputable section
open Set Filter
open scoped Topology

/-- A normalized entire function with sublinear power growth equals the product
over its actual zeros, with multiplicities. Convergence is proved from growth. -/
theorem entire_sublinear_growth_hadamard {f : ℂ → ℂ} (hf : Differentiable ℂ f)
    (h0 : f 0 = 1) {C p : ℝ} (hC : 0 ≤ C) (hp : 0 ≤ p) (hp1 : p < 1)
    (hgrowth : ∀ R : ℝ, 1 ≤ R → ∀ z : ℂ, ‖z‖ ≤ R → ‖f z‖ ≤ Real.exp (C * R ^ p)) :
    f = fullCanonicalProduct f := by
  let q : ℝ := (p + 1) / 2
  have hq : 0 < q := by dsimp [q]; linarith
  have hpq : p < q := by dsimp [q]; linarith
  have hq1 : q < 1 := by dsimp [q]; linarith
  have hs := entire_growth_zeroPowerSummable hf h0 hC hp hp1 hgrowth
  have hsq := entire_growth_zeroPowerSummable hf h0 hC hp hpq hgrowth
  have hn : f 0 ≠ 0 := by simp [h0]
  have hQ := canonicalProductQuotient_entire hf hs hn
  obtain ⟨g, hg, hg0, he⟩ := entire_normalized_exists_log hQ
    (canonicalProductQuotient_ne_zero hf hs hn) (by rw [canonicalProductQuotient_zero hf hs, h0])
  let B := reciprocalPowerMass f q / q
  have hB : 0 ≤ B := div_nonneg (reciprocalPowerMass_nonneg _ _) hq.le
  have hzero : g = 0 := entire_sublinear_factor_rigidity hf (fullCanonicalProduct_entire hs)
    hg (fullCanonicalProduct_zero f) hg0 (fun z => by rw [he]; exact fullCanonicalProduct_times_quotient hf hs hn z)
    (show 0 ≤ C + B by positivity) hq1 (by
      intro R hR z hz
      have hRp : 0 ≤ R ^ q := Real.rpow_nonneg (by linarith) _
      constructor
      · apply (hgrowth R hR z hz).trans
        apply Real.exp_le_exp.mpr
        calc
          _ ≤ C * R ^ q := mul_le_mul_of_nonneg_left (Real.rpow_le_rpow_of_exponent_le hR hpq.le) hC
          _ ≤ (C + B) * R ^ q := by nlinarith
      · apply (fullCanonicalProduct_growth hs hsq hq hq1.le z).trans
        apply Real.exp_le_exp.mpr
        change B * ‖z‖ ^ q ≤ _
        calc
          _ ≤ B * R ^ q := mul_le_mul_of_nonneg_left (Real.rpow_le_rpow (norm_nonneg _) hz hq.le) hB
          _ ≤ (C + B) * R ^ q := by nlinarith)
  funext z
  have h := fullCanonicalProduct_times_quotient hf hs hn z
  rw [← he z, hzero] at h
  simpa using h.symm

end
end Komorebi.PaperIV
