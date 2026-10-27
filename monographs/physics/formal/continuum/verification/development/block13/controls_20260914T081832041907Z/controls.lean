import KomorebiPhysics.LadderExamples

namespace Check_ResidueWrongCharacterSign
open KomorebiPhysics KomorebiPhysics.BoundedSpectral
open KomorebiPhysics.LadderDomains KomorebiPhysics.LadderExamples
open KomorebiPhysics.LadderRouting KomorebiPhysics.ResidueProjectors
open scoped BigOperators lp
noncomputable section
example : (3 : ℂ)⁻¹ * ∑ k : ZMod 3,
    ZMod.stdAddChar ((1 : ZMod 3)*k) * ZMod.stdAddChar (k*(1 : ZMod 3)) = 1 := by
  rw [ResidueCharacters.wrong_sign_three]
  norm_num
end
end Check_ResidueWrongCharacterSign

namespace Check_ResidueMissingNormalization
open KomorebiPhysics KomorebiPhysics.BoundedSpectral
open KomorebiPhysics.LadderDomains KomorebiPhysics.LadderExamples
open KomorebiPhysics.LadderRouting KomorebiPhysics.ResidueProjectors
open scoped BigOperators lp
noncomputable section
example : ∑ k : ZMod 3,
    ZMod.stdAddChar (-((1 : ZMod 3)*k)) * ZMod.stdAddChar (k*(1 : ZMod 3)) = (1 : ℂ) := by
  rw [unnormalized_character_sum]
  norm_num
end
end Check_ResidueMissingNormalization

namespace Check_LadderWrongAmplitude
open KomorebiPhysics KomorebiPhysics.BoundedSpectral
open KomorebiPhysics.LadderDomains KomorebiPhysics.LadderExamples
open KomorebiPhysics.LadderRouting KomorebiPhysics.ResidueProjectors
open scoped BigOperators lp
noncomputable section
example : lower (single 9 1) = lp.single 2 8 (9 : ℂ) := by
  simp only [wrong_square_root_amplitude]
end
end Check_LadderWrongAmplitude

namespace Check_LadderLowerWrongLane
open KomorebiPhysics KomorebiPhysics.BoundedSpectral
open KomorebiPhysics.LadderDomains KomorebiPhysics.LadderExamples
open KomorebiPhysics.LadderRouting KomorebiPhysics.ResidueProjectors
open scoped BigOperators lp
noncomputable section
example : projector 3 0 (lower (packet 3 0 (single 9 1))) ≠ 0 := by
  simp only [lowering_wrong_lane, ne_eq, not_true_eq_false]
end
end Check_LadderLowerWrongLane

namespace Check_LadderRaiseWrongLane
open KomorebiPhysics KomorebiPhysics.BoundedSpectral
open KomorebiPhysics.LadderDomains KomorebiPhysics.LadderExamples
open KomorebiPhysics.LadderRouting KomorebiPhysics.ResidueProjectors
open scoped BigOperators lp
noncomputable section
example : projector 3 1 (raise (packet 3 2 (single 8 1))) ≠ 0 := by
  simp only [raising_wrong_lane, ne_eq, not_true_eq_false]
end
end Check_LadderRaiseWrongLane

namespace Check_LadderVacuumSurvives
open KomorebiPhysics KomorebiPhysics.BoundedSpectral
open KomorebiPhysics.LadderDomains KomorebiPhysics.LadderExamples
open KomorebiPhysics.LadderRouting KomorebiPhysics.ResidueProjectors
open scoped BigOperators lp
noncomputable section
example : lower (single 0 1) ≠ 0 := by
  simp only [vacuum_lowering, ne_eq, not_true_eq_false]
end
end Check_LadderVacuumSurvives

namespace Check_LadderLowerBounded
open KomorebiPhysics KomorebiPhysics.BoundedSpectral
open KomorebiPhysics.LadderDomains KomorebiPhysics.LadderExamples
open KomorebiPhysics.LadderRouting KomorebiPhysics.ResidueProjectors
open scoped BigOperators lp
noncomputable section
example : ∃ A : Space →L[ℂ] Space, ∀ x : domain, lower x = A x := by
  simp only [no_bounded_lower_extension]
end
end Check_LadderLowerBounded

namespace Check_LadderRaiseBounded
open KomorebiPhysics KomorebiPhysics.BoundedSpectral
open KomorebiPhysics.LadderDomains KomorebiPhysics.LadderExamples
open KomorebiPhysics.LadderRouting KomorebiPhysics.ResidueProjectors
open scoped BigOperators lp
noncomputable section
example : ∃ A : Space →L[ℂ] Space, ∀ x : domain, raise x = A x := by
  simp only [no_bounded_raise_extension]
end
end Check_LadderRaiseBounded

