/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.NormalizedGrowth
import KomorebiPaperIV.SublinearHadamard
import KomorebiPaperIV.AnalyticTaylorAlgebra
import KomorebiPaperIV.ThetaZeroBell

namespace Komorebi.PaperIV
noncomputable section
open Set Filter
open scoped Topology

/-- The full genus-zero product for every normalized residue section. -/
theorem entireNormalizedSection_hadamard {N : ℕ} (hN : 2 ≤ N) (j : ℕ) :
    entireNormalizedSection N j = fullCanonicalProduct (entireNormalizedSection N j) := by
  have hN0 : 0 < N := by omega
  apply entire_sublinear_growth_hadamard
    (fun z => (analyticAt_entireNormalizedSection hN0 j z).differentiableAt)
    (entireNormalizedSection_zero N j) (normalizedSectionGrowthConstant_pos j).le (by positivity)
    _ (entireNormalizedSection_disk_growth hN0 j)
  have hn : (1 : ℝ) < N := by exact_mod_cast (show 1 < N by omega)
  exact (div_lt_one (by positivity : (0 : ℝ) < N)).mpr hn

theorem entireNormalizedSection_hadamard_uniform {N : ℕ} (hN : 2 ≤ N) (j : ℕ)
    {K : Set ℂ} (hK : IsCompact K) :
    HasProdUniformlyOn (fun (i : ZeroMultiplicityIndex (entireNormalizedSection N j)) w =>
      1 - w / indexedZero i) (entireNormalizedSection N j) K := by
  have hn : (1 : ℝ) < N := by exact_mod_cast (show 1 < N by omega)
  have hs := entireNormalizedSection_zeroPowerSummable (show 0 < N by omega) j
    ((div_lt_one (by positivity : (0 : ℝ) < N)).mpr hn)
  simpa only [← entireNormalizedSection_hadamard hN j] using fullCanonicalProduct_uniform_on_compact hs hK

theorem analyticTaylorSeries_entireNormalizedSection {N : ℕ} (hN : 0 < N) (j : ℕ) :
    analyticTaylorSeries (entireNormalizedSection N j) = normalizedResidueSection (K := ℂ) N j := by
  ext n
  rw [analyticTaylorSeries_coeff, analyticTaylorCoefficient, entireNormalizedSection_iteratedDeriv_zero hN,
    coeff_normalizedResidueSection]
  have hn : (n.factorial : ℂ) ≠ 0 := by exact_mod_cast n.factorial_ne_zero
  field_simp

end
end Komorebi.PaperIV
