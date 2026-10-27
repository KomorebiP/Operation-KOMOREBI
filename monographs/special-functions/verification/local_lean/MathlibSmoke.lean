module
import Mathlib.Tactic.Ring

namespace SpecialFunctionsRuntimeSmoke

theorem polynomial_identity (x y : ℤ) :
    (x + y)^2 = x^2 + 2*x*y + y^2 := by ring

end SpecialFunctionsRuntimeSmoke
#print axioms SpecialFunctionsRuntimeSmoke.polynomial_identity
