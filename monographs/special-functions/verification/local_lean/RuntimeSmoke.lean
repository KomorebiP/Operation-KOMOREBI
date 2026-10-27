module
import Mathlib

namespace SpecialFunctionsRuntimeSmoke

theorem polynomial_identity (x y : ℝ) :
    (x + y)^2 = x^2 + 2*x*y + y^2 := by ring

theorem exponential_positive (x : ℝ) : 0 < Real.exp x := Real.exp_pos x

end SpecialFunctionsRuntimeSmoke
#print axioms SpecialFunctionsRuntimeSmoke.polynomial_identity
#print axioms SpecialFunctionsRuntimeSmoke.exponential_positive
