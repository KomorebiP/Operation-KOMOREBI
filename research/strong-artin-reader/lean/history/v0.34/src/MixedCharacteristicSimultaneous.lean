import MixedCharacteristicFrobenius
import SimultaneousFrobeniusCriterion

/-! The inherited norm-localization class now has automatic coordinates at
mixed-characteristic matrix layers. One global correction is shared by all labels. -/
noncomputable section
namespace Komorebi.StrongArtin.MixedCharacteristic
open SquareZeroH2 SimultaneousNorm NonsemisimpleNorm
variable (p m : ℕ) [Fact (Nat.Prime p)] (hpm : p ∣ m) (hm : m ≠ 0)
variable (n : Type) [Fintype n] [DecidableEq n] {I : Type}

theorem matchingClass_zero_iff_localization
    (F : (Matrix n n (Upper p m))ˣ) (d : I → ℕ) (U : I → (Matrix n n (Upper p m))ˣ)
    (hU : ∀ i, (matrixDatum p m hpm n).q (U i) = (matrixDatum p m hpm n).q (F^d i)) :
    (matrixDatum p m hpm n).frobeniusMatchingClass F d U hU = 0 ↔
      LocalizationSolvable (residualAdjoint p m n F) d
        (fun i => kernelCoordinates p m hpm n hm
          ((matrixDatum p m hpm n).unitMismatch (U i) (F^d i) (hU i))) :=
  (linearModel p m hpm hm n F).matchingClass_zero_iff_linear_localization d U hU

theorem simultaneous_matching_iff_localization
    (F : (Matrix n n (Upper p m))ˣ) (d : I → ℕ) (U : I → (Matrix n n (Upper p m))ˣ)
    (hU : ∀ i, (matrixDatum p m hpm n).q (U i) = (matrixDatum p m hpm n).q (F^d i)) :
    (∃ F' : (Matrix n n (Upper p m))ˣ,
      (matrixDatum p m hpm n).q F' = (matrixDatum p m hpm n).q F ∧
      ∃ u : I → (Matrix n n (Upper p m))ˣ,
        (∀ i, (matrixDatum p m hpm n).q (u i) = 1) ∧
        ∀ i, u i * F'^d i * (u i)⁻¹ = U i) ↔
      LocalizationSolvable (residualAdjoint p m n F) d
        (fun i => kernelCoordinates p m hpm n hm
          ((matrixDatum p m hpm n).unitMismatch (U i) (F^d i) (hU i))) :=
  (linearModel p m hpm hm n F).simultaneous_matching_iff_linear_localization d U hU

theorem primePower_matchingClass_zero_iff_pivot
    (F : (Matrix n n (Upper p m))ˣ) (a : I → ℕ) (U : I → (Matrix n n (Upper p m))ˣ)
    (hU : ∀ i, (matrixDatum p m hpm n).q (U i) = (matrixDatum p m hpm n).q (F^(p^a i)))
    (i₀ : I) (hmin : ∀ i, p^a i₀ ≤ p^a i) :
    let e := fun i => kernelCoordinates p m hpm n hm
      ((matrixDatum p m hpm n).unitMismatch (U i) (F^(p^a i)) (hU i))
    (matrixDatum p m hpm n).frobeniusMatchingClass F (fun i => p^a i) U hU = 0 ↔
      e i₀ ∈ LinearMap.range ((residualAdjoint p m n F-1)^(p^a i₀-1)) ∧
      ∀ i, e i - ((residualAdjoint p m n F-1)^(p^a i-p^a i₀)) (e i₀) ∈
        LinearMap.range ((residualAdjoint p m n F-1)^(p^a i)) :=
  (linearModel p m hpm hm n F).primePower_matchingClass_zero_iff_pivot p a U hU i₀ hmin

/-- No missing mixed-characteristic coordinate datum remains at any r >= 1. -/
theorem primePower_layer_simultaneous_criterion
    (r : ℕ) (hr : 0 < r) (F : (Matrix n n (Upper p (p^r)))ˣ)
    (a : I → ℕ) (U : I → (Matrix n n (Upper p (p^r)))ˣ)
    (hU : ∀ i, (matrixDatum p (p^r) (dvd_pow_self p (Nat.ne_of_gt hr)) n).q (U i) =
      (matrixDatum p (p^r) (dvd_pow_self p (Nat.ne_of_gt hr)) n).q (F^(p^a i)))
    (i₀ : I) (hmin : ∀ i, p^a i₀ ≤ p^a i) :
    let D := matrixDatum p (p^r) (dvd_pow_self p (Nat.ne_of_gt hr)) n
    let S := primePowerLayerModel p n r hr F
    let e := fun i => S.coordinates (D.unitMismatch (U i) (F^(p^a i)) (hU i))
    D.frobeniusMatchingClass F (fun i => p^a i) U hU = 0 ↔
      e i₀ ∈ LinearMap.range ((S.operator-1)^(p^a i₀-1)) ∧
      ∀ i, e i - ((S.operator-1)^(p^a i-p^a i₀)) (e i₀) ∈
        LinearMap.range ((S.operator-1)^(p^a i)) :=
  (primePowerLayerModel p n r hr F).primePower_matchingClass_zero_iff_pivot p a U hU i₀ hmin

end Komorebi.StrongArtin.MixedCharacteristic
