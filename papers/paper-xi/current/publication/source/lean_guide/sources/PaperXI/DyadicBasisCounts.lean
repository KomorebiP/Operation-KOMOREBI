import PaperXI.DyadicBasis
import PaperXI.DyadicRefinementCounts

/-! Counts of every actual refinement on an arbitrary space, conditional on
supplied symplectic coordinates. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.DyadicBasisCounts
open scoped BigOperators Classical
open PaperXI.Dyadic PaperXI.DyadicAffine PaperXI.DyadicCoordinates
variable {V ι : Type*} [AddCommGroup V] [Module F2 V] [Fintype ι]
variable {b : V →ₗ[F2] V →ₗ[F2] F2}

def arfFiberEquiv (e : V ≃ₗ[F2] (ι → F2 × F2))
    (hb : ∀ x y, b x y = symplectic (e x) (e y)) (t : F2) :
    {q : Refinement b // PaperXI.DyadicBasis.basisArf e q = t} ≃
      {q : Refinement (symplectic (ι := ι)) //
        PaperXI.DyadicRefinementCounts.basisArf q = t} :=
  (PaperXI.DyadicBasis.refinementEquiv e hb).subtypeEquiv (fun q => by rfl)

theorem even_count (e : V ≃ₗ[F2] (ι → F2 × F2))
    (hb : ∀ x y, b x y = symplectic (e x) (e y)) :
    (Nat.card {q : Refinement b // PaperXI.DyadicBasis.basisArf e q = 0} : ℚ) =
      (2 : ℚ) ^ ((Fintype.card ι : ℤ) - 1) * ((2 : ℚ) ^ Fintype.card ι + 1) := by
  rw [Nat.card_congr (arfFiberEquiv e hb 0), Nat.card_eq_fintype_card]
  exact PaperXI.DyadicRefinementCounts.even_refinement_count

theorem odd_count (e : V ≃ₗ[F2] (ι → F2 × F2))
    (hb : ∀ x y, b x y = symplectic (e x) (e y)) :
    (Nat.card {q : Refinement b // PaperXI.DyadicBasis.basisArf e q = 1} : ℚ) =
      (2 : ℚ) ^ ((Fintype.card ι : ℤ) - 1) * ((2 : ℚ) ^ Fintype.card ι - 1) := by
  rw [Nat.card_congr (arfFiberEquiv e hb 1), Nat.card_eq_fintype_card]
  exact PaperXI.DyadicRefinementCounts.odd_refinement_count

end PaperXI.DyadicBasisCounts
