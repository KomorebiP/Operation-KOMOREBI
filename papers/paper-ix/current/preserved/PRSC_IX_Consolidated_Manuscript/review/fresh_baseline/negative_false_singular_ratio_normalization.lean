module
public import SingularAmiceExamples
example : PowerSeries.constantCoeff (KomorebiPaperIX.SingularRatioAmice.rationalRatioPullback 6 (by decide) 2) = 1 := by
 rw [KomorebiPaperIX.SingularAmiceExamples.p3_singular_ratio_constant]
 norm_num
