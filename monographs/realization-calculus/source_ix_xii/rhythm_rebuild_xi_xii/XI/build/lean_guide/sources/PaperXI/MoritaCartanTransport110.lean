import PaperXI.MoritaLattice110
import Mathlib.GroupTheory.Index

/-! Actual lattice-index transport under normalizing outer Cartan factors.
The intersection is transported by the additive conjugation equivalence;
relative index is preserved by its proved injectivity. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.MoritaCartanTransport110
open PaperXI.MoritaLattice110

section Conjugation
variable {D : Type*} [Ring D]

/-- The literal additive-subgroup image under unit conjugation. -/
def conjugate (L : AddSubgroup D) (u : Dˣ) : AddSubgroup D :=
  L.map (unitConjugation u).toAddMonoidHom

/-- The order of the conjugations agrees with multiplication of the units. -/
theorem unitConjugation_mul (u v : Dˣ) :
    (unitConjugation (u * v)).toAddMonoidHom =
      (unitConjugation u).toAddMonoidHom.comp (unitConjugation v).toAddMonoidHom := by
  ext x
  simp [unitConjugation, mul_assoc]

theorem unitConjugation_inv_apply_apply (u : Dˣ) (x : D) :
    unitConjugation u⁻¹ (unitConjugation u x) = x := by
  simp [unitConjugation, mul_assoc]

theorem conjugate_mul (L : AddSubgroup D) (u v : Dˣ) :
    conjugate L (u * v) = conjugate (conjugate L v) u := by
  unfold conjugate
  rw [unitConjugation_mul, AddSubgroup.map_map]

/-- Normalization fixes the actual subgroup image, not merely its size. -/
theorem conjugate_eq_of_normalizing (L : AddSubgroup D) (u : Dˣ)
    (hu : u ∈ normalizingUnits L) : conjugate L u = L := by
  ext x
  change x ∈ L.map (unitConjugation u).toAddMonoidHom ↔ x ∈ L
  rw [mem_conjugate]
  exact ((normalizingUnits L).inv_mem hu) x

/-- The additive equivalence carries the actual intersection to the intersection of images. -/
theorem conjugate_inf (L M : AddSubgroup D) (u : Dˣ) :
    conjugate (L ⊓ M) u = conjugate L u ⊓ conjugate M u :=
  AddSubgroup.map_inf L M (unitConjugation u).toAddMonoidHom (unitConjugation u).injective

/-- Removing the right factor and transporting by the left factor gives an
equality of the actual intersection subgroups. -/
theorem intersection_outer_factors (L : AddSubgroup D) (k₁ d k₂ : Dˣ)
    (hk₁ : k₁ ∈ normalizingUnits L) (hk₂ : k₂ ∈ normalizingUnits L) :
    L ⊓ conjugate L (k₁ * d * k₂) = conjugate (L ⊓ conjugate L d) k₁ := by
  rw [conjugate_mul L (k₁ * d) k₂, conjugate_eq_of_normalizing L k₂ hk₂,
    conjugate_mul L k₁ d, conjugate_inf, conjugate_eq_of_normalizing L k₁ hk₁]

/-- The actual lattice-relative-index is invariant under normalizing outer factors.
No final-index or quotient-cardinality premise is supplied. -/
theorem intersection_relIndex_outer_factors (L : AddSubgroup D) (k₁ d k₂ : Dˣ)
    (hk₁ : k₁ ∈ normalizingUnits L) (hk₂ : k₂ ∈ normalizingUnits L) :
    (L ⊓ L.map (unitConjugation (k₁ * d * k₂)).toAddMonoidHom).relIndex L =
      (L ⊓ L.map (unitConjugation d).toAddMonoidHom).relIndex L := by
  change (L ⊓ conjugate L (k₁ * d * k₂)).relIndex L =
    (L ⊓ conjugate L d).relIndex L
  calc
    _ = (conjugate (L ⊓ conjugate L d) k₁).relIndex (conjugate L k₁) := by
      rw [intersection_outer_factors L k₁ d k₂ hk₁ hk₂,
        conjugate_eq_of_normalizing L k₁ hk₁]
    _ = _ := AddSubgroup.relIndex_map_map_of_injective
      (L ⊓ conjugate L d) L (unitConjugation k₁).injective

end Conjugation

section IntegralMatrixUnits
variable {R D m : Type*} [Ring R] [Ring D] [Fintype m] [DecidableEq m]

/-- A genuine coefficient-matrix unit mapped into the endomorphism matrix ring. -/
def mappedMatrixUnit (φ : R →+* D) (k : (Matrix m m R)ˣ) : (Matrix m m D)ˣ :=
  Units.map φ.mapMatrix.toMonoidHom k

@[simp] theorem mappedMatrixUnit_val (φ : R →+* D) (k : (Matrix m m R)ˣ) :
    (mappedMatrixUnit φ k : Matrix m m D) = (k : Matrix m m R).map φ := rfl

@[simp] theorem mappedMatrixUnit_inv (φ : R →+* D) (k : (Matrix m m R)ˣ) :
    mappedMatrixUnit φ k⁻¹ = (mappedMatrixUnit φ k)⁻¹ := by
  exact map_inv
    (Units.map (φ.mapMatrix : Matrix m m R →+* Matrix m m D).toMonoidHom) k

/-- Bimodule stability supplies actual integral-unit conjugation stability. -/
theorem mappedMatrixUnit_conjugation_mem (φ : R →+* D)
    (L : AddSubgroup (Matrix m m D)) (hL : IsMatrixBimodule φ L)
    (k : (Matrix m m R)ˣ) {x : Matrix m m D} (hx : x ∈ L) :
    unitConjugation (mappedMatrixUnit φ k) x ∈ L := by
  have h := hL.2 ((k⁻¹ : (Matrix m m R)ˣ) : Matrix m m R) _
    (hL.1 (k : Matrix m m R) x hx)
  simpa [unitConjugation, ← mappedMatrixUnit_inv] using h

/-- Every actual mapped integral matrix unit normalizes the lattice. -/
theorem mappedMatrixUnit_mem_normalizingUnits (φ : R →+* D)
    (L : AddSubgroup (Matrix m m D)) (hL : IsMatrixBimodule φ L)
    (k : (Matrix m m R)ˣ) : mappedMatrixUnit φ k ∈ normalizingUnits L := by
  intro x
  constructor
  · intro hx
    have h := mappedMatrixUnit_conjugation_mem φ L hL k⁻¹ hx
    rw [mappedMatrixUnit_inv, unitConjugation_inv_apply_apply] at h
    exact h
  · exact mappedMatrixUnit_conjugation_mem φ L hL k

/-- The generic Cartan transport applies to actual mapped integral matrix factors. -/
theorem matrix_intersection_relIndex_outer_factors (φ : R →+* D)
    (L : AddSubgroup (Matrix m m D)) (hL : IsMatrixBimodule φ L)
    (k₁ k₂ : (Matrix m m R)ˣ) (d : (Matrix m m D)ˣ) :
    (L ⊓ L.map (unitConjugation (mappedMatrixUnit φ k₁ * d *
      mappedMatrixUnit φ k₂)).toAddMonoidHom).relIndex L =
        (L ⊓ L.map (unitConjugation d).toAddMonoidHom).relIndex L :=
  intersection_relIndex_outer_factors L (mappedMatrixUnit φ k₁) d
    (mappedMatrixUnit φ k₂) (mappedMatrixUnit_mem_normalizingUnits φ L hL k₁)
      (mappedMatrixUnit_mem_normalizingUnits φ L hL k₂)

end IntegralMatrixUnits
end PaperXI.MoritaCartanTransport110
