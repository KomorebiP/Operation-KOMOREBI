import FiniteCyclicH1Quotient
import LocalFrobeniusPerfectPairing

namespace Komorebi.StrongArtin.FrobeniusCyclicH1Model

open CategoryTheory
open Komorebi.StrongArtin.FiniteCyclicH1Quotient
open Komorebi.StrongArtin.FrobeniusCocycleQuotient
open Komorebi.StrongArtin.LocalFrobeniusPerfectPairing
open Komorebi.StrongArtin.SpectralTraceConjugacy

universe u
noncomputable section
set_option maxHeartbeats 800000

variable {k G n : Type u}
  [Field k] [CommGroup G] [Fintype G] [Fintype n] [DecidableEq n]

/-- A finite cyclic cohomology model whose generator-minus-one quotient is
identified with the Frobenius conjugation quotient on matrices. -/
structure Model where
  coeff : Rep.{u} k G
  generator : G
  generates : ∀ x, x ∈ Subgroup.zpowers generator
  norm_zero : coeff.norm.hom.toLinearMap = 0
  frobenius : (Matrix n n k)ˣ
  coordinates : coeff.V ≃ₗ[k] Matrix n n k
  range_compatibility :
    Submodule.map coordinates.toLinearMap
      (LinearMap.range (Rep.applyAsHom coeff generator - 𝟙 coeff).hom.toLinearMap) =
      frobeniusCoboundaries frobenius

/-- Transport finite cyclic `H¹` to the Frobenius matrix quotient. -/
def Model.h1EquivFrobeniusQuotient (D : Model (k := k) (G := G) (n := n)) :
    groupCohomology D.coeff 1 ≃ₗ[k]
      Matrix n n k ⧸ frobeniusCoboundaries D.frobenius :=
  (cyclicH1QuotientEquiv D.coeff D.generator D.generates D.norm_zero).trans
    (Submodule.Quotient.equiv
      (LinearMap.range (Rep.applyAsHom D.coeff D.generator - 𝟙 D.coeff).hom.toLinearMap)
      (frobeniusCoboundaries D.frobenius)
      D.coordinates D.range_compatibility)

/-- The perfect Frobenius trace pairing transported to genuine finite cyclic group cohomology. -/
def Model.centralizerEquivH1Dual (D : Model (k := k) (G := G) (n := n)) :
    frobeniusCentralizer D.frobenius ≃ₗ[k]
      Module.Dual k (groupCohomology D.coeff 1) :=
  (centralizerEquivQuotientDual D.frobenius).trans
    D.h1EquivFrobeniusQuotient.dualMap

@[simp]
theorem Model.centralizerEquivH1Dual_apply
    (D : Model (k := k) (G := G) (n := n))
    (P : frobeniusCentralizer D.frobenius)
    (h : groupCohomology D.coeff 1) :
    D.centralizerEquivH1Dual P h =
      centralizerEquivQuotientDual D.frobenius P
        (D.h1EquivFrobeniusQuotient h) := rfl

/-- The transported pairing is perfect in the tame/projector variable. -/
theorem Model.centralizer_pairing_injective
    (D : Model (k := k) (G := G) (n := n)) :
    Function.Injective D.centralizerEquivH1Dual :=
  D.centralizerEquivH1Dual.injective

/-- Every linear functional on finite cyclic `H¹` has a unique Frobenius-centralizing
matrix representative. -/
theorem Model.exists_unique_centralizer_for_h1_functional
    (D : Model (k := k) (G := G) (n := n))
    (φ : Module.Dual k (groupCohomology D.coeff 1)) :
    ∃! P : frobeniusCentralizer D.frobenius,
      D.centralizerEquivH1Dual P = φ := by
  let P := D.centralizerEquivH1Dual.symm φ
  refine ⟨P, D.centralizerEquivH1Dual.apply_symm_apply φ, ?_⟩
  intro Q hQ
  exact D.centralizerEquivH1Dual.injective
    (hQ.trans (D.centralizerEquivH1Dual.apply_symm_apply φ).symm)

/-- Every nonzero genuine finite cyclic degree-one class is detected by a
Frobenius-centralizing trace direction. -/
theorem Model.exists_centralizer_detecting_h1
    (D : Model (k := k) (G := G) (n := n))
    (h : groupCohomology D.coeff 1) (hh : h ≠ 0) :
    ∃ P : frobeniusCentralizer D.frobenius,
      D.centralizerEquivH1Dual P h ≠ 0 := by
  obtain ⟨φ, hφ⟩ := Module.Projective.exists_dual_ne_zero k hh
  let P := D.centralizerEquivH1Dual.symm φ
  refine ⟨P, ?_⟩
  rw [show D.centralizerEquivH1Dual P = φ by
    exact D.centralizerEquivH1Dual.apply_symm_apply φ]
  exact hφ

end
end Komorebi.StrongArtin.FrobeniusCyclicH1Model

#print axioms Komorebi.StrongArtin.FrobeniusCyclicH1Model.Model.h1EquivFrobeniusQuotient
#print axioms Komorebi.StrongArtin.FrobeniusCyclicH1Model.Model.centralizerEquivH1Dual
#print axioms Komorebi.StrongArtin.FrobeniusCyclicH1Model.Model.exists_unique_centralizer_for_h1_functional
#print axioms Komorebi.StrongArtin.FrobeniusCyclicH1Model.Model.exists_centralizer_detecting_h1
