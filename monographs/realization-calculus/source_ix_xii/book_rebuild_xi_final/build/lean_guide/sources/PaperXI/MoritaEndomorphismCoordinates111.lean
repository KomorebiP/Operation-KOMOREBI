import PaperXI.MoritaActualCartan110
import PaperXI.ActualCuspidalCandidate105
import Mathlib.LinearAlgebra.Pi
import Mathlib.LinearAlgebra.Matrix.ToLin

/-! Natural block-endomorphism coordinates for the literal Morita carrier.
No basis of E over F is chosen: the block decomposition uses the finite
product's coordinate inclusions and projections. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.MoritaEndomorphismCoordinates111
open Matrix Module

section BlockEndomorphisms
variable (F E m : Type*) [Field F] [Field E] [Algebra F E]
  [Fintype m] [DecidableEq m]

/-- Assemble each row by the finite-product universal property, then assemble
the output coordinates. This is the natural block decomposition. -/
def blockLinearEquiv : Matrix m m (Module.End F E) ≃ₗ[F] Module.End F (m → E) :=
  (LinearEquiv.piCongrRight fun _ : m =>
    LinearMap.lsum F (fun _ : m => E) F).trans (LinearEquiv.linearMapPi F)

@[simp] theorem blockLinearEquiv_apply (A : Matrix m m (Module.End F E))
    (v : m → E) (i : m) :
    blockLinearEquiv F E m A v i = ∑ j, A i j (v j) := by
  change (∑ j, (A i j).comp (LinearMap.proj j)) v = _
  simp only [LinearMap.sum_apply, LinearMap.comp_apply, LinearMap.proj_apply]

/-- Matrix multiplication is composition of the actual block actions. -/
theorem blockLinearEquiv_mul (A B : Matrix m m (Module.End F E)) :
    blockLinearEquiv F E m (A * B) = blockLinearEquiv F E m A * blockLinearEquiv F E m B := by
  apply LinearMap.ext
  intro v
  funext i
  simp only [blockLinearEquiv_apply, Module.End.mul_apply, Matrix.mul_apply,
    LinearMap.sum_apply, map_sum]
  exact Finset.sum_comm

/-- The exact ring equivalence between Morita matrices and endomorphisms of E^m. -/
def blockRingEquiv : Matrix m m (Module.End F E) ≃+* Module.End F (m → E) where
  __ := (blockLinearEquiv F E m).toAddEquiv
  map_mul' := blockLinearEquiv_mul F E m

@[simp] theorem blockRingEquiv_apply (A : Matrix m m (Module.End F E))
    (v : m → E) (i : m) :
    blockRingEquiv F E m A v i = ∑ j, A i j (v j) :=
  blockLinearEquiv_apply F E m A v i

end BlockEndomorphisms

section ActualCoordinates
variable (F E m n : Type*) [Field F] [Field E] [Algebra F E]
  [TopologicalSpace F] [TopologicalSpace E]
  [Fintype m] [DecidableEq m] [Fintype n] [DecidableEq n]

