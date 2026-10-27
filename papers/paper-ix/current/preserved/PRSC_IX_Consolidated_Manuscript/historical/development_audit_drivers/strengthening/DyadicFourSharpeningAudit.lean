module
public import DyadicFourSharpening
@[expose] public section
set_option autoImplicit false
open KomorebiPaperIX
#print axioms KomorebiPaperIX.DyadicFourSharpening.factorial_even
#print axioms KomorebiPaperIX.DyadicFourSharpening.unnormalized_difference_factorial
#print axioms KomorebiPaperIX.DyadicFourSharpening.factorial_difference_bound
#print axioms KomorebiPaperIX.DyadicFourSharpening.factorial_difference_precision
#print axioms KomorebiPaperIX.DyadicFourSharpening.normalized_period
#print axioms KomorebiPaperIX.DyadicFourSharpening.half_period
#print axioms KomorebiPaperIX.DyadicFourSharpening.half_period_precision
#print axioms KomorebiPaperIX.DyadicFourSharpening.half_period_degree
#print axioms KomorebiPaperIX.DyadicFourSharpening.all_rows_even

example : GlobalEulerBoundary.precision 2 (6 : ℤ)
    (NishibuchiCompletion.generalizedEuler 4 (by decide) 3 (4 * 5 + 2 ^ 6) -
     NishibuchiCompletion.generalizedEuler 4 (by decide) 3 (4 * 5)) :=
  DyadicFourSharpening.half_period_degree 3 6 5 (by decide) (by decide) (by decide) (by decide)
