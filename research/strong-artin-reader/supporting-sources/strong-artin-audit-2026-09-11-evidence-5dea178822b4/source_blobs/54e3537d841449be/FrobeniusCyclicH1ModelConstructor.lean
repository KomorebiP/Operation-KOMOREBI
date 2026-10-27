import FrobeniusCyclicH1Model

/-!
# Constructing the finite cyclic Frobenius model

The compatibility between the cyclic generator quotient and the Frobenius
coboundary quotient follows from a concrete intertwining identity: in matrix
coordinates, the cyclic generator acts by conjugation with residual Frobenius.
-/

namespace Komorebi.StrongArtin.FrobeniusCyclicH1ModelConstructor

open CategoryTheory
open Komorebi.StrongArtin.FrobeniusCocycleQuotient
open Komorebi.StrongArtin.FrobeniusCyclicH1Model

universe u
noncomputable section

variable {k G n : Type u}
  [Field k] [CommGroup G] [Fintype G]
  [Fintype n] [DecidableEq n]

omit [Fintype G] in
/-- If cyclic-generator action becomes Frobenius conjugation in matrix
coordinates, the generator-minus-one range is exactly the Frobenius coboundary
space. -/
theorem range_compatibility_of_generator_action
    (coeff : Rep.{u} k G) (generator : G)
    (frobenius : (Matrix n n k)ˣ)
    (coordinates : coeff.V ≃ₗ[k] Matrix n n k)
    (hgenerator : ∀ x : coeff.V,
      coordinates (coeff.ρ generator x) =
        conjugationLinear frobenius (coordinates x)) :
    Submodule.map coordinates.toLinearMap
      (LinearMap.range
        (Rep.applyAsHom coeff generator - 𝟙 coeff).hom.toLinearMap) =
      frobeniusCoboundaries frobenius := by
  ext X
  constructor
  · rintro ⟨_, ⟨x, rfl⟩, rfl⟩
    refine ⟨-coordinates x, ?_⟩
    change
      frobeniusCoboundaryMap frobenius (-coordinates x) =
        coordinates (coeff.ρ generator x - x)
    rw [map_sub, hgenerator]
    simp [frobeniusCoboundaryMap_apply, conjugationLinear_apply]
    abel
  · rintro ⟨X, rfl⟩
    let x : coeff.V := coordinates.symm (-X)
    refine ⟨(Rep.applyAsHom coeff generator - 𝟙 coeff).hom.toLinearMap x,
      ⟨x, rfl⟩, ?_⟩
    change
      coordinates (coeff.ρ generator x - x) =
        frobeniusCoboundaryMap frobenius X
    rw [map_sub, hgenerator]
    have hx : coordinates x = -X := coordinates.apply_symm_apply (-X)
    rw [hx]
    simp [conjugationLinear_apply, frobeniusCoboundaryMap_apply]
    abel

/-- Construct the finite cyclic Frobenius `H¹` model from the concrete generator
intertwining identity. -/
def Model.ofGeneratorAction
    (coeff : Rep.{u} k G) (generator : G)
    (generates : ∀ x, x ∈ Subgroup.zpowers generator)
    (norm_zero : coeff.norm.hom.toLinearMap = 0)
    (frobenius : (Matrix n n k)ˣ)
    (coordinates : coeff.V ≃ₗ[k] Matrix n n k)
    (hgenerator : ∀ x : coeff.V,
      coordinates (coeff.ρ generator x) =
        conjugationLinear frobenius (coordinates x)) :
    Model (k := k) (G := G) (n := n) where
  coeff := coeff
  generator := generator
  generates := generates
  norm_zero := norm_zero
  frobenius := frobenius
  coordinates := coordinates
  range_compatibility :=
    range_compatibility_of_generator_action
      coeff generator frobenius coordinates hgenerator

end
end Komorebi.StrongArtin.FrobeniusCyclicH1ModelConstructor

#print axioms Komorebi.StrongArtin.FrobeniusCyclicH1ModelConstructor.range_compatibility_of_generator_action
#print axioms Komorebi.StrongArtin.FrobeniusCyclicH1ModelConstructor.Model.ofGeneratorAction
