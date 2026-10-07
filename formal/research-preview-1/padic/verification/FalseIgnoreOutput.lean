import KomorebiPadic.ResidualMinimalityExamples
open KomorebiPadic.ResidualRealization
example : behavior zeroOutputSameModule [] = behavior constantOne [] := by
  change (0 : ZMod 5) = 1
  decide +kernel
