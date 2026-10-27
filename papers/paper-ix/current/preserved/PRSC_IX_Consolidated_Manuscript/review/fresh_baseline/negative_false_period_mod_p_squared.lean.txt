module
public import PeriodExamples
open KomorebiPaperIX
example : (2:ℤ)≤padicValRat 3 (Congruential.coeff 6 0 2-Congruential.coeff 6 0 1) := by
 rw [PeriodExamples.first_difference_precision_is_one]
 norm_num
