import FiniteCyclicFrobeniusH1
import LocalFrobeniusPerfectPairing

/-!
# Perfect pairing with finite cyclic group cohomology

Under the zero-norm finite cyclic model, the checked Frobenius trace pairing
becomes an exact perfect pairing with actual `H¹` of the cyclic group.
-/

namespace Komorebi.StrongArtin.FiniteCyclicTamePairing

open CategoryTheory
open Rep
open groupCohomology
open Komorebi.StrongArtin.FiniteCyclicH1Model
open Komorebi.StrongArtin.FiniteCyclicFrobeniusH1
open Komorebi.StrongArtin.FrobeniusCocycleQuotient
open Komorebi.StrongArtin.SpectralTraceConjugacy
open Komorebi.StrongArtin.LocalFrobeniusPerfectPairing

noncomputable section

universe u

variable {k G n : Type u} [Field k] [CommGroup G] [Fintype G]
  [Fintype n] [DecidableEq n]

/-- The Frobenius centralizer is exactly the dual of finite cyclic `H¹` in the
zero-norm matrix-conjugation model. -/
def centralizerEquivCyclicH1Dual
    (ρ : Representation k G (Matrix n n k))
    (g : G) (hg : ∀ x, x ∈ Subgroup.zpowers g)
    (F : (Matrix n n k)ˣ)
    (hact : ρ g = conjugationLinear F)
    (hN : (Rep.of ρ).norm.hom.toLinearMap = 0) :
    frobeniusCentralizer F ≃ₗ[k]
      Module.Dual k (groupCohomology.H1 (Rep.of ρ)) :=
  (centralizerEquivQuotientDual F).trans
    (LinearEquiv.dualMap
      (h1EquivFrobeniusQuotient ρ g hg F hact hN)).symm

/-- On the cohomology class represented by `X`, the pairing is exactly
`tr(PX)`. -/
@[simp]
theorem centralizerEquivCyclicH1Dual_apply_class
    (ρ : Representation k G (Matrix n n k))
    (g : G) (hg : ∀ x, x ∈ Subgroup.zpowers g)
    (F : (Matrix n n k)ˣ)
    (hact : ρ g = conjugationLinear F)
    (hN : (Rep.of ρ).norm.hom.toLinearMap = 0)
    (P : frobeniusCentralizer F)
    (X : Matrix n n k) :
    centralizerEquivCyclicH1Dual ρ g hg F hact hN P
        (h1ClassOfValue (Rep.of ρ) g hg hN X) =
      traceProbe P.1 X := by
  let e := h1EquivFrobeniusQuotient ρ g hg F hact hN
  change
    (LinearEquiv.dualMap e).symm
        (centralizerEquivQuotientDual F P)
        (h1ClassOfValue (Rep.of ρ) g hg hN X) =
      traceProbe P.1 X
  rw [← h1EquivFrobeniusQuotient_mkQ ρ g hg F hact hN X]
  have hdual := LinearEquiv.dualMap_apply e
    ((LinearEquiv.dualMap e).symm (centralizerEquivQuotientDual F P))
    ((frobeniusCoboundaries F).mkQ X)
  rw [(LinearEquiv.dualMap e).apply_symm_apply] at hdual
  rw [← hdual]
  exact centralizerEquivQuotientDual_apply_mkQ F P X


/-- A Frobenius-centralizing matrix gives a nonzero cyclic `H¹` functional
exactly when the matrix itself is nonzero. -/
@[simp]
theorem centralizerEquivCyclicH1Dual_ne_zero_iff
    (ρ : Representation k G (Matrix n n k))
    (g : G) (hg : ∀ x, x ∈ Subgroup.zpowers g)
    (F : (Matrix n n k)ˣ)
    (hact : ρ g = conjugationLinear F)
    (hN : (Rep.of ρ).norm.hom.toLinearMap = 0)
    (P : frobeniusCentralizer F) :
    centralizerEquivCyclicH1Dual ρ g hg F hact hN P ≠ 0 ↔ P ≠ 0 := by
  exact LinearEquiv.map_ne_zero_iff (centralizerEquivCyclicH1Dual ρ g hg F hact hN)

/-- Every functional on finite cyclic `H¹` has a unique Frobenius-centralizing
matrix representative. -/
theorem exists_unique_cyclic_h1_representative
    (ρ : Representation k G (Matrix n n k))
    (g : G) (hg : ∀ x, x ∈ Subgroup.zpowers g)
    (F : (Matrix n n k)ˣ)
    (hact : ρ g = conjugationLinear F)
    (hN : (Rep.of ρ).norm.hom.toLinearMap = 0)
    (φ : Module.Dual k (groupCohomology.H1 (Rep.of ρ))) :
    ∃! P : frobeniusCentralizer F,
      ∀ X : Matrix n n k,
        φ (h1ClassOfValue (Rep.of ρ) g hg hN X) = traceProbe P.1 X := by
  let P := (centralizerEquivCyclicH1Dual ρ g hg F hact hN).symm φ
  have hP : ∀ X : Matrix n n k,
      φ (h1ClassOfValue (Rep.of ρ) g hg hN X) = traceProbe P.1 X := by
    intro X
    calc
      φ (h1ClassOfValue (Rep.of ρ) g hg hN X) =
          centralizerEquivCyclicH1Dual ρ g hg F hact hN P
            (h1ClassOfValue (Rep.of ρ) g hg hN X) := by
              rw [show centralizerEquivCyclicH1Dual ρ g hg F hact hN P = φ by
                exact (centralizerEquivCyclicH1Dual ρ g hg F hact hN).apply_symm_apply φ]
      _ = traceProbe P.1 X :=
        centralizerEquivCyclicH1Dual_apply_class ρ g hg F hact hN P X
  refine ⟨P, hP, ?_⟩
  intro Q hQ
  apply (centralizerEquivCyclicH1Dual ρ g hg F hact hN).injective
  ext z
  obtain ⟨X, rfl⟩ := h1ClassOfValue_surjective (Rep.of ρ) g hg hN z
  rw [centralizerEquivCyclicH1Dual_apply_class,
    centralizerEquivCyclicH1Dual_apply_class]
  exact (hQ X).symm.trans (hP X)

end
end Komorebi.StrongArtin.FiniteCyclicTamePairing

#print axioms Komorebi.StrongArtin.FiniteCyclicTamePairing.centralizerEquivCyclicH1Dual
#print axioms Komorebi.StrongArtin.FiniteCyclicTamePairing.centralizerEquivCyclicH1Dual_apply_class
#print axioms Komorebi.StrongArtin.FiniteCyclicTamePairing.centralizerEquivCyclicH1Dual_ne_zero_iff
#print axioms Komorebi.StrongArtin.FiniteCyclicTamePairing.exists_unique_cyclic_h1_representative
