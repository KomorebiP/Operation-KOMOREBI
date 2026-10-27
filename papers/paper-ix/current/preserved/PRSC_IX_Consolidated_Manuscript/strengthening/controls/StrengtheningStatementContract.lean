module
public import DyadicFourFinalStrengthening
public import DyadicSharpTower
@[expose] public section
set_option autoImplicit false
open KomorebiPaperIX

example (j u k n : ℕ) (hj : j < 4) :
    GlobalEulerBoundary.precision 2
      ((k * (padicValNat 2 u + 1) + padicValNat 2 j.factorial : ℕ) : ℤ)
      (Mahler.difference u k (Congruential.unnormalized 4 j) n) :=
  DyadicFourFinalStrengthening.unnormalized_step_precision j u k n hj

example (j r n : ℕ) (hj : j < 4) (hr : 0 < r) :
    GlobalEulerBoundary.precision 2 (r : ℤ)
      (NishibuchiCompletion.generalizedEuler 4 (by decide) j (4 * n + 2 ^ (r + 1)) -
       NishibuchiCompletion.generalizedEuler 4 (by decide) j (4 * n)) :=
  DyadicFourFinalStrengthening.all_rows_period_degree j r n hj hr

example (j r n : ℕ) (hj : j < 4) (hj2 : 2 ≤ j) (hr : 2 ≤ r) :
    GlobalEulerBoundary.precision 2 (r : ℤ)
      (NishibuchiCompletion.generalizedEuler 4 (by decide) j (4 * n + 2 ^ r) -
       NishibuchiCompletion.generalizedEuler 4 (by decide) j (4 * n)) :=
  DyadicFourFinalStrengthening.all_rows_half_period_degree j r n hj hj2 hr

example (n M : ℕ) : (2 : ℤ_[2]) ^ (4 * M + 3) ∣
    (EulerCoefficients.eulerEven n : ℤ_[2]) - DyadicReconstruction.truncationPadic n M :=
  DyadicSharpTower.dyadic_supercongruence_sharp n M

example (M : ℕ) : padicValRat 2
    ((EulerCoefficients.eulerEven (M + 1) : ℚ) - DyadicReconstruction.truncation (M + 1) M) =
      (4 * M + 3 : ℕ) :=
  DyadicSharpTower.first_omitted_error_valuation M
