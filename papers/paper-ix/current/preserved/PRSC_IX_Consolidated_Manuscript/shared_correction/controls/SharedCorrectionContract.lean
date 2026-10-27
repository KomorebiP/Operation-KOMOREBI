module

public import SharedCorrection

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace Komorebi.SharedCorrectionContract

/-- External statement contract: the quotient and simultaneous correction
condition are written explicitly, with no compatibility premise added. -/
theorem explicit_quotient_contract
    (R U V W : Type*) [CommRing R]
    [AddCommGroup U] [Module R U]
    [AddCommGroup V] [Module R V]
    [AddCommGroup W] [Module R W]
    (J : U →ₗ[R] V) (K : U →ₗ[R] W) (u v : U) :
    (Submodule.Quotient.mk u : U ⧸ (LinearMap.ker J ⊔ LinearMap.ker K)) =
      Submodule.Quotient.mk v ↔ ∃ w : U, J w = J u ∧ K w = K v :=
  SharedCorrection.quotient_mk_eq_iff_common J K u v

end Komorebi.SharedCorrectionContract

#print axioms Komorebi.SharedCorrectionContract.explicit_quotient_contract
