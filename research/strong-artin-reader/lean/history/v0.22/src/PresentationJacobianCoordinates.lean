import PresentationObstructionExactSequence

/-!
# Jacobian coordinates of a polynomial presentation

The relation differential map in `Algebra.Presentation` is the transpose
Jacobian of the chosen relations.  This file records the coordinate formulas
needed to compare a displayed presentation matrix with the intrinsic cotangent
complex.
-/

namespace Komorebi.StrongArtin.PresentationJacobianCoordinates

open Module MvPolynomial
open Komorebi.StrongArtin.PresentationObstructionExactSequence

noncomputable section

universe u v w t

variable {R : Type u} {S : Type v} {ι : Type w} {σ : Type t}
  [CommRing R] [CommRing S] [Algebra R S]

/-- The Jacobian entry of relation `r` with respect to generator `i`, evaluated
in the presented algebra. -/
def relationJacobianEntry
    (P : Algebra.Presentation R S ι σ) (r : σ) (i : ι) : S :=
  aeval P.val (pderiv i (P.relation r))

/-- The Jacobian matrix of the selected relation family.  Rows are relations
and columns are generators. -/
def relationJacobianMatrix
    (P : Algebra.Presentation R S ι σ) : Matrix σ ι S :=
  fun r i => relationJacobianEntry P r i

set_option backward.isDefEq.respectTransparency false in
/-- A basis relation is sent by the relation differential map to the
corresponding row of the Jacobian matrix. -/
theorem relationDifferentialMap_single_apply
    (P : Algebra.Presentation R S ι σ) (r : σ) (i : ι) :
    relationDifferentialMap P (Finsupp.single r 1) i =
      relationJacobianMatrix P r i := by
  have hmap : relationDifferentialMap P (Finsupp.single r 1) =
      P.differentialsRelations.relation r := by
    change P.differentialsRelations.map (Finsupp.single r 1) =
      P.differentialsRelations.relation r
    exact P.differentialsRelations.map_single r
  rw [hmap]
  simp [Algebra.Presentation.differentialsRelations,
    relationJacobianMatrix, relationJacobianEntry,
    KaehlerDifferential.mvPolynomialBasis_repr_apply]


set_option backward.isDefEq.respectTransparency false in
/-- For an arbitrary relation vector, the relation differential is the
finite-support transpose-Jacobian action. -/
theorem relationDifferentialMap_apply
    (P : Algebra.Presentation R S ι σ) (x : σ →₀ S) (i : ι) :
    relationDifferentialMap P x i =
      x.sum (fun r a => a * relationJacobianMatrix P r i) := by
  classical
  change (Finsupp.linearCombination S
    P.differentialsRelations.relation x) i = _
  rw [Finsupp.linearCombination_apply, Finsupp.sum_apply]
  apply Finsupp.sum_congr
  intro r hr
  have hrj : P.differentialsRelations.relation r i =
      relationJacobianMatrix P r i := by
    have h := relationDifferentialMap_single_apply P r i
    change P.differentialsRelations.map (Finsupp.single r 1) i = _ at h
    simpa using h
  simp [hrj]

/-- Membership in the presentation obstruction kernel is exactly annihilation
by every column of the displayed Jacobian transpose. -/
theorem mem_presentationObstructionDual_iff_jacobianTranspose
    (P : Algebra.Presentation R S ι σ) (x : σ →₀ S) :
    x ∈ LinearMap.ker (relationDifferentialMap P) ↔
      ∀ i : ι, x.sum (fun r a => a * relationJacobianMatrix P r i) = 0 := by
  constructor
  · intro hx i
    change relationDifferentialMap P x = 0 at hx
    have hi := congrArg (fun y : ι →₀ S => y i) hx
    simpa [relationDifferentialMap_apply] using hi
  · intro hx
    change relationDifferentialMap P x = 0
    ext i
    simpa [relationDifferentialMap_apply] using hx i

/-- In cotangent-space coordinates, the cotangent complex applied to a linear
combination of relation generators is exactly the relation differential map. -/
theorem cotangentComplex_hom₁_coordinates
    (P : Algebra.Presentation R S ι σ) (x : σ →₀ S) :
    P.cotangentSpaceBasis.repr
      (P.toExtension.cotangentComplex
        (Algebra.Presentation.differentials.hom₁ P x)) =
      relationDifferentialMap P x := by
  have h := DFunLike.congr_fun (cotangentComplex_comp_hom₁ P) x
  apply P.cotangentSpaceBasis.repr.symm.injective
  simpa using h

/-- The cotangent complex on an individual relation generator has coordinate
`(r,i)` equal to the corresponding Jacobian entry. -/
theorem cotangentComplex_relation_coordinate
    (P : Algebra.Presentation R S ι σ) (r : σ) (i : ι) :
    P.cotangentSpaceBasis.repr
      (P.toExtension.cotangentComplex
        (Algebra.Presentation.differentials.hom₁ P
          (Finsupp.single r 1))) i =
      relationJacobianMatrix P r i := by
  rw [cotangentComplex_hom₁_coordinates,
    relationDifferentialMap_single_apply]

/-- A relation vector belongs to the displayed Jacobian-transpose kernel iff
the associated conormal class maps to zero under the cotangent complex. -/
theorem mem_presentationObstructionDual_iff_cotangentComplex_eq_zero
    (P : Algebra.Presentation R S ι σ) (x : σ →₀ S) :
    x ∈ LinearMap.ker (relationDifferentialMap P) ↔
      P.toExtension.cotangentComplex
        (Algebra.Presentation.differentials.hom₁ P x) = 0 := by
  constructor
  · intro hx
    change relationDifferentialMap P x = 0 at hx
    have h := DFunLike.congr_fun (cotangentComplex_comp_hom₁ P) x
    simpa [hx] using h
  · intro hx
    change relationDifferentialMap P x = 0
    apply P.cotangentSpaceBasis.repr.symm.injective
    calc
      P.cotangentSpaceBasis.repr.symm (relationDifferentialMap P x) =
          P.toExtension.cotangentComplex
            (Algebra.Presentation.differentials.hom₁ P x) := by
              symm
              exact DFunLike.congr_fun (cotangentComplex_comp_hom₁ P) x
      _ = 0 := hx
      _ = P.cotangentSpaceBasis.repr.symm 0 := by simp

end

end Komorebi.StrongArtin.PresentationJacobianCoordinates

#print axioms Komorebi.StrongArtin.PresentationJacobianCoordinates.relationDifferentialMap_single_apply
#print axioms Komorebi.StrongArtin.PresentationJacobianCoordinates.relationDifferentialMap_apply
#print axioms Komorebi.StrongArtin.PresentationJacobianCoordinates.mem_presentationObstructionDual_iff_jacobianTranspose
#print axioms Komorebi.StrongArtin.PresentationJacobianCoordinates.cotangentComplex_hom₁_coordinates
#print axioms Komorebi.StrongArtin.PresentationJacobianCoordinates.mem_presentationObstructionDual_iff_cotangentComplex_eq_zero
