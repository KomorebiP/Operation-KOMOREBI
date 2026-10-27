module
public import OddEulerExamples
example : KomorebiPaperIX.OddEuler.truncation 2 0 0 = KomorebiPaperIX.EulerCoefficients.eulerEven 0 := by
  norm_num [KomorebiPaperIX.OddEuler.truncation, KomorebiPaperIX.EulerCoefficients.inverseEven, KomorebiPaperIX.OddPower.source, Finset.sum_range_succ, KomorebiPaperIX.OddEulerExamples.euler_anchor_values.1]
