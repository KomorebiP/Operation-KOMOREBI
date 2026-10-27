import KomorebiPhysics.Relativistic3DCenteredRates
noncomputable section
open KomorebiPhysics Relativistic3DCenteredRates Relativistic3DFullFourierEvolution
example (m h t : ℝ) (f : Relativistic3DFullFourierEvolution.CoeffL2) :
    ‖centralCoeffPropagator m h t f - continuumCoeffPropagator m t f‖ ≤
      (|t| * h ^ 2 / 6) * thirdOrderMoment f := by
  exact centered_propagator_quadratic_bound m h t f
