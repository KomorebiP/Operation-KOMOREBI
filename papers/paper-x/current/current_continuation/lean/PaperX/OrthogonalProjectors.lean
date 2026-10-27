import PaperX.MatrixProjector
import Mathlib.Algebra.BigOperators.Ring.Finset

/-! A complete labeled orthogonal family of actual equivariant projectors. -/
set_option autoImplicit false
namespace PaperX.OrthogonalProjectors
open PaperX.RepresentationLimits PaperX.MatrixProjector
open scoped BigOperators

variable {R Γ ι : Type*} [CommRing R] [Group Γ]
  [Fintype ι] [DecidableEq ι]

structure Family (ρ : MatrixRep R Γ ι) (J : Type*) [Fintype J] where
  projector : J → Projector ρ
  orthogonal : ∀ i j, i ≠ j → (projector i).matrix * (projector j).matrix = 0
  total : ∑ i, (projector i).matrix = 1

namespace Family
variable {ρ : MatrixRep R Γ ι} {J : Type*} [Fintype J] (E : Family ρ J)

theorem product [DecidableEq J] (i j : J) :
    (E.projector i).matrix * (E.projector j).matrix =
      if i = j then (E.projector i).matrix else 0 := by
  split
  · rename_i h
    subst j
    exact (E.projector i).idempotent
  · exact E.orthogonal i j ‹i ≠ j›

def changeCoefficients {S : Type*} [CommRing S] (f : R →+* S) :
    Family (RepresentationLimits.changeCoefficients f ρ) J where
  projector i := (E.projector i).changeCoefficients f
  orthogonal i j hij := by
    change ((E.projector i).matrix.map f) * ((E.projector j).matrix.map f) = 0
    rw [← Matrix.map_mul, E.orthogonal i j hij]
    exact f.mapMatrix.map_zero
  total := by
    change ∑ i, f.mapMatrix (E.projector i).matrix = 1
    rw [← map_sum, E.total, map_one]

end Family
end PaperX.OrthogonalProjectors
