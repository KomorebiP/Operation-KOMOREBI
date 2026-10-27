module
public import DyadicExamples
example : (KomorebiPaperIX.EulerCoefficients.eulerEven 1 : ℚ) = ∑ m ∈ Finset.range 2, KomorebiPaperIX.Dyadic.beta m * ((2:ℕ).descFactorial (2*m) : ℚ) * KomorebiPaperIX.Dyadic.sourceEven (1-m) := by
  rw [KomorebiPaperIX.OddEulerExamples.euler_anchor_values.2.1]
  norm_num [Finset.sum_range_succ, KomorebiPaperIX.Dyadic.sourceEven, KomorebiPaperIX.DyadicExamples.beta_one, Nat.descFactorial]
