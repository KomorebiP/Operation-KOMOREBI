import PaperICompletion8.DivisionProduct
import Mathlib.Algebra.DirectSum.Module
import Mathlib.RingTheory.SimpleModule.Basic

/-! Literal natural modules, column decompositions, and regular multiplicities.
The matrices act on the LEFT. Taking columns is an A-linear rearrangement of
coordinates, not the false assertion that transpose preserves multiplication. -/
set_option autoImplicit false
set_option linter.unusedSectionVars false

namespace Komorebi.PaperICompletion8.RegularMultiplicity

open scoped BigOperators DirectSum
open Komorebi.SeedRankBasics Komorebi.SeedRankOperations
open Komorebi.PaperICompletion8.DivisionProduct

universe u v

section Natural
variable {D : Type u} [DivisionRing D]
variable {n : ℕ}

/-- A nonzero vector generates the natural module over a division ring. -/
theorem natural_nonzero_generates {x : Fin n → D} (hx : x ≠ 0) :
    Generates (Matrix (Fin n) (Fin n) D) (Fin n → D) {x} := by
  rw [generates_singleton_iff_surjective]
  obtain ⟨j, hj⟩ : ∃ j, x j ≠ 0 := by
    by_contra h
    apply hx
    funext i
    by_contra hi
    exact h ⟨i, hi⟩
  intro y
  let A : Matrix (Fin n) (Fin n) D := fun i k ↦ if k = j then y i / x j else 0
  refine ⟨A, ?_⟩
  funext i
  change (Matrix.mulVec A x) i = y i
  simp [A, Matrix.mulVec, dotProduct, hj]

/-- The exact canonical seed rank on a positive-dimensional natural module. -/
theorem natural_seedRank_eq_one (hn : 0 < n) :
    seedRank (Matrix (Fin n) (Fin n) D) (Fin n → D) = 1 := by
  classical
  let : Nonempty (Fin n) := ⟨⟨0, hn⟩⟩
  let x : Fin n → D := Pi.single ⟨0, hn⟩ 1
  have hx : x ≠ 0 := by
    intro h
    have hh := congrFun h ⟨0, hn⟩
    simp [x] at hh
  have hsurj := (generates_singleton_iff_surjective _ _ x).mp (natural_nonzero_generates hx)
  let : Module.Finite (Matrix (Fin n) (Fin n) D) (Fin n → D) :=
    Module.Finite.of_surjective (oneSeedMap _ _ x) hsurj
  exact (seedRank_eq_one_iff_cyclic _ _).mpr ⟨x, natural_nonzero_generates hx⟩

end Natural

section Product
variable {I : Type v} [Fintype I] [DecidableEq I]
variable {D : I → Type u} [∀ i, DivisionRing (D i)]
variable (d m : I → ℕ)

/-- The natural module of factor i, inflated along the actual coordinate projection. -/
abbrev Simple (i : I) := Fin (d i) → D i

/-- Scalar restriction along the coordinate ring homomorphism, not a central action. -/
scoped instance simpleModule (i : I) :
    Module (DivisionProductAlgebra (D := D) d) (Simple (D := D) d i) :=
  Module.compHom (Simple (D := D) d i)
    (Pi.evalRingHom (fun j ↦ Matrix (Fin (d j)) (Fin (d j)) (D j)) i)

/-- The scalar action selects exactly the ith matrix factor. -/
theorem simple_smul (a : DivisionProductAlgebra (D := D) d)
    (i : I) (x : Simple (D := D) d i) : a • x = Matrix.mulVec (a i) x := rfl

/-- The literal product of multiplicity copies of natural modules. -/
abbrev MultiplicityModule := ∀ i : I, Fin (m i) → Simple (D := D) d i

