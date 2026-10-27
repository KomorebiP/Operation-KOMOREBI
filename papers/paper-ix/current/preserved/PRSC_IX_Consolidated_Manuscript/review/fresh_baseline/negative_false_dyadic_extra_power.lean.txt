module
public import ConjectureExamples
example : (2:ℤ) ≤ padicValRat 2 (KomorebiPaperIX.Congruential.unnormalized 4 1 1 - KomorebiPaperIX.Congruential.unnormalized 4 1 0) := by
 rw [KomorebiPaperIX.ConjectureExamples.dyadic_nonzero_address_valuation]
 norm_num
