import Komorebi.QuadraticTransport

noncomputable section
set_option autoImplicit false
namespace Komorebi.QuadraticTransport
open MeasureTheory
open scoped ENNReal NNReal

variable {E : Type*} [NormedAddCommGroup E] [MeasurableSpace E]

/-- The square root convention agrees exactly with the quadratic infimum. -/
theorem wasserstein2_sq (μ ν : Measure E) :
    wasserstein2 μ ν ^ (2 : ℕ) = wasserstein2Sq μ ν := by
  unfold wasserstein2
  rw [← ENNReal.rpow_natCast, ← ENNReal.rpow_mul]
  norm_num

/-- Any nonnegative squared certificate gives a 2-Wasserstein tolerance. -/
theorem wasserstein2_le_of_sq_le (μ ν : Measure E) (ε : ℝ) (hε : 0 ≤ ε)
    (h : wasserstein2Sq μ ν ≤ ENNReal.ofReal (ε^2)) :
    wasserstein2 μ ν ≤ ENNReal.ofReal ε := by
  have heq : ENNReal.ofReal (ε^2) = (ENNReal.ofReal ε)^2 := by
    exact ENNReal.ofReal_pow hε
  rw [heq, ← wasserstein2_sq μ ν] at h
  exact (pow_le_pow_left₀ (by positivity) (by positivity) (by norm_num : (2 : ℕ) ≠ 0)).mp h

end Komorebi.QuadraticTransport
