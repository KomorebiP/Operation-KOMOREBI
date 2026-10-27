import KomorebiPhysics.SpectralEvolutionExamples
open KomorebiPhysics KomorebiPhysics.BoundedSpectral KomorebiPhysics.HarmonicSurrogates
open KomorebiPhysics.SpectralEvolution KomorebiPhysics.SpectralEvolutionExamples
open KomorebiPhysics.UnboundedExamples
open scoped Topology lp

namespace Test_RoughStateInDomain
noncomputable section
example : roughState ∈ DiagonalDomain.domain harmonicEigenvalue := by
  simp only [roughState_not_domain]

end
end Test_RoughStateInDomain
namespace Test_CoordinateDerivativeSuffices
noncomputable section
example : DifferentiableAt ℝ (fun s => evolution harmonicEigenvalue s roughState) 0 := by
  have coordinates := rough_coordinates_differentiable 0
  simp only [rough_orbit_not_differentiable]

end
end Test_CoordinateDerivativeSuffices
namespace Test_PhaseSmoothsOutsideDomain
noncomputable section
example : evolution harmonicEigenvalue 1 roughState ∈ DiagonalDomain.domain harmonicEigenvalue := by
  rw [domain_iff]
  simp only [roughState_not_domain]

end
end Test_PhaseSmoothsOutsideDomain
namespace Test_PhaseOperatorNormContinuous
noncomputable section
example : ContinuousAt (fun t => evolution harmonicEigenvalue t) 0 := by
  simp only [not_operator_norm_continuous]

end
end Test_PhaseOperatorNormContinuous
namespace Test_HalfTurnNormDistanceZero
noncomputable section
example : ‖evolution harmonicEigenvalue (halfTurnTime 100) -
    ContinuousLinearMap.id ℂ Space‖ = 0 := by
  rw [halfTurn_operator_distance]

end
end Test_HalfTurnNormDistanceZero
namespace Test_SmoothCutoffVelocityBounded
noncomputable section
example : ‖deriv (fun s => SpectralTruncation.cutoff 4
    (evolution harmonicEigenvalue s roughState)) 0‖ ^ 2 ≤ 1 := by
  rw [rough_cutoff_velocity_norm_sq]
  norm_num

end
end Test_SmoothCutoffVelocityBounded
namespace Test_CoherentObservableStationary
noncomputable section
example : HasDerivAt (fun t => ‖coherentAmplitude t‖ ^ 2 / 2) 0 0 := by
  apply coherent_observable_hasDerivAt.congr_deriv
  norm_num

end
end Test_CoherentObservableStationary
namespace Test_CoherentObservableWrongSign
noncomputable section
example : HasDerivAt (fun t => ‖coherentAmplitude t‖ ^ 2 / 2) (-12/25) 0 := by
  apply coherent_observable_hasDerivAt.congr_deriv
  norm_num

end
end Test_CoherentObservableWrongSign