/-- Every nonzero vector of an inflated simple factor generates it. -/
theorem simple_nonzero_generates (i : I) {x : Simple (D := D) d i} (hx : x ≠ 0) :
    Generates (DivisionProductAlgebra (D := D) d) (Simple (D := D) d i) {x} := by
  rw [generates_singleton_iff_surjective]
  have h := (generates_singleton_iff_surjective _ _ x).mp (natural_nonzero_generates hx)
  intro y
  obtain ⟨a, ha⟩ := h y
  refine ⟨Pi.single i a, ?_⟩
  simpa only [oneSeedMap_apply, simple_smul, Pi.single_eq_same, Matrix.smul_eq_mulVec] using ha

/-- Regular matrix-ring coordinates are literally its columns. -/
def regularColumnsEquiv :
    DivisionProductAlgebra (D := D) d ≃ₗ[DivisionProductAlgebra (D := D) d]
      MultiplicityModule (D := D) d d where
  toFun a i j r := a i r j
  invFun x i r j := x i j r
  left_inv _ := rfl
  right_inv _ := rfl
  map_add' _ _ := rfl
  map_smul' a b := by
    funext i j r
    change (a i * b i) r j = (Matrix.mulVec (a i) (fun s ↦ b i s j)) r
    rfl

/-- The regular equivalence is a column rearrangement on every entry. -/
theorem regularColumnsEquiv_apply (a : DivisionProductAlgebra (D := D) d)
    (i : I) (j r : Fin (d i)) : regularColumnsEquiv d a i j r = a i r j := rfl

/-- The product-to-finite-direct-sum equivalence keeps the inflated actions. -/
noncomputable def multiplicityDirectSumEquiv :
    MultiplicityModule (D := D) d m ≃ₗ[DivisionProductAlgebra (D := D) d]
      ⨁ i : I, (Fin (m i) → Simple (D := D) d i) :=
  (DirectSum.linearEquivFunOnFintype (DivisionProductAlgebra (D := D) d) I
    (fun i ↦ Fin (m i) → Simple (D := D) d i)).symm

/-- The printed regular-module multiplicity equivalence over arbitrary division rings. -/
noncomputable def regularDirectSumEquiv :
    DivisionProductAlgebra (D := D) d ≃ₗ[DivisionProductAlgebra (D := D) d]
      ⨁ i : I, (Fin (d i) → Simple (D := D) d i) :=
  (regularColumnsEquiv d).trans (multiplicityDirectSumEquiv d d)

section Rectangular
local instance (priority := 100) blockModuleAction (i : I) :
    Module (Matrix (Fin (d i)) (Fin (d i)) (D i))
      (Matrix (Fin (d i)) (Fin (m i)) (D i)) := Matrix.Module.matrixModule

/-- Rectangular matrices are the literal multiplicity copies by columns. -/
def columnsEquiv :
    DivisionProductModule (D := D) d m ≃ₗ[DivisionProductAlgebra (D := D) d]
      MultiplicityModule (D := D) d m where
  toFun a i j r := a i r j
  invFun x i r j := x i j r
  left_inv _ := rfl
  right_inv _ := rfl
  map_add' _ _ := rfl
  map_smul' a x := by
    funext i j r
    change (∑ s, a i r s • x i s) j = ∑ s, a i r s * x i s j
    simp

/-- The multiplicity seed formula is about natural-module copies, not just a matrix alias. -/
theorem multiplicity_seedRank (hd : ∀ i, 0 < d i) :
    seedRank (DivisionProductAlgebra (D := D) d) (MultiplicityModule (D := D) d m) =
      (maxCeilDiv d m : Cardinal) := by
  rw [← seedRank_linearEquiv (columnsEquiv (D := D) d m)]
  exact divisionProduct_seedRank_eq_maxCeilDiv d m hd

/-- The exact finite-direct-sum form of the multiplicity formula. -/
theorem directSum_seedRank (hd : ∀ i, 0 < d i) :
    seedRank (DivisionProductAlgebra (D := D) d)
      (⨁ i : I, (Fin (m i) → Simple (D := D) d i)) =
        (maxCeilDiv d m : Cardinal) := by
  rw [← seedRank_linearEquiv (multiplicityDirectSumEquiv (D := D) d m)]
  exact multiplicity_seedRank d m hd

end Rectangular
end Product
end Komorebi.PaperICompletion8.RegularMultiplicity
