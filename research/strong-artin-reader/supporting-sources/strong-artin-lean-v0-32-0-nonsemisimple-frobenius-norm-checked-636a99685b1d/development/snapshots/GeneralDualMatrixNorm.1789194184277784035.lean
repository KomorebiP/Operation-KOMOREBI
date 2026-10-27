import NonsemisimpleFrobeniusLifting
import DiagonalMatrixNormModel

/-! Coordinates for arbitrary invertible Frobenius matrices over dual numbers.
The base Frobenius is not assumed diagonal or semisimple. -/
noncomputable section
namespace Komorebi.StrongArtin.SquareZeroH2.GeneralDualMatrix
open Komorebi.StrongArtin.NonsemisimpleNorm
variable (k n : Type) [Field k] [Fintype n] [DecidableEq n]

abbrev D := DiagonalModel.datum k n
abbrev Dual := DiagonalModel.Dual k

def coordinates : (D k n).Kernel ≃+ Matrix n n k where
  toFun X i j := (X.val i j).snd
  invFun x := ⟨fun i j => TrivSqZeroExt.inr (x i j), by ext i j; rfl⟩
  left_inv X := by
    apply Subtype.ext
    funext i j
    apply TrivSqZeroExt.ext
    · exact (congrFun (congrFun X.property i) j).symm
    · rfl
  right_inv x := by funext i j; rfl
  map_add' X Y := by funext i j; rfl

/-- Canonical upper-ring Frobenius above any invertible residual matrix. -/
def upperFrobenius (F : (Matrix n n k)ˣ) : (Matrix n n (Dual k))ˣ :=
  Units.map ((TrivSqZeroExt.inlHom k k).mapMatrix).toMonoidHom F

def conjugationOperator (F : (Matrix n n k)ˣ) : Module.End k (Matrix n n k) where
  toFun X := (F : Matrix n n k) * X * (↑F⁻¹ : Matrix n n k)
  map_add' X Y := by simp [Matrix.mul_add, Matrix.add_mul]
  map_smul' a X := by simp

theorem conjugation_coordinates (F : (Matrix n n k)ˣ) (X : (D k n).Kernel) :
    coordinates k n ((D k n).conjugate (upperFrobenius k n F) X) =
      conjugationOperator k n F (coordinates k n X) := by
  ext i j
  change ((((fun i j => (TrivSqZeroExt.inl ((F : Matrix n n k) i j) : Dual k)) : Matrix n n (Dual k)) * X.val *
    ((fun i j => (TrivSqZeroExt.inl ((↑F⁻¹ : Matrix n n k) i j) : Dual k)) : Matrix n n (Dual k))) i j).snd = _
  simp [Matrix.mul_apply, TrivSqZeroExt.snd_sum, TrivSqZeroExt.snd_mul,
    conjugationOperator, coordinates, mul_assoc]

def linearModel (F : (Matrix n n k)ˣ) :
    FrobeniusLinearCoordinates (D k n) (upperFrobenius k n F) k (Matrix n n k) where
  coordinates := coordinates k n
  operator := conjugationOperator k n F
  conjugate_coordinates := conjugation_coordinates k n F

/-- Every matrix Frobenius, including unipotent Frobenius, has the exact prime-power image criterion. -/
theorem matrix_prescribed_primePower_iff (F : (Matrix n n k)ˣ)
    (U : (Matrix n n (Dual k))ˣ) (p a : ℕ)
    [Fact (Nat.Prime p)] [CharP k p]
    (hU : (D k n).q U = (D k n).q ((upperFrobenius k n F)^(p^a))) :
    (∃ F' : (Matrix n n (Dual k))ˣ,
      (D k n).q F' = (D k n).q (upperFrobenius k n F) ∧ F'^(p^a) = U) ↔
    coordinates k n ((D k n).unitMismatch U ((upperFrobenius k n F)^(p^a)) hU) ∈
      LinearMap.range ((conjugationOperator k n F - 1)^(p^a-1)) :=
  (linearModel k n F).prescribed_primePower_iff U p a hU

end Komorebi.StrongArtin.SquareZeroH2.GeneralDualMatrix
