import PaperX.ConditionalArithmeticSpine

set_option autoImplicit false
namespace PaperX.Claim82IndependentAudit
open PaperX.RepresentationLimits PaperX.RepresentationClasses
open PaperX.ClassCompletion PaperX.InverseLimitLocalConditions
open PaperX.DeterminantSpine

variable {R G : Type} [CommRing R] [Group G]

-- Rank zero is permitted: its determinant is one, including at every precision.
example (ρ : MatrixRep R G (Fin 0)) (g : G) : determinantCharacter ρ g = 1 := by
  simp [determinantCharacter]

variable {ι : Type} [Fintype ι] [DecidableEq ι]
variable (I : Ideal R) [IsAdicComplete I R]

-- This consequence would fail if the closure premise hid an arbitrary existing
-- system rather than universally ranging over the actual compatible families.
example (C : ClassConditions (G := G) (ι := ι) I)
    (h : InverseLimitClosed I C (fun _ => False)) :
    ¬ ∃ ρ : MatrixRep R G ι, ∀ k, C.allowed k (classOf (reduce I ρ k)) := by
  rintro ⟨ρ, hρ⟩
  exact of_realization I C _ h ρ hρ

-- An empty local label family adds no unstated nonemptiness premise.
example (C : ClassConditions (G := G) (ι := ι) I)
    (P : Empty → MatrixRep R G ι → Prop) :
    InverseLimitClosed I C (fun ρ => ∀ s, P s ρ) := by
  intro f hf s
  exact s.elim

-- Target determinant values are actual units and satisfy the character law,
-- even though the main interface only supplies them as functions.
example (ρ : MatrixRep R G ι) (g h : G) :
    determinantCharacter ρ (g * h) =
      determinantCharacter ρ g * determinantCharacter ρ h :=
  (determinantCharacter ρ).map_mul g h

example (ρ : MatrixRep R G ι) (g : G) : IsUnit (determinantCharacter ρ g) := by
  exact IsUnit.map (determinantCharacter ρ) (Group.isUnit g)

#print axioms PaperX.ConditionalArithmeticSpine.adelic_finite_depth_completion
#print axioms PaperX.InverseLimitLocalConditions.inverseLimitClosed_iff_realizations
#print axioms PaperX.InverseLimitLocalConditions.changeCoefficients_pullback
#print axioms PaperX.DeterminantSpine.class_realization_has_common_determinant

end PaperX.Claim82IndependentAudit
