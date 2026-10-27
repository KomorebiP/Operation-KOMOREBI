import PaperX.Reconstruction
import Mathlib.LinearAlgebra.Matrix.Charpoly.Basic
import Mathlib.RepresentationTheory.Basic

/-! Actual matrix representations reconstructed from compatible finite quotients.
Completeness and separatedness are explicit. No companion existence is assumed
inside the constructions. A group homomorphism into matrices has invertible
images, and it is also converted to Mathlib's ordinary Representation type. -/
set_option autoImplicit false
namespace PaperX.RepresentationLimits
open scoped BigOperators
variable {R : Type*} [CommRing R] (I : Ideal R)

/-- A compatible scalar family is realized using the already checked ring-map
reconstruction, applied to evaluation of the polynomial generator. -/
def scalarFamily (a : (k : ℕ) → R ⧸ I^k)
    (h : ∀ {j k} (hjk : j ≤ k), Ideal.Quotient.factorPow I hjk (a k) = a j) :
    PaperX.Reconstruction.RingFamily (Polynomial R) I where
  maps k := Polynomial.eval₂RingHom (Ideal.Quotient.mk (I^k)) (a k)
  compatible := by
    intro j k hjk
    apply Polynomial.ringHom_ext
    · intro c
      simp
    · simpa using h hjk

noncomputable def scalarLift [IsAdicComplete I R] (a : (k : ℕ) → R ⧸ I^k)
    (h : ∀ {j k} (hjk : j ≤ k), Ideal.Quotient.factorPow I hjk (a k) = a j) : R :=
  PaperX.Reconstruction.reconstruct I (scalarFamily I a h) Polynomial.X

@[simp] theorem scalarLift_reduces [IsAdicComplete I R]
    (a : (k : ℕ) → R ⧸ I^k)
    (h : ∀ {j k} (hjk : j ≤ k), Ideal.Quotient.factorPow I hjk (a k) = a j) (k : ℕ) :
    Ideal.Quotient.mk (I^k) (scalarLift I a h) = a k := by
  have H := RingHom.congr_fun
    (PaperX.Reconstruction.reconstruct_reduces I (scalarFamily I a h) k) Polynomial.X
  simpa [scalarLift, scalarFamily] using H

/-- Equality is detected by all finite coefficient precisions. -/
theorem scalar_ext [IsHausdorff I R] {a b : R}
    (h : ∀ k, Ideal.Quotient.mk (I^k) a = Ideal.Quotient.mk (I^k) b) : a = b := by
  exact congrFun (IsHausdorff.funext' I (f := fun _ : Unit => a)
    (g := fun _ : Unit => b) (fun k _ => h k)) ()

variable {G : Type*} [Group G] {ι : Type*} [Fintype ι] [DecidableEq ι]

/-- This is an actual matrix-valued monoid homomorphism, not a family with a
postulated limit. Inverses follow from the source being a group. -/
abbrev MatrixRep (R : Type*) [CommRing R] (G : Type*) [Group G]
    (ι : Type*) [Fintype ι] [DecidableEq ι] := G →* Matrix ι ι R

def changeCoefficients {S : Type*} [CommRing S] (f : R →+* S)
    (ρ : MatrixRep R G ι) : MatrixRep S G ι :=
  f.mapMatrix.toMonoidHom.comp ρ

@[simp] theorem changeCoefficients_apply {S : Type*} [CommRing S]
    (f : R →+* S) (ρ : MatrixRep R G ι) (g : G) (i j : ι) :
    changeCoefficients f ρ g i j = f (ρ g i j) := rfl

def reduce (ρ : MatrixRep R G ι) (k : ℕ) : MatrixRep (R ⧸ I^k) G ι :=
  changeCoefficients (Ideal.Quotient.mk (I^k)) ρ

def transition {j k : ℕ} (h : j ≤ k) :
    MatrixRep (R ⧸ I^k) G ι → MatrixRep (R ⧸ I^j) G ι :=
  changeCoefficients (Ideal.Quotient.factorPow I h)

@[simp] theorem transition_reduce (ρ : MatrixRep R G ι) {j k : ℕ} (h : j ≤ k) :
    transition I h (reduce I ρ k) = reduce I ρ j := by
  ext g i l
  simp [transition, reduce]

@[simp] theorem transition_self {k : ℕ} (ρ : MatrixRep (R ⧸ I^k) G ι) :
    transition I (Nat.le_refl k) ρ = ρ := by
  ext g i j
  simp [transition]

/-- Full compatibility, including the unique trivial precision-zero quotient. -/
structure Family (R : Type*) [CommRing R] (I : Ideal R)
    (G : Type*) [Group G] (ι : Type*) [Fintype ι] [DecidableEq ι] where
  maps : (k : ℕ) → MatrixRep (R ⧸ I^k) G ι
  compatible : ∀ {j k} (h : j ≤ k), transition I h (maps k) = maps j

theorem family_ext {f g : Family R I G ι} (h : f.maps = g.maps) : f = g := by
  cases f
  cases g
  cases h
  rfl

def reduceFamily (ρ : MatrixRep R G ι) : Family R I G ι where
  maps := reduce I ρ
  compatible := transition_reduce I ρ