/-- Transport the actual block carrier through the supplied F-coordinates. -/
def coordinateRingEquiv (e : (m → E) ≃L[F] (n → F)) :
    Matrix m m (Module.End F E) ≃+* Matrix n n F :=
  (blockRingEquiv F E m).trans
    ((e.toLinearEquiv.conjAlgEquiv F).toRingEquiv.trans
      LinearMap.toMatrixAlgEquiv'.toRingEquiv)

/-- The induced map on genuine units of the Morita carrier. -/
def coordinateUnitMap (e : (m → E) ≃L[F] (n → F)) :
    (Matrix m m (Module.End F E))ˣ →* GL n F :=
  Units.map (coordinateRingEquiv F E m n e).toMonoidHom

omit [TopologicalSpace F] [TopologicalSpace E] in
/-- The block embedding acts exactly as the existing restricted-scalar E-matrix action. -/
theorem blockRingEquiv_centralizerEmbedding (y : GL m E) :
    blockRingEquiv F E m (PaperXI.MoritaActualCartan110.centralizerEmbedding F E m y :
      Matrix m m (Module.End F E)) =
        (PaperXI.ActualELatticeResidue59.restrictScalarMatrix F E m y).toLinearMap := by
  apply LinearMap.ext
  intro v
  funext i
  rw [blockRingEquiv_apply]
  rfl

/-- The supplied-coordinate unit action agrees with the block endomorphism action. -/
theorem coordinateAut_coordinateUnitMap (e : (m → E) ≃L[F] (n → F))
    (u : (Matrix m m (Module.End F E))ˣ) (v : m → E) :
    PaperXI.LatticeCongruenceTopology60.coordinateAut e (coordinateUnitMap F E m n e u) v =
      blockRingEquiv F E m (u : Matrix m m (Module.End F E)) v := by
  rw [PaperXI.LatticeCongruenceTopology60.coordinateAut_apply]
  change e.symm ((LinearMap.toMatrix'
    ((e.toLinearEquiv.conjAlgEquiv F) (blockRingEquiv F E m (u : Matrix m m (Module.End F E)))))
      *ᵥ e v) = _
  rw [LinearMap.toMatrix'_mulVec]
  change e.symm (e (blockRingEquiv F E m (u : Matrix m m (Module.End F E))
    (e.symm (e v)))) = _
  simp only [e.symm_apply_apply]

/-- The Morita centralizer maps to the literal existing centralizer on the original F-carrier. -/
theorem coordinateUnitMap_centralizer (e : (m → E) ≃L[F] (n → F)) (y : GL m E) :
    coordinateUnitMap F E m n e
      (PaperXI.MoritaActualCartan110.centralizerEmbedding F E m y) =
        PaperXI.ActualCuspidalCandidate105.centralizerMap F E m n e y := by
  apply (PaperXI.LatticeCongruenceTopology60.coordinateAut e).injective
  change PaperXI.LatticeCongruenceTopology60.coordinateAut e
    (coordinateUnitMap F E m n e
      (PaperXI.MoritaActualCartan110.centralizerEmbedding F E m y)) =
        PaperXI.LatticeCongruenceTopology60.coordinateAut e
          ((PaperXI.LatticeCongruenceTopology60.coordinateAut e).symm
            (PaperXI.ActualELatticeResidue59.restrictScalarMatrix F E m y))
  rw [MulEquiv.apply_symm_apply]
  apply LinearEquiv.ext
  intro v
  rw [coordinateAut_coordinateUnitMap]
  exact congrArg (fun f : Module.End F (m → E) => f v)
    (blockRingEquiv_centralizerEmbedding F E m y)

/-- Ring transport intertwines the actual unit-conjugation actions. -/
theorem coordinateRingEquiv_unitConjugation (e : (m → E) ≃L[F] (n → F))
    (u : (Matrix m m (Module.End F E))ˣ) (x : Matrix m m (Module.End F E)) :
    coordinateRingEquiv F E m n e (PaperXI.MoritaLattice110.unitConjugation u x) =
      PaperXI.MoritaLattice110.unitConjugation (coordinateUnitMap F E m n e u)
        (coordinateRingEquiv F E m n e x) := by
  change coordinateRingEquiv F E m n e ((u : Matrix m m (Module.End F E)) * x *
    ((u⁻¹ : (Matrix m m (Module.End F E))ˣ) : Matrix m m (Module.End F E))) = _
  change _ = coordinateRingEquiv F E m n e (u : Matrix m m (Module.End F E)) *
    coordinateRingEquiv F E m n e x * coordinateRingEquiv F E m n e
      ((u⁻¹ : (Matrix m m (Module.End F E))ˣ) : Matrix m m (Module.End F E))
  simp only [map_mul]

/-- The literal image of a conjugated lattice is the conjugate of its image. -/
theorem coordinate_map_conjugate (e : (m → E) ≃L[F] (n → F))
    (L : AddSubgroup (Matrix m m (Module.End F E)))
    (u : (Matrix m m (Module.End F E))ˣ) :
    (L.map (PaperXI.MoritaLattice110.unitConjugation u).toAddMonoidHom).map
      (coordinateRingEquiv F E m n e).toAddMonoidHom =
        (L.map (coordinateRingEquiv F E m n e).toAddMonoidHom).map
          (PaperXI.MoritaLattice110.unitConjugation (coordinateUnitMap F E m n e u)).toAddMonoidHom := by
  rw [AddSubgroup.map_map, AddSubgroup.map_map]
  congr 1
  apply AddMonoidHom.ext
  intro x
  exact coordinateRingEquiv_unitConjugation F E m n e u x

/-- The relative index of the actual conjugate intersection is preserved in F-matrix coordinates. -/
theorem coordinate_intersection_relIndex (e : (m → E) ≃L[F] (n → F))
    (L : AddSubgroup (Matrix m m (Module.End F E)))
    (u : (Matrix m m (Module.End F E))ˣ) :
    ((L.map (coordinateRingEquiv F E m n e).toAddMonoidHom) ⊓
      (L.map (coordinateRingEquiv F E m n e).toAddMonoidHom).map
        (PaperXI.MoritaLattice110.unitConjugation (coordinateUnitMap F E m n e u)).toAddMonoidHom).relIndex
          (L.map (coordinateRingEquiv F E m n e).toAddMonoidHom) =
            (L ⊓ L.map (PaperXI.MoritaLattice110.unitConjugation u).toAddMonoidHom).relIndex L := by
  have h := AddSubgroup.map_inf L
    (L.map (PaperXI.MoritaLattice110.unitConjugation u).toAddMonoidHom)
    (coordinateRingEquiv F E m n e).toAddMonoidHom (coordinateRingEquiv F E m n e).injective
  rw [coordinate_map_conjugate F E m n e L u] at h
  rw [← h]
  exact AddSubgroup.relIndex_map_map_of_injective
    (L ⊓ L.map (PaperXI.MoritaLattice110.unitConjugation u).toAddMonoidHom) L
      (coordinateRingEquiv F E m n e).injective

section IntegralCoordinates
open ValuativeRel
variable [ValuativeRel E]

/-- Integral centralizer units agree with the existing integral-matrix coordinate map. -/
theorem coordinateUnitMap_integral (e : (m → E) ≃L[F] (n → F)) (k : GL m 𝒪[E]) :
    coordinateUnitMap F E m n e
      (PaperXI.MoritaCartanTransport110.mappedMatrixUnit
        (PaperXI.MoritaCornerRank110.coefficientMap F E) k) =
          (PaperXI.LatticeCongruenceTopology60.coordinateAut e).symm
            (PaperXI.ActualELatticeResidue59.integralMatrix F E m k) := by
  rw [← PaperXI.MoritaActualCartan110.centralizerEmbedding_integral F E m k,
    coordinateUnitMap_centralizer F E m n e]
  rfl

end IntegralCoordinates
end ActualCoordinates
end PaperXI.MoritaEndomorphismCoordinates111
