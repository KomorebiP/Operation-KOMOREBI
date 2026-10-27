import BaseToAuxiliaryQuotient

/-!
# Exact augmentation quotient equivalence
-/

namespace Komorebi.StrongArtin.AugmentationQuotientEquiv

open Komorebi.StrongArtin.PolynomialExpressionTaylor
open Komorebi.StrongArtin.PolynomialSystemTaylor
open Komorebi.StrongArtin.PresentedAlgebraPoint
open Komorebi.StrongArtin.PolynomialRelationAlgebra
open Komorebi.StrongArtin.AugmentedRelationAlgebra
open Komorebi.StrongArtin.AuxiliaryIdealBasic
open Komorebi.StrongArtin.BaseToAuxiliaryQuotient

noncomputable section

set_option linter.unusedSectionVars false
set_option linter.unusedSimpArgs false
set_option maxHeartbeats 800000

variable {R ι κ Aux : Type*} [CommRing R] [DecidableEq Aux]

/-- Quotienting the augmented presentation by its auxiliary coordinates
recovers the base presented algebra exactly. -/

def auxiliaryQuotientEquivBase
    (system : System ι κ R) (column : Aux → (κ → R)) (Q : Finset Aux) :
    AuxiliaryKilledAlgebra system column Q ≃ₐ[R] PresentedAlgebra system :=
  AlgEquiv.ofAlgHom
    (auxiliaryQuotientToBase system column Q)
    (baseToAuxiliaryQuotient system column Q)
    (by
      apply Ideal.Quotient.algHom_ext R
      apply MvPolynomial.algHom_ext
      intro i
      change auxiliaryQuotientToBase system column Q
          (baseToAuxiliaryQuotient system column Q
            (PresentedAlgebraPoint.generator system i)) =
        PresentedAlgebraPoint.generator system i
      rw [baseToAuxiliaryQuotient_generator]
      change auxiliaryQuotientToBase system column Q
          (Ideal.Quotient.mk (auxiliaryIdeal system column Q)
            (augmentedGenerator system column Q (Sum.inl i))) = _
      rw [auxiliaryQuotientToBase_mk]
      rw [baseSpecialization_baseGenerator])
    (by
      apply Ideal.Quotient.algHom_ext R
      apply Ideal.Quotient.algHom_ext R
      apply MvPolynomial.algHom_ext
      intro s
      cases s with
      | inl i =>
          change baseToAuxiliaryQuotient system column Q
              (baseSpecialization system column Q
                (augmentedGenerator system column Q (Sum.inl i))) =
            Ideal.Quotient.mk (auxiliaryIdeal system column Q)
              (augmentedGenerator system column Q (Sum.inl i))
          rw [baseSpecialization_baseGenerator]
          rw [baseToAuxiliaryQuotient_generator]
          rfl
      | inr a =>
          change baseToAuxiliaryQuotient system column Q
              (baseSpecialization system column Q
                (augmentedGenerator system column Q (Sum.inr a))) =
            Ideal.Quotient.mk (auxiliaryIdeal system column Q)
              (augmentedGenerator system column Q (Sum.inr a))
          rw [baseSpecialization_auxGenerator]
          rw [map_zero]
          exact (auxiliaryGenerator_mk_eq_zero system column Q a).symm)

/-- The kernel of the augmentation specialization is exactly the ideal
spanned by the selected auxiliary coordinate classes. -/
theorem ker_baseSpecialization_eq_auxiliaryIdeal
    (system : System ι κ R) (column : Aux → (κ → R)) (Q : Finset Aux) :
    RingHom.ker (baseSpecialization system column Q).toRingHom =
      auxiliaryIdeal system column Q := by
  apply le_antisymm
  · intro x hx
    have hz :
        auxiliaryQuotientToBase system column Q
          (Ideal.Quotient.mk (auxiliaryIdeal system column Q) x) = 0 := by
      simpa using hx
    have hmk :
        Ideal.Quotient.mk (auxiliaryIdeal system column Q) x = 0 :=
      (auxiliaryQuotientEquivBase system column Q).injective
        (by simpa [auxiliaryQuotientEquivBase] using hz)
    exact Ideal.Quotient.eq_zero_iff_mem.mp hmk
  · exact auxiliaryIdeal_le_ker_baseSpecialization system column Q

end

end Komorebi.StrongArtin.AugmentationQuotientEquiv

#print axioms Komorebi.StrongArtin.AugmentationQuotientEquiv.auxiliaryQuotientEquivBase
#print axioms Komorebi.StrongArtin.AugmentationQuotientEquiv.ker_baseSpecialization_eq_auxiliaryIdeal