noncomputable def liftMatrix [IsAdicComplete I R] (f : Family R I G ι) (g : G) :
    Matrix ι ι R := fun i j => scalarLift I (fun k => f.maps k g i j)
      (fun h => congrArg (fun ρ => ρ g i j) (f.compatible h))

@[simp] theorem liftMatrix_reduces [IsAdicComplete I R] (f : Family R I G ι)
    (g : G) (k : ℕ) : (liftMatrix I f g).map (Ideal.Quotient.mk (I^k)) = f.maps k g := by
  ext i j
  simp only [liftMatrix, Matrix.map_apply]
  apply scalarLift_reduces
  intro j' k' hjk
  exact congrArg (fun ρ => ρ g i j) (f.compatible hjk)

omit [Fintype ι] [DecidableEq ι] in
/-- Entrywise separatedness gives equality of actual matrices. -/
theorem matrix_ext [IsHausdorff I R] {A B : Matrix ι ι R}
    (h : ∀ k, A.map (Ideal.Quotient.mk (I^k)) = B.map (Ideal.Quotient.mk (I^k))) : A = B := by
  ext i j
  exact scalar_ext I (fun k => congrArg (fun M => M i j) (h k))

noncomputable def reconstruct [IsAdicComplete I R] (f : Family R I G ι) :
    MatrixRep R G ι where
  toFun := liftMatrix I f
  map_one' := by
    apply matrix_ext I
    intro k
    rw [liftMatrix_reduces, map_one]
    symm
    exact (Ideal.Quotient.mk (I^k)).mapMatrix.map_one
  map_mul' g h := by
    apply matrix_ext I
    intro k
    rw [liftMatrix_reduces, Matrix.map_mul, liftMatrix_reduces, liftMatrix_reduces,
      map_mul]

@[simp] theorem reconstruct_reduces [IsAdicComplete I R] (f : Family R I G ι) (k : ℕ) :
    reduce I (reconstruct I f) k = f.maps k := by
  ext g i j
  exact congrArg (fun M => M i j) (liftMatrix_reduces I f g k)

theorem reconstruct_unique [IsAdicComplete I R] (f : Family R I G ι)
    (ρ : MatrixRep R G ι) (h : ∀ k, reduce I ρ k = f.maps k) : ρ = reconstruct I f := by
  ext g i j
  apply scalar_ext I
  intro k
  exact (congrArg (fun τ => τ g i j) (h k)).trans
    (congrArg (fun τ => τ g i j) (reconstruct_reduces I f k)).symm

@[simp] theorem reconstruct_reduce [IsAdicComplete I R] (ρ : MatrixRep R G ι) :
    reconstruct I (reduceFamily I ρ) = ρ :=
  (reconstruct_unique I _ ρ (fun _ => rfl)).symm

@[simp] theorem reduce_reconstruct [IsAdicComplete I R] (f : Family R I G ι) :
    reduceFamily I (reconstruct I f) = f := by
  apply family_ext
  funext k
  exact reconstruct_reduces I f k

/-- Complete inverse-limit equivalence of actual matrix representations. -/
noncomputable def representationEquiv [IsAdicComplete I R] :
    MatrixRep R G ι ≃ Family R I G ι where
  toFun := reduceFamily I
  invFun := reconstruct I
  left_inv := reconstruct_reduce I
  right_inv := reduce_reconstruct I

/-- The reconstructed matrices really are invertible, with inverse given by g^-1. -/
theorem reconstructed_inverse [IsAdicComplete I R] (f : Family R I G ι) (g : G) :
    reconstruct I f g * reconstruct I f g⁻¹ = 1 ∧
      reconstruct I f g⁻¹ * reconstruct I f g = 1 := by
  constructor <;> simp [← map_mul]

noncomputable def unitRepresentation [IsAdicComplete I R] (f : Family R I G ι) :
    G →* (Matrix ι ι R)ˣ := (reconstruct I f).toHomUnits

/-- Conversion to the ordinary representation on the finite free module. -/
noncomputable def linearRepresentation [IsAdicComplete I R] (f : Family R I G ι) :
    Representation R G (ι → R) :=
  Matrix.toLinAlgEquiv'.toAlgHom.toMonoidHom.comp (reconstruct I f)

/-- Characteristic polynomials, not only traces, commute with finite reduction. -/
theorem charpoly_reduces [IsAdicComplete I R] (f : Family R I G ι) (g : G) (k : ℕ) :
    Polynomial.map (Ideal.Quotient.mk (I^k)) (reconstruct I f g).charpoly =
      (f.maps k g).charpoly := by
  rw [← Matrix.charpoly_map]
  change ((liftMatrix I f g).map _).charpoly = _
  rw [liftMatrix_reduces]

/-- All prescribed integral characteristic-polynomial coefficients survive the limit. -/
theorem charpoly_of_all_reductions [IsAdicComplete I R] (f : Family R I G ι)
    (g : G) (P : Polynomial R)
    (h : ∀ k, (f.maps k g).charpoly = P.map (Ideal.Quotient.mk (I^k))) :
    (reconstruct I f g).charpoly = P := by
  apply Polynomial.ext
  intro n
  apply scalar_ext I
  intro k
  have H := congrArg (fun p : Polynomial (R ⧸ I^k) => p.coeff n)
    ((charpoly_reduces I f g k).trans (h k))
  simpa using H

end PaperX.RepresentationLimits
