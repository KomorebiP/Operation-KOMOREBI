import MixedCharacteristicMatrixKernel
import NonsemisimpleFrobeniusLifting

/-! Automatic FrobeniusLinearCoordinates for the actual mixed-characteristic
matrix kernel, at every positive prime-power coefficient layer. -/
noncomputable section
namespace Komorebi.StrongArtin.MixedCharacteristic
open SquareZeroH2 NonsemisimpleNorm
variable (p m : ℕ) [Fact (Nat.Prime p)] (hpm : p ∣ m) (hm : m ≠ 0)
variable (n : Type) [Fintype n] [DecidableEq n]

def linearModel (F : (Matrix n n (Upper p m))ˣ) :
    FrobeniusLinearCoordinates (matrixDatum p m hpm n) F (ZMod p) (Matrix n n (ZMod p)) where
  coordinates := kernelCoordinates p m hpm n hm
  operator := residualAdjoint p m n F
  conjugate_coordinates := conjugation_coordinates p m hpm n hm F

/-- Exact norm coordinates for arbitrary degree and arbitrary residual Frobenius. -/
theorem kernel_norm_coordinates (F : (Matrix n n (Upper p m))ˣ)
    (d : ℕ) (X : (matrixDatum p m hpm n).Kernel) :
    kernelCoordinates p m hpm n hm ((matrixDatum p m hpm n).frobeniusNorm F d X) =
      operatorNorm (residualAdjoint p m n F) d (kernelCoordinates p m hpm n hm X) :=
  (linearModel p m hpm hm n F).norm_coordinates d X

theorem prescribed_power_iff (F U : (Matrix n n (Upper p m))ˣ) (d : ℕ)
    (hU : (matrixDatum p m hpm n).q U = (matrixDatum p m hpm n).q (F^d)) :
    (∃ F' : (Matrix n n (Upper p m))ˣ,
      (matrixDatum p m hpm n).q F' = (matrixDatum p m hpm n).q F ∧ F'^d = U) ↔
    kernelCoordinates p m hpm n hm ((matrixDatum p m hpm n).unitMismatch U (F^d) hU) ∈
      LinearMap.range (operatorNorm (residualAdjoint p m n F) d) :=
  (linearModel p m hpm hm n F).prescribed_power_iff_operator_image U d hU

theorem prescribed_primePower_iff (F U : (Matrix n n (Upper p m))ˣ) (a : ℕ)
    (hU : (matrixDatum p m hpm n).q U = (matrixDatum p m hpm n).q (F^(p^a))) :
    (∃ F' : (Matrix n n (Upper p m))ˣ,
      (matrixDatum p m hpm n).q F' = (matrixDatum p m hpm n).q F ∧ F'^(p^a) = U) ↔
    kernelCoordinates p m hpm n hm ((matrixDatum p m hpm n).unitMismatch U (F^(p^a)) hU) ∈
      LinearMap.range ((residualAdjoint p m n F - 1)^(p^a-1)) :=
  (linearModel p m hpm hm n F).prescribed_primePower_iff U p a hU

/-- Multiplication by p^r identifies the residue vector space with the r-th actual layer. -/
def primePowerLayerModel (r : ℕ) (hr : 0 < r)
    (F : (Matrix n n (Upper p (p^r)))ˣ) :
    FrobeniusLinearCoordinates
      (matrixDatum p (p^r) (dvd_pow_self p (Nat.ne_of_gt hr)) n)
      F (ZMod p) (Matrix n n (ZMod p)) :=
  linearModel p (p^r) (dvd_pow_self p (Nat.ne_of_gt hr))
    (pow_ne_zero r (Nat.Prime.ne_zero (Fact.out : Nat.Prime p))) n F

theorem primePower_layer_prescribed_root_iff (r : ℕ) (hr : 0 < r)
    (F U : (Matrix n n (Upper p (p^r)))ˣ) (a : ℕ)
    (hU : (matrixDatum p (p^r) (dvd_pow_self p (Nat.ne_of_gt hr)) n).q U =
      (matrixDatum p (p^r) (dvd_pow_self p (Nat.ne_of_gt hr)) n).q (F^(p^a))) :
    (∃ F' : (Matrix n n (Upper p (p^r)))ˣ,
      (matrixDatum p (p^r) (dvd_pow_self p (Nat.ne_of_gt hr)) n).q F' =
        (matrixDatum p (p^r) (dvd_pow_self p (Nat.ne_of_gt hr)) n).q F ∧ F'^(p^a) = U) ↔
    (primePowerLayerModel p n r hr F).coordinates
      ((matrixDatum p (p^r) (dvd_pow_self p (Nat.ne_of_gt hr)) n).unitMismatch U (F^(p^a)) hU) ∈
      LinearMap.range ((residualAdjoint p (p^r) n F - 1)^(p^a-1)) :=
  (primePowerLayerModel p n r hr F).prescribed_primePower_iff U p a hU

end Komorebi.StrongArtin.MixedCharacteristic
