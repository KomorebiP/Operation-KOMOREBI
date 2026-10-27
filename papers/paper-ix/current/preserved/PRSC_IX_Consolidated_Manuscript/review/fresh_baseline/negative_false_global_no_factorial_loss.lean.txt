module
public import AllResidueExamples
example : KomorebiPaperIX.GlobalEulerBoundary.precision 3 1 (KomorebiPaperIX.Mahler.difference 1 1 (KomorebiPaperIX.Congruential.coeff 6 3) 1) := by
 rw [KomorebiPaperIX.GlobalEulerBoundary.precision, KomorebiPaperIX.Mahler.difference_one, KomorebiPaperIX.Normalization.normalized_difference]
 norm_num [padicValRat_def, padicValInt, padicValNat.eq_zero_of_not_dvd]
