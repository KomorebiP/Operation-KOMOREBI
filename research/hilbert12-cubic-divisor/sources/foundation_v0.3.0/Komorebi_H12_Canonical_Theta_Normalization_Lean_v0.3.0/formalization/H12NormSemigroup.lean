/- Complete residue-ten semigroup of the norm actions on the two generator classes. -/
module
public import Mathlib.Data.Int.Basic
public section
namespace H12.NormSemigroup
abbrev Mat := ℤ × ℤ × ℤ × ℤ

def identity : Mat := (1,0,0,1)
def zero : Mat := (0,0,0,0)
def projector : Mat := (1,-6,0,0)
def multiply (a b : Mat) : Mat :=
  (a.1*b.1+a.2.1*b.2.2.1,
   a.1*b.2.1+a.2.1*b.2.2.2,
   a.2.2.1*b.1+a.2.2.2*b.2.2.1,
   a.2.2.1*b.2.1+a.2.2.2*b.2.2.2)
def residue (n : ℕ) : Fin 10 := ⟨n%10,Nat.mod_lt n (by decide)⟩
def residueProduct (a b : Fin 10) : Fin 10 := residue (a.val*b.val)
def action (a : Fin 10) : Mat :=
  if a.val%5=0 then zero else if a.val%2=0 then projector else identity
def normMatrix (n : ℕ) : Mat := action (residue n)

theorem all_residue_products : ∀ a b : Fin 10,
    action (residueProduct a b)=multiply (action a) (action b) := by decide

theorem residue_product (m n : ℕ) : residue (m*n)=residueProduct (residue m) (residue n) := by
  apply Fin.ext
  exact Nat.mul_mod m n 10

theorem norm_matrix_multiplicative (m n : ℕ) :
    normMatrix (m*n)=multiply (normMatrix m) (normMatrix n) := by
  unfold normMatrix
  rw [residue_product]
  exact all_residue_products _ _

theorem norm_one : normMatrix 1=identity := by decide
theorem norm_two : normMatrix 2=projector := by decide
theorem norm_five : normMatrix 5=zero := by decide
end H12.NormSemigroup
