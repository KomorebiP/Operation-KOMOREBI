import Mathlib.LinearAlgebra.Matrix.GeneralLinearGroup.Basic
import Mathlib.Algebra.Group.TypeTags.Basic
import Mathlib.Tactic.Abel
import Mathlib.Tactic.FieldSimp

/-! Literal square-zero coordinate radicals, entrywise lifting, and contraction
by a normalized Cartan diagonal. Neither a contracting subgroup nor its lifts
are supplied to the matrix theorem. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.SplitRadical105
open Matrix
variable {ι R F k : Type*} [Fintype ι] [DecidableEq ι]
  [CommRing R] [Field F] [Field k]

/-- Matrix supported in the rectangle S times its complement. -/
def rect (S : Finset ι) (X : Matrix ι ι R) : Matrix ι ι R :=
  fun i j => if i ∈ S ∧ j ∉ S then X i j else 0

theorem rect_mul (S : Finset ι) (X Y : Matrix ι ι R) :
    rect S X * rect S Y = 0 := by
  ext i j
  apply Finset.sum_eq_zero
  intro t _
  by_cases ht : t ∈ S <;> simp [rect, ht]

omit [Fintype ι] in
theorem rect_add (S : Finset ι) (X Y : Matrix ι ι R) :
    rect S (X + Y) = rect S X + rect S Y := by
  ext i j
  by_cases h : i ∈ S ∧ j ∉ S <;> simp [rect, h]

/-- The inverse is supplied by square-zero, not by a determinant certificate. -/
def unip (S : Finset ι) (X : Matrix ι ι R) : GL ι R where
  val := 1 + rect S X
  inv := 1 - rect S X
  val_inv := by simp [mul_sub, add_mul, rect_mul]
  inv_val := by simp [sub_mul, mul_add, rect_mul]

theorem unip_add (S : Finset ι) (X Y : Matrix ι ι R) :
    unip S (X + Y) = unip S X * unip S Y := by
  apply Units.ext
  change 1 + rect S (X + Y) = (1 + rect S X) * (1 + rect S Y)
  rw [rect_add]
  simp only [add_mul, mul_add, one_mul, mul_one, rect_mul, add_zero]
  abel

theorem unip_zero (S : Finset ι) : unip S (0 : Matrix ι ι R) = 1 := by
  apply Units.ext
  ext i j
  simp [unip, rect]

def radicalMap (S : Finset ι) : Multiplicative (Matrix ι ι R) →* GL ι R where
  toFun X := unip S X.toAdd
  map_one' := unip_zero S
  map_mul' X Y := unip_add S X.toAdd Y.toAdd

