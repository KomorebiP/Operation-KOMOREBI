import PaperX.MatrixProjector
import PaperX.PrecisionIdempotent

/-! End-to-end lifting of an actual summand inside a supplied finite-group carrier.
Only one sufficiently deep equivariant quotient projector is required. -/
set_option autoImplicit false
namespace PaperX.FiniteCarrierSummands
open PaperX.RepresentationLimits PaperX.MatrixProjector

variable {R Γ ι : Type*} [CommRing R] [IsDomain R]
  [Group Γ] [Fintype Γ] [Fintype ι] [DecidableEq ι]

/-- The carrier's integral projector is constructed, not an input. -/
theorem exists_split_projector (π : R) [IsAdicComplete (Ideal.span {π}) R]
    (e k : ℕ) (ρ : MatrixRep R Γ ι)
    (hΓ : (Fintype.card Γ : R) ≠ 0) (hdiv : (Fintype.card Γ : R) ∣ π^e)
    (hk : 0 < k) (B : Matrix ι ι (R ⧸ (Ideal.span {π})^(e+k)))
    (hB : B * B = B)
    (hcomm : ∀ g, (ρ g).map (Ideal.Quotient.mk ((Ideal.span {π})^(e+k))) * B =
      B * (ρ g).map (Ideal.Quotient.mk ((Ideal.span {π})^(e+k)))) :
    ∃ P : Projector ρ,
      P.matrix.map (Ideal.Quotient.mk ((Ideal.span {π})^k)) =
        B.map (Ideal.Quotient.factorPow (Ideal.span {π}) (Nat.le_add_left k e)) := by
  obtain ⟨E, hE, hred, hρ⟩ := PrecisionIdempotent.exists_idempotent_lift
    π e k ρ hΓ hdiv hk B hB hcomm
  exact ⟨⟨E, hE, hρ⟩, hred⟩

/-- Equivariant inclusion and retraction are actual maps of the actual image.
Their projection and the full carrier decomposition follow from the constructed
projector. Both summands reduce onto exactly the prescribed quotient submodules. -/
theorem exists_lifted_summand (π : R) [IsAdicComplete (Ideal.span {π}) R]
    (e k : ℕ) (ρ : MatrixRep R Γ ι)
    (hΓ : (Fintype.card Γ : R) ≠ 0) (hdiv : (Fintype.card Γ : R) ∣ π^e)
    (hk : 0 < k) (B : Matrix ι ι (R ⧸ (Ideal.span {π})^(e+k)))
    (hB : B * B = B)
    (hcomm : ∀ g, (ρ g).map (Ideal.Quotient.mk ((Ideal.span {π})^(e+k))) * B =
      B * (ρ g).map (Ideal.Quotient.mk ((Ideal.span {π})^(e+k)))) :
    ∃ P : Projector ρ,
      P.matrix.map (Ideal.Quotient.mk ((Ideal.span {π})^k)) =
        B.map (Ideal.Quotient.factorPow (Ideal.span {π}) (Nat.le_add_left k e)) ∧
      P.retraction.comp P.inclusion = LinearMap.id ∧
      P.inclusion.comp P.retraction = P.linear ∧
      (∀ g v, P.inclusion (P.image.toRepresentation g v) = carrier ρ g (P.inclusion v)) ∧
      (∀ g v, P.retraction (carrier ρ g v) = P.image.toRepresentation g (P.retraction v)) ∧
      (∀ w : ι → R ⧸ (Ideal.span {π})^k,
        (∃ v : P.image.toSubmodule,
          (Ideal.Quotient.mk ((Ideal.span {π})^k)) ∘ (v : ι → R) = w) ↔
        (B.map (Ideal.Quotient.factorPow (Ideal.span {π}) (Nat.le_add_left k e))).mulVec w = w) ∧
      (∀ w : ι → R ⧸ (Ideal.span {π})^k,
        (∃ v : P.kernel.toSubmodule,
          (Ideal.Quotient.mk ((Ideal.span {π})^k)) ∘ (v : ι → R) = w) ↔
        (B.map (Ideal.Quotient.factorPow (Ideal.span {π}) (Nat.le_add_left k e))).mulVec w = 0) := by
  obtain ⟨P, hP⟩ := exists_split_projector π e k ρ hΓ hdiv hk B hB hcomm
  refine ⟨P, hP, P.split_law, P.inclusion_retraction,
    P.inclusion_equivariant, P.retraction_equivariant, ?_, ?_⟩
  · intro w
    rw [P.image_reduction_iff _ Ideal.Quotient.mk_surjective,
      (P.changeCoefficients (Ideal.Quotient.mk ((Ideal.span {π})^k))).image_iff]
    change (P.matrix.map _).mulVec w = w ↔ _
    rw [hP]
  · intro w
    rw [P.kernel_reduction_iff _ Ideal.Quotient.mk_surjective]
    change (P.matrix.map _).mulVec w = 0 ↔ _
    rw [hP]

/-- The same projector defines a summand of any pullback through the finite group. -/
def pullback {G : Type*} [Group G] (ρ : MatrixRep R Γ ι)
    (P : Projector ρ) (q : G →* Γ) : Projector (ρ.comp q) where
  matrix := P.matrix
  idempotent := P.idempotent
  commutes g := P.commutes (q g)

omit [IsDomain R] [Fintype Γ] in
theorem pullback_projection (ρ : MatrixRep R Γ ι) (P : Projector ρ)
    {G : Type*} [Group G] (q : G →* Γ) : (pullback ρ P q).matrix = P.matrix := rfl

end PaperX.FiniteCarrierSummands
