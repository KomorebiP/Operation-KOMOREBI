module
public import DworkWindowExamples
example : (3:ℤ) ≤ padicValRat 3 (KomorebiPaperIX.Mahler.difference 1 2 (KomorebiPaperIX.Congruential.coeff 6 2) 1) := by
 rw [KomorebiPaperIX.DworkWindowExamples.window_second_difference_valuation]
 norm_num
