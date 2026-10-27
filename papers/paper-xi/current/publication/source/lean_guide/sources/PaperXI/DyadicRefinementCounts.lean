import PaperXI.DyadicCounts
import PaperXI.DyadicCoordinates

/-! Cardinalities of the complete spaces of quadratic refinements with each
Arf invariant, including dimension zero. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.DyadicRefinementCounts
open scoped BigOperators Classical
open PaperXI.Dyadic PaperXI.DyadicAffine PaperXI.DyadicCoordinates
variable {ι : Type*} [Fintype ι]

instance refinementFintype : Fintype (Refinement (symplectic (ι := ι))) :=
  Fintype.ofEquiv (ι → F2 × F2) coordinateEquiv

def basisArf (q : Refinement (symplectic (ι := ι))) : F2 :=
  ∑ i, q.value (firstAxis i) * q.value (secondAxis i)

@[simp] theorem basisArf_coordinate (a : ι → F2 × F2) :
    basisArf (coordinateEquiv a) = arf a := by
  simp [basisArf, coordinateEquiv, coordinateRefinement, arf]

/-- Restrict the complete coordinate equivalence to either Arf fiber. -/
def arfFiberEquiv (t : F2) :
    {a : ι → F2 × F2 // arf a = t} ≃
      {q : Refinement (symplectic (ι := ι)) // basisArf q = t} :=
  coordinateEquiv.subtypeEquiv (fun a => by rw [basisArf_coordinate])

theorem even_fiber_card :
    Fintype.card {q : Refinement (symplectic (ι := ι)) // basisArf q = 0} =
      PaperXI.DyadicCounts.evenCount ι := by
  rw [← Fintype.card_congr (arfFiberEquiv (ι := ι) 0)]
  exact Fintype.card_subtype _

theorem odd_fiber_card :
    Fintype.card {q : Refinement (symplectic (ι := ι)) // basisArf q = 1} =
      PaperXI.DyadicCounts.oddCount ι := by
  rw [← Fintype.card_congr (arfFiberEquiv (ι := ι) 1)]
  exact Fintype.card_subtype _

/-- The exact even Arf count for all ranks, with integer exponent r - 1. -/
theorem even_refinement_count :
    (Fintype.card {q : Refinement (symplectic (ι := ι)) // basisArf q = 0} : ℚ) =
      (2 : ℚ) ^ ((Fintype.card ι : ℤ) - 1) * ((2 : ℚ) ^ Fintype.card ι + 1) := by
  rw [even_fiber_card]
  exact PaperXI.DyadicCounts.even_factored_rational

/-- The exact odd Arf count for all ranks, with integer exponent r - 1. -/
theorem odd_refinement_count :
    (Fintype.card {q : Refinement (symplectic (ι := ι)) // basisArf q = 1} : ℚ) =
      (2 : ℚ) ^ ((Fintype.card ι : ℤ) - 1) * ((2 : ℚ) ^ Fintype.card ι - 1) := by
  rw [odd_fiber_card]
  exact PaperXI.DyadicCounts.odd_factored_rational

end PaperXI.DyadicRefinementCounts
