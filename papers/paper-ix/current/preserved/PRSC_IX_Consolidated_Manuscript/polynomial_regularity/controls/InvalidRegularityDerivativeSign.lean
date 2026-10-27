module
public import PolynomialRegularityControls

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace Komorebi.InvalidRegularityDerivativeSign

/-- Deliberately invalid: F(Y,T)=Y+T has derivative -I, not +I. -/
theorem wrong_parameter_derivative (p : ℕ) [Fact p.Prime] (t : Fin 1 → ℚ_[p]) :
    HasStrictFDerivAt (fun u : Fin 1 → ℚ_[p] => -u)
      (ContinuousLinearMap.id ℚ_[p] (Fin 1 → ℚ_[p])) t := by
  exact PolynomialRegularityControls.linear_strict_derivative t

end Komorebi.InvalidRegularityDerivativeSign
