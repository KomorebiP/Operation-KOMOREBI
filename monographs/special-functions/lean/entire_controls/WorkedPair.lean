import CoupledEntire
open Komorebi.SpecialFunctions.Coupled
open Komorebi.SpecialFunctions.Coupled.Scales

-- A consumer of the global convergence theorem at norm five, beyond Block02's disk.
example : workedScales.NormConverges (3 + 4 * Complex.I) :=
  workedScales.coefficient_series_entire workedScales_positive (by norm_num [workedScales]) _

-- The existing rational parameters also discharge every strict-contraction guard.
example (z : ℂ) : HasDerivAt workedScales.U
    (1 + workedScales.U ((workedScales.q : ℂ) * z) *
      workedScales.V ((workedScales.r : ℂ) * z)) z :=
  ((workedScales.coupled_entire_solution workedScales_positive
    (by norm_num [workedScales])).2.2 z).1
