import FiniteCyclicTamePairing
import TameInertiaRelation

/-!
# Finite cyclic Taylor--Wiles pairing capstone

At residue-field norm `q = 1`, the linearized tame relation space is exactly
the dual of actual first group cohomology for a finite cyclic quotient, under
the explicit zero-norm hypothesis.  The representative formula is `tr(PX)`.
-/

namespace Komorebi.StrongArtin.FiniteCyclicTaylorWilesPairingCapstone

open CategoryTheory
open Rep
open groupCohomology
open Komorebi.StrongArtin.FiniteCyclicH1Model
open Komorebi.StrongArtin.FiniteCyclicTamePairing
open Komorebi.StrongArtin.FrobeniusCocycleQuotient
open Komorebi.StrongArtin.LocalFrobeniusPerfectPairing
open Komorebi.StrongArtin.SpectralTraceConjugacy
open Komorebi.StrongArtin.TameInertiaRelation

noncomputable section

universe u

variable {k G n : Type u} [Field k] [CommGroup G] [Fintype G]
  [Fintype n] [DecidableEq n]

/-- The tame relation space at `q = 1` is exactly the dual of finite cyclic
`H¹` in the Frobenius-conjugation model. -/
def tameRelationEquivCyclicH1Dual
    (ρ : Representation k G (Matrix n n k))
    (g : G) (hg : ∀ x, x ∈ Subgroup.zpowers g)
    (F : (Matrix n n k)ˣ)
    (hact : ρ g = conjugationLinear F)
    (hN : (Rep.of ρ).norm.hom.toLinearMap = 0) :
    tameInertiaRelationSpace F 1 ≃ₗ[k]
      Module.Dual k (groupCohomology.H1 (Rep.of ρ)) :=
  (LinearEquiv.ofEq
      (tameInertiaRelationSpace F 1)
      (frobeniusCentralizer F)
      (tameInertiaRelationSpace_one_eq_centralizer F)).trans
    (centralizerEquivCyclicH1Dual ρ g hg F hact hN)

/-- On a cyclic cohomology class represented by `X`, the tame pairing is exactly
`tr(PX)`. -/
@[simp]
theorem tameRelationEquivCyclicH1Dual_apply_class
    (ρ : Representation k G (Matrix n n k))
    (g : G) (hg : ∀ x, x ∈ Subgroup.zpowers g)
    (F : (Matrix n n k)ˣ)
    (hact : ρ g = conjugationLinear F)
    (hN : (Rep.of ρ).norm.hom.toLinearMap = 0)
    (P : tameInertiaRelationSpace F 1)
    (X : Matrix n n k) :
    tameRelationEquivCyclicH1Dual ρ g hg F hact hN P
        (h1ClassOfValue (Rep.of ρ) g hg hN X) =
      traceProbe P.1 X := by
  let Pcentral : frobeniusCentralizer F :=
    (LinearEquiv.ofEq
      (tameInertiaRelationSpace F 1)
      (frobeniusCentralizer F)
      (tameInertiaRelationSpace_one_eq_centralizer F)) P
  change centralizerEquivCyclicH1Dual ρ g hg F hact hN Pcentral
      (h1ClassOfValue (Rep.of ρ) g hg hN X) = traceProbe P.1 X
  rw [centralizerEquivCyclicH1Dual_apply_class]
  rfl

/-- Every functional on finite cyclic `H¹` has one unique representative
satisfying the linearized tame relation. -/
theorem exists_unique_tame_cyclic_h1_representative
    (ρ : Representation k G (Matrix n n k))
    (g : G) (hg : ∀ x, x ∈ Subgroup.zpowers g)
    (F : (Matrix n n k)ˣ)
    (hact : ρ g = conjugationLinear F)
    (hN : (Rep.of ρ).norm.hom.toLinearMap = 0)
    (φ : Module.Dual k (groupCohomology.H1 (Rep.of ρ))) :
    ∃! P : tameInertiaRelationSpace F 1,
      ∀ X : Matrix n n k,
        φ (h1ClassOfValue (Rep.of ρ) g hg hN X) = traceProbe P.1 X := by
  let P := (tameRelationEquivCyclicH1Dual ρ g hg F hact hN).symm φ
  have hP : ∀ X : Matrix n n k,
      φ (h1ClassOfValue (Rep.of ρ) g hg hN X) = traceProbe P.1 X := by
    intro X
    calc
      φ (h1ClassOfValue (Rep.of ρ) g hg hN X) =
          tameRelationEquivCyclicH1Dual ρ g hg F hact hN P
            (h1ClassOfValue (Rep.of ρ) g hg hN X) := by
              rw [show tameRelationEquivCyclicH1Dual ρ g hg F hact hN P = φ by
                exact (tameRelationEquivCyclicH1Dual ρ g hg F hact hN).apply_symm_apply φ]
      _ = traceProbe P.1 X :=
        tameRelationEquivCyclicH1Dual_apply_class ρ g hg F hact hN P X
  refine ⟨P, hP, ?_⟩
  intro Q hQ
  apply (tameRelationEquivCyclicH1Dual ρ g hg F hact hN).injective
  ext z
  obtain ⟨X, rfl⟩ := h1ClassOfValue_surjective (Rep.of ρ) g hg hN z
  rw [tameRelationEquivCyclicH1Dual_apply_class,
    tameRelationEquivCyclicH1Dual_apply_class]
  exact (hQ X).symm.trans (hP X)

end
end Komorebi.StrongArtin.FiniteCyclicTaylorWilesPairingCapstone

#print axioms Komorebi.StrongArtin.FiniteCyclicTaylorWilesPairingCapstone.tameRelationEquivCyclicH1Dual
#print axioms Komorebi.StrongArtin.FiniteCyclicTaylorWilesPairingCapstone.tameRelationEquivCyclicH1Dual_apply_class
#print axioms Komorebi.StrongArtin.FiniteCyclicTaylorWilesPairingCapstone.exists_unique_tame_cyclic_h1_representative
