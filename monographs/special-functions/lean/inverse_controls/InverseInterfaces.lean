import CoupledGermInverse
open Komorebi.SpecialFunctions.Coupled
open Scales Filter
open scoped Topology

example (c : ℕ → ℝ) : denseOdd c 3 = (c 1 : ℂ) ∧
    denseOdd c 5 = (c 2 : ℂ) ∧ denseOdd c 7 = (c 3 : ℂ) ∧
    denseOdd c 0 = 0 ∧ denseOdd c 2 = 0 := by
  exact ⟨denseOdd_odd c 1, denseOdd_odd c 2, denseOdd_odd c 3,
    denseOdd_even c 0, denseOdd_even c 1⟩

example {t : Scales} (ht : t.positive)
    (hst : t.q < 1 ∧ t.r < 1 ∧ t.a < 1 ∧ t.b < 1)
    (hu : workedScales.U =ᶠ[𝓝 0] t.U)
    (hv : workedScales.V =ᶠ[𝓝 0] t.V) : workedScales = t := by
  apply parameters_of_analytic_germs workedScales_positive ht
    (by norm_num [workedScales]) hst ?_ hu hv
  rw [workedScales_defect]
  norm_num

example : boundaryLeft.positive ∧ boundaryRight.positive ∧
    boundaryLeft.defect = 0 ∧ boundaryLeft.sameJet boundaryRight ∧
    boundaryLeft ≠ boundaryRight := boundary_collision

example (s : Scales) (hs : s.positive)
    (hst : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1)
    {f g : ℂ → ℂ} {p q : FormalMultilinearSeries ℂ ℂ ℂ}
    (hp : HasFPowerSeriesAt f p 0) (hq : HasFPowerSeriesAt g q 0)
    (hz : f 0 = 0 ∧ g 0 = 0) (he : s.GermEquations f g) :
    p.coeff 7 = ((s.coefficients 3).1 : ℂ) ∧ q.coeff 7 = ((s.coefficients 3).2 : ℂ) := by
  simpa only [show 7 = 2 * 3 + 1 from rfl, denseOdd_odd] using
    s.analytic_solution_Taylor_coefficients hs hst hp hq hz he 7
