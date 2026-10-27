import KomorebiPadic.ResidualMinimalityExamples
open KomorebiPadic.ResidualRealization
example : behavior trailingZero [0] = 0 := by
  rw [trailingZero_single_zero]
  decide +kernel
