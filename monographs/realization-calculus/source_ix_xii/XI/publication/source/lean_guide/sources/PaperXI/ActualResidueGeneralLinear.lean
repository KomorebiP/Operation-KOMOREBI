import Mathlib.LinearAlgebra.Matrix.GeneralLinearGroup.Defs
import Mathlib.NumberTheory.LocalField.Basic

/-! Entrywise reduction of actual integral general linear groups.

The lifting argument works over any commutative local ring: lift each entry,
then use the nonzero reduced determinant to prove that the lifted determinant
is a unit. The final declarations specialize this to the given nonarchimedean
local field's own ring of integers and finite residue field.
-/
set_option autoImplicit false
noncomputable section
namespace PaperXI.ActualResidueGeneralLinear
open Matrix ValuativeRel

section LocalRing
variable (n : Type*) [Fintype n] [DecidableEq n]
variable (R : Type*) [CommRing R] [IsLocalRing R]

/-- Entrywise reduction from a local ring to its residue field. -/
def residueMap : GeneralLinearGroup n R →*
    GeneralLinearGroup n (IsLocalRing.ResidueField R) :=
  GeneralLinearGroup.map (IsLocalRing.residue R)

@[simp] theorem residueMap_apply (g : GeneralLinearGroup n R) (i j : n) :
    residueMap n R g i j = IsLocalRing.residue R (g i j) := rfl

/-- Lift all entries of an invertible residue matrix. Its determinant lifts to
an element outside the maximal ideal, hence is a unit. -/
theorem residueMap_surjective : Function.Surjective (residueMap n R) := by
  intro g
  choose s hs using (IsLocalRing.residue_surjective (R := R))
  let A : Matrix n n R := fun i j => s (g i j)
  have hA : A.map (IsLocalRing.residue R) = (g : Matrix n n _) := by
    ext i j
    exact hs (g i j)
  have hdet : IsUnit A.det := by
    apply (IsLocalRing.residue_ne_zero_iff_isUnit A.det).mp
    rw [RingHom.map_det, RingHom.mapMatrix_apply, hA]
    exact GeneralLinearGroup.det_ne_zero g
  refine ⟨GeneralLinearGroup.mk'' A hdet, ?_⟩
  apply GeneralLinearGroup.ext
  intro i j
  exact hs (g i j)
end LocalRing

section ActualField
variable (K : Type*) [Field K] [ValuativeRel K]
variable (n : Type*) [Fintype n] [DecidableEq n]

/-- The actual residue map of the given valued field's integral matrix group. -/
def reduction : GeneralLinearGroup n 𝒪[K] →* GeneralLinearGroup n 𝓀[K] :=
  residueMap n 𝒪[K]

@[simp] theorem reduction_apply (g : GeneralLinearGroup n 𝒪[K]) (i j : n) :
    reduction K n g i j = IsLocalRing.residue 𝒪[K] (g i j) := rfl

/-- Every invertible matrix over the actual residue field has an integral lift. -/
theorem reduction_surjective : Function.Surjective (reduction K n) :=
  residueMap_surjective n 𝒪[K]

variable [TopologicalSpace K] [IsNonarchimedeanLocalField K]

/-- Finiteness of the actual target follows from the local-field hypotheses. -/
theorem finite_reduction_target : Finite (GeneralLinearGroup n 𝓀[K]) :=
  inferInstance
end ActualField

end PaperXI.ActualResidueGeneralLinear
