import KomorebiPhysics.Relativistic3DCenteredRates
noncomputable section
open KomorebiPhysics Relativistic3DCenteredRates Relativistic3DCenteredConvergence
open Relativistic3DUnboundedDirac
example (m h : ℝ) (f : Relativistic3DFullFourierEvolution.CoeffL2)
    (hf : HasThirdOrderMoment f) :
    ‖centeredCoeffOperator m h f -
      continuumDiracOutput m ⟨f, hf.mem_continuumDiracDomain m⟩‖ ≤
      h ^ 2 / 6 * thirdOrderMoment f := by
  exact centered_generator_quadratic_bound m h (by assumption) f hf
