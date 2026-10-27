import Mathlib.Probability.Distributions.Gaussian.Real
import Mathlib.Probability.Kernel.Posterior
open MeasureTheory ProbabilityTheory
open scoped ENNReal NNReal
namespace Test

theorem cs (m y x h p r : ℝ) (hp:p≠0) (hr:r≠0)
    (hs:h^2*p+r≠0) :
    (x-m)^2/p + (y-h*x)^2/r =
      (y-h*m)^2/(h^2*p+r) +
      (x-(r*m+p*h*y)/(h^2*p+r))^2/(p*r/(h^2*p+r)) := by
  have hs' : r + p * h^2 ≠ 0 := by
    intro hz
    apply hs
    calc h^2 * p + r = r + p * h^2 := by ring
      _ = 0 := hz
  field_simp [hs, hs']
  ring

end Test
