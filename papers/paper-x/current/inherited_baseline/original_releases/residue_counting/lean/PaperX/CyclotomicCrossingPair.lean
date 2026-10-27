import PaperX.CyclotomicCrossingCore
import Mathlib.FieldTheory.LinearDisjoint

/-!
# Constructing the crossing automorphism from a disjoint compositum

Both Galois intermediate fields are supplied, together with their disjointness
and compositum equality. The automorphism with prescribed restrictions is
constructed from the actual restriction homomorphism.
-/

set_option autoImplicit false

noncomputable section

namespace PaperX.CyclotomicCrossing

open IntermediateField

variable {K T : Type*} [Field K] [Field T] [Algebra K T]

/-- The pair of actual restrictions to two normal intermediate fields. -/
def restrictionPair (L A : IntermediateField K T) [Normal K L] [Normal K A] :
    (T ≃ₐ[K] T) →* ((L ≃ₐ[K] L) × (A ≃ₐ[K] A)) :=
  (AlgEquiv.restrictNormalHom L).prod (AlgEquiv.restrictNormalHom A)

/-- Restrictions determine an automorphism when the two fields generate `T`. -/
theorem restrictionPair_injective (L A : IntermediateField K T)
    [Normal K L] [Normal K A] (hsup : L ⊔ A = ⊤) :
    Function.Injective (restrictionPair L A) := by
  apply (MonoidHom.ker_eq_bot_iff _).mp
  rw [restrictionPair, MonoidHom.ker_prod, L.restrictNormalHom_ker,
    A.restrictNormalHom_ker, ← fixingSubgroup_sup, hsup, fixingSubgroup_top]

variable [FiniteDimensional K T] [IsGalois K T]

