import Mathlib.Analysis.InnerProductSpace.l2Space
import Mathlib.Analysis.Calculus.Deriv.Slope
import Mathlib.Tactic
open Filter
open scoped Topology lp
set_option pp.all true in
example {I : Type*} {f : ℝ → ℓ²(I, ℂ)} {y : ℓ²(I, ℂ)} {t : ℝ}
    (hc : ∀ i, HasDerivAt (fun s => f s i) (y i) t) (i : I) :
    Tendsto (fun s => (s-t)⁻¹ • (f s i - f t i)) (𝓝[≠] t) (𝓝 (y i)) := by
  have h := (hc i).tendsto_slope
  dsimp only [slope, vsub_eq_sub] at h
  exact h