theorem map_unip {R' : Type*} [CommRing R'] (f : R →+* R')
    (S : Finset ι) (X : Matrix ι ι R) :
    GeneralLinearGroup.map f (unip S X) = unip S (X.map f) := by
  apply Units.ext
  ext i j
  by_cases h : i ∈ S ∧ j ∉ S <;> by_cases hij : i = j <;>
    simp [unip, rect, h, hij]

/-- Invertible diagonal with literal entries and reciprocal inverse. -/
def diagonalGL (c : ι → F) (hc : ∀ i, c i ≠ 0) : GL ι F where
  val := diagonal c
  inv := diagonal (fun i => (c i)⁻¹)
  val_inv := by
    rw [diagonal_mul_diagonal]
    ext i j
    by_cases h : i = j <;> simp [diagonal, Matrix.one_apply, h, hc]
  inv_val := by
    rw [diagonal_mul_diagonal]
    ext i j
    by_cases h : i = j <;> simp [diagonal, Matrix.one_apply, h, hc]

def cartan (π : F) (hπ : π ≠ 0) (a : ι → ℕ) : GL ι F :=
  diagonalGL (fun i => (π ^ a i)⁻¹) (fun _ => inv_ne_zero (pow_ne_zero _ hπ))

def zeroSet (a : ι → ℕ) : Finset ι := Finset.univ.filter (fun i => a i = 0)

omit [DecidableEq ι] in
@[simp] theorem mem_zeroSet (a : ι → ℕ) (i : ι) : i ∈ zeroSet a ↔ a i = 0 := by
  simp [zeroSet]

/-- Conjugation by diag(pi^(-a_i)) contracts the radical at the zero/positive cut. -/
theorem cartan_conjugation (f : R →+* F) (π : R) (hπ : f π ≠ 0)
    (a : ι → ℕ) (X : Matrix ι ι R) :
    cartan (f π) hπ a * GeneralLinearGroup.map f (unip (zeroSet a) X) *
      (cartan (f π) hπ a)⁻¹ =
    GeneralLinearGroup.map f (unip (zeroSet a) (fun i j => π ^ a j * X i j)) := by
  have hc : cartan (f π) hπ a * GeneralLinearGroup.map f (unip (zeroSet a) X) =
      GeneralLinearGroup.map f (unip (zeroSet a) (fun i j => π ^ a j * X i j)) *
        cartan (f π) hπ a := by
    apply Units.ext
    ext i j
    change (diagonal (fun i => ((f π) ^ a i)⁻¹) *
      (1 + rect (zeroSet a) X).map f) i j =
      ((1 + rect (zeroSet a) (fun i j => π ^ a j * X i j)).map f *
        diagonal (fun i => ((f π) ^ a i)⁻¹)) i j
    rw [diagonal_mul, mul_diagonal]
    by_cases hij : i = j
    · subst j
      simp [rect]
    · by_cases hi : a i = 0
      · by_cases hj : a j = 0
        · simp [rect, hij, hi, hj]
        · simp [rect, hij, hi, hj, map_mul, map_pow]
          field_simp
      · simp [rect, hij, hi]
  rw [hc, mul_assoc, mul_inv_cancel, mul_one]

theorem contracted_reduction (red : R →+* k) (π : R) (hπ : red π = 0)
    (a : ι → ℕ) (X : Matrix ι ι R) :
    GeneralLinearGroup.map red
      (unip (zeroSet a) (fun i j => π ^ a j * X i j)) = 1 := by
  apply Units.ext
  ext i j
  change red ((1 + rect (zeroSet a) (fun i j => π ^ a j * X i j)) i j) = (1 : Matrix ι ι k) i j
  by_cases hi : a i = 0
  · by_cases hj : a j = 0
    · simp [Matrix.one_apply, rect, hi, hj]
    · simp [Matrix.one_apply, rect, hi, hj, map_mul, map_pow, hπ, zero_pow hj]
  · simp [Matrix.one_apply, rect, hi]

/-- Surjective residue reduction constructs every radical lift and a contracted partner. -/
theorem exists_contracted_lift (f : R →+* F) (red : R →+* k)
    (hred : Function.Surjective red) (π : R) (hπ : f π ≠ 0) (hπred : red π = 0)
    (a : ι → ℕ) (X : Matrix ι ι k) :
    ∃ u v : GL ι R,
      GeneralLinearGroup.map red u = unip (zeroSet a) X ∧
      GeneralLinearGroup.map red v = 1 ∧
      cartan (f π) hπ a * GeneralLinearGroup.map f u * (cartan (f π) hπ a)⁻¹ =
        GeneralLinearGroup.map f v := by
  let Y : Matrix ι ι R := fun i j => Classical.choose (hred (X i j))
  have hY : Y.map red = X := by
    ext i j
    exact Classical.choose_spec (hred (X i j))
  refine ⟨unip (zeroSet a) Y,
    unip (zeroSet a) (fun i j => π ^ a j * Y i j), ?_,
    contracted_reduction red π hπred a Y, cartan_conjugation f π hπ a Y⟩
  rw [map_unip, hY]

theorem cartan_zero (π : F) (hπ : π ≠ 0) (a : ι → ℕ) (ha : ∀ i, a i = 0) :
    cartan π hπ a = 1 := by
  apply Units.ext
  ext i j
  simp [cartan, diagonalGL, ha]

end PaperXI.SplitRadical105