/-- Linear disjointness upgrades the injective restriction pair to a bijection. -/
theorem restrictionPair_bijective (L A : IntermediateField K T)
    [IsGalois K L] [IsGalois K A]
    (hdisj : L.LinearDisjoint A) (hsup : L ⊔ A = ⊤) :
    Function.Bijective (restrictionPair L A) := by
  apply (Nat.bijective_iff_injective_and_card _).mpr
  refine ⟨restrictionPair_injective L A hsup, ?_⟩
  rw [Nat.card_prod, IsGalois.card_aut_eq_finrank, IsGalois.card_aut_eq_finrank,
    IsGalois.card_aut_eq_finrank]
  have hdim := hdisj.finrank_sup
  rw [hsup, finrank_top'] at hdim
  exact hdim

/-- The actual Galois group of a disjoint compositum is the product of the
two factor Galois groups, via restriction. -/
def restrictionPairEquiv (L A : IntermediateField K T)
    [IsGalois K L] [IsGalois K A]
    (hdisj : L.LinearDisjoint A) (hsup : L ⊔ A = ⊤) :
    (T ≃ₐ[K] T) ≃* ((L ≃ₐ[K] L) × (A ≃ₐ[K] A)) :=
  MulEquiv.ofBijective (restrictionPair L A) (restrictionPair_bijective L A hdisj hsup)

/-- The chosen automorphism on the compositum with the prescribed two restrictions. -/
def crossingAutomorphism (L A : IntermediateField K T)
    [IsGalois K L] [IsGalois K A]
    (hdisj : L.LinearDisjoint A) (hsup : L ⊔ A = ⊤)
    (sigma : L ≃ₐ[K] L) (eta : A ≃ₐ[K] A) : T ≃ₐ[K] T :=
  (restrictionPairEquiv L A hdisj hsup).symm (sigma, eta)

/-- The constructed automorphism restricts to the prescribed pair. -/
theorem restrictionPair_crossingAutomorphism (L A : IntermediateField K T)
    [IsGalois K L] [IsGalois K A]
    (hdisj : L.LinearDisjoint A) (hsup : L ⊔ A = ⊤)
    (sigma : L ≃ₐ[K] L) (eta : A ≃ₐ[K] A) :
    restrictionPair L A (crossingAutomorphism L A hdisj hsup sigma eta) = (sigma, eta) :=
  (restrictionPairEquiv L A hdisj hsup).apply_symm_apply _

/-- If the order on the first factor divides that on the auxiliary factor,
restriction to the auxiliary field preserves the crossing automorphism's order. -/
theorem crossingAutomorphism_order (L A : IntermediateField K T)
    [IsGalois K L] [IsGalois K A]
    (hdisj : L.LinearDisjoint A) (hsup : L ⊔ A = ⊤)
    (sigma : L ≃ₐ[K] L) (eta : A ≃ₐ[K] A)
    (horder : orderOf sigma ∣ orderOf eta) :
    orderOf (crossingAutomorphism L A hdisj hsup sigma eta) = orderOf eta := by
  rw [← orderOf_injective (restrictionPair L A) (restrictionPair_injective L A hsup),
    restrictionPair_crossingAutomorphism, Prod.orderOf_mk, Nat.lcm_eq_right horder]

/-- The field-crossing identity `T = E A`, for the actual fixed field of the
constructed automorphism. -/
theorem crossing_fixedField_sup_eq_top (L A : IntermediateField K T)
    [IsGalois K L] [IsGalois K A]
    (hdisj : L.LinearDisjoint A) (hsup : L ⊔ A = ⊤)
    (sigma : L ≃ₐ[K] L) (eta : A ≃ₐ[K] A)
    (horder : orderOf sigma ∣ orderOf eta) :
    fixedField (Subgroup.zpowers (crossingAutomorphism L A hdisj hsup sigma eta)) ⊔ A = ⊤ := by
  apply fixedField_zpowers_sup_eq_top
  rw [crossingAutomorphism_order L A hdisj hsup sigma eta horder]
  exact congrArg (fun p => orderOf p.2)
    (restrictionPair_crossingAutomorphism L A hdisj hsup sigma eta)

/-- A supplied cyclic auxiliary field of the matching degree produces the
crossing automorphism, fixed-field identity, cyclic extension, and exact
relative degree without supplying a chosen auxiliary generator. -/
theorem exists_crossing_of_cyclic_auxiliary (L A : IntermediateField K T)
    [IsGalois K L] [IsGalois K A] [IsCyclic (A ≃ₐ[K] A)]
    (hdisj : L.LinearDisjoint A) (hsup : L ⊔ A = ⊤)
    (sigma : L ≃ₐ[K] L) (hdegree : Module.finrank K A = orderOf sigma) :
    ∃ rho : T ≃ₐ[K] T,
      AlgEquiv.restrictNormalHom L rho = sigma ∧
      fixedField (Subgroup.zpowers rho) ⊔ A = ⊤ ∧
      IsCyclic (T ≃ₐ[fixedField (Subgroup.zpowers rho)] T) ∧
      Module.finrank (fixedField (Subgroup.zpowers rho)) T = orderOf sigma := by
  obtain ⟨eta, heta⟩ := isCyclic_iff_exists_zpowers_eq_top.mp
    (inferInstance : IsCyclic (A ≃ₐ[K] A))
  have heta_order : orderOf eta = orderOf sigma := by
    rw [orderOf_eq_card_of_forall_mem_zpowers (fun x => by rw [heta]; exact Subgroup.mem_top x),
      IsGalois.card_aut_eq_finrank, hdegree]
  have hdiv : orderOf sigma ∣ orderOf eta := by rw [heta_order]
  let rho := crossingAutomorphism L A hdisj hsup sigma eta
  refine ⟨rho, ?_, crossing_fixedField_sup_eq_top L A hdisj hsup sigma eta hdiv,
    isCyclic_fixedField_zpowers rho, ?_⟩
  · exact congrArg Prod.fst (restrictionPair_crossingAutomorphism L A hdisj hsup sigma eta)
  · rw [finrank_fixedField_zpowers,
      crossingAutomorphism_order L A hdisj hsup sigma eta hdiv, heta_order]

end PaperX.CyclotomicCrossing
