import FiniteCyclicH1Model
import FrobeniusCocycleQuotient

/-!
# Finite cyclic group cohomology in Frobenius matrix coordinates

This module identifies first cohomology of a finite cyclic quotient with the
Frobenius-cocycle quotient already used by the Strong Artin local model, under
an explicit zero-norm hypothesis.
-/

namespace Komorebi.StrongArtin.FiniteCyclicFrobeniusH1

open CategoryTheory
open Rep
open Rep.FiniteCyclicGroup
open groupCohomology
open Komorebi.StrongArtin.FiniteCyclicH1Model
open Komorebi.StrongArtin.FrobeniusCocycleQuotient

noncomputable section

universe u

variable {k G n : Type u} [Field k] [CommGroup G] [Fintype G]
  [Fintype n] [DecidableEq n]

omit [Fintype G] in
/-- The range of `ρ(g)-1` agrees with the range of `1-Ad(F)` whenever the
chosen cyclic generator acts by conjugation with `F`. -/
theorem range_generator_sub_one_eq_frobeniusCoboundaries
    (ρ : Representation k G (Matrix n n k))
    (g : G) (F : (Matrix n n k)ˣ)
    (hact : ρ g = conjugationLinear F) :
    LinearMap.range
        (applyAsHom (Rep.of ρ) g - 𝟙 (Rep.of ρ)).hom.toLinearMap =
      frobeniusCoboundaries F := by
  ext X
  constructor
  · rintro ⟨Y, rfl⟩
    refine ⟨-Y, ?_⟩
    change
      ((LinearMap.id : Matrix n n k →ₗ[k] Matrix n n k) - conjugationLinear F) (-Y) =
        ((ρ g) - (LinearMap.id : Matrix n n k →ₗ[k] Matrix n n k)) Y
    rw [hact]
    simp [sub_eq_add_neg, add_comm]
  · rintro ⟨Y, rfl⟩
    refine ⟨-Y, ?_⟩
    change
      ((ρ g) - (LinearMap.id : Matrix n n k →ₗ[k] Matrix n n k)) (-Y) =
        ((LinearMap.id : Matrix n n k →ₗ[k] Matrix n n k) - conjugationLinear F) Y
    rw [hact]
    simp [sub_eq_add_neg, add_comm]

/-- **Finite cyclic Frobenius `H¹` model.** If the cyclic norm vanishes and
its generator acts by Frobenius conjugation, group cohomology is the checked
matrix quotient by local Frobenius coboundaries. -/
def h1EquivFrobeniusQuotient
    (ρ : Representation k G (Matrix n n k))
    (g : G) (hg : ∀ x, x ∈ Subgroup.zpowers g)
    (F : (Matrix n n k)ˣ)
    (hact : ρ g = conjugationLinear F)
    (hN : (Rep.of ρ).norm.hom.toLinearMap = 0) :
    (Matrix n n k ⧸ frobeniusCoboundaries F) ≃ₗ[k]
      groupCohomology.H1 (Rep.of ρ) :=
  (Submodule.quotEquivOfEq
      (frobeniusCoboundaries F)
      (LinearMap.range
        (applyAsHom (Rep.of ρ) g - 𝟙 (Rep.of ρ)).hom.toLinearMap)
      (range_generator_sub_one_eq_frobeniusCoboundaries ρ g F hact).symm).trans
    (h1EquivValueQuotient (Rep.of ρ) g hg hN)

@[simp]
theorem h1EquivFrobeniusQuotient_mkQ
    (ρ : Representation k G (Matrix n n k))
    (g : G) (hg : ∀ x, x ∈ Subgroup.zpowers g)
    (F : (Matrix n n k)ˣ)
    (hact : ρ g = conjugationLinear F)
    (hN : (Rep.of ρ).norm.hom.toLinearMap = 0)
    (X : Matrix n n k) :
    h1EquivFrobeniusQuotient ρ g hg F hact hN
        ((frobeniusCoboundaries F).mkQ X) =
      h1ClassOfValue (Rep.of ρ) g hg hN X := by
  rfl

end
end Komorebi.StrongArtin.FiniteCyclicFrobeniusH1

#print axioms Komorebi.StrongArtin.FiniteCyclicFrobeniusH1.range_generator_sub_one_eq_frobeniusCoboundaries
#print axioms Komorebi.StrongArtin.FiniteCyclicFrobeniusH1.h1EquivFrobeniusQuotient
