import PaperX.OrthogonalLifting
import PaperX.FamilySummands
import PaperX.FamilyRigidity

/-! End-to-end finite-depth existence and labeled conjugacy classification
inside a supplied complete local finite-group carrier. -/
set_option autoImplicit false
namespace PaperX.FamilyClassification
open PaperX.RepresentationLimits PaperX.OrthogonalProjectors

variable {R Γ ι J : Type*} [CommRing R] [IsDomain R] [IsLocalRing R]
  [Group Γ] [Fintype Γ] [Fintype ι] [DecidableEq ι] [Fintype J]

/-- Every allowed deep family has a lift, and all lifts of its retained
reduction are equivariantly conjugate by a unit equal to the identity there. -/
theorem exists_family_unique_up_to_conjugacy
    (π : R) [IsAdicComplete (Ideal.span {π}) R] (hπ : ¬ IsUnit π)
    (e k : ℕ) (hk : 0 < k) (ρ : MatrixRep R Γ ι)
    (hΓ : (Fintype.card Γ : R) ≠ 0)
    (hdiv : (Fintype.card Γ : R) ∣ π^e)
    (Q : Family (reduce (Ideal.span {π}) ρ (e+k)) J) :
    ∃ E : Family ρ J,
      (∀ i, (E.projector i).matrix.map (Ideal.Quotient.mk ((Ideal.span {π})^k)) =
        (Q.projector i).matrix.map
          (Ideal.Quotient.factorPow (Ideal.span {π}) (Nat.le_add_left k e))) ∧
      ∀ F : Family ρ J,
        (∀ i, (F.projector i).matrix.map (Ideal.Quotient.mk ((Ideal.span {π})^k)) =
          (Q.projector i).matrix.map
            (Ideal.Quotient.factorPow (Ideal.span {π}) (Nat.le_add_left k e))) →
        ∃ U : (Matrix ι ι R)ˣ,
          (U : Matrix ι ι R) = FamilyRigidity.comparison E F ∧
          (U : Matrix ι ι R).map (Ideal.Quotient.mk ((Ideal.span {π})^k)) = 1 ∧
          (∀ g, ρ g * (U : Matrix ι ι R) = (U : Matrix ι ι R) * ρ g) ∧
          ∀ i, (U : Matrix ι ι R) * (E.projector i).matrix *
            (↑(U⁻¹) : Matrix ι ι R) = (F.projector i).matrix := by
  obtain ⟨E, hE⟩ := OrthogonalLifting.exists_family_lift π e k hk ρ hΓ hdiv Q
  refine ⟨E, hE, fun F hF => ?_⟩
  exact FamilyRigidity.exists_conjugating_unit_of_reduction π hπ k hk E F
    (fun i => (hE i).trans (hF i).symm)

end PaperX.FamilyClassification
