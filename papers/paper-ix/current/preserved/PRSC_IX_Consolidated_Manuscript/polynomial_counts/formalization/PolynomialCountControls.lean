module
public import PolynomialLiftCounts
public import Mathlib.Tactic

@[expose] public section
noncomputable section
set_option autoImplicit false
namespace Komorebi.PolynomialCountControls
open MvPolynomial PolynomialDigitBridge NativeAffine PolynomialObstruction

def linearSystem : Fin 1 → MvPolynomial (Fin 1) ℤ := fun _ => X 0
def zeroSystem : Fin 1 → MvPolynomial (Fin 1) ℤ := fun _ => 0
def squareSystem : Fin 1 → MvPolynomial (Fin 1) ℤ := fun _ => X 0 ^ 2
def squareMinusTwo : Fin 1 → MvPolynomial (Fin 1) ℤ := fun _ => X 0 ^ 2 - C 2

/-- A nonsingular linear equation has exactly one correction digit. -/
theorem linear_digit_count (q : ℕ) :
    Nat.card (DigitSolutions q linearSystem (fun _ => 0) (fun _ => 0)) = 1 := by
  apply Nat.card_eq_one_iff_exists.mpr
  refine ⟨⟨0, by ext i; simp [reduction, digitJacobian, linearSystem]⟩, ?_⟩
  intro t
  apply Subtype.ext
  funext i
  have h := congrFun t.property 0
  simpa [reduction, digitJacobian, linearSystem, Fin.eq_zero i] using h

/-- A zero equation imposes no restriction on the single correction digit. -/
theorem zero_digit_count (q : ℕ) (hq : 0 < q) :
    Nat.card (DigitSolutions q zeroSystem (fun _ => 0) (fun _ => 0)) = q := by
  let : NeZero q := ⟨Nat.ne_of_gt hq⟩
  have h := Nat.card_congr (show DigitSolutions q zeroSystem (fun _ => 0) (fun _ => 0) ≃
      (Fin 1 → ZMod q) from {
    toFun := Subtype.val
    invFun t := ⟨t, by ext i; simp [reduction, digitJacobian, zeroSystem]⟩
    left_inv _ := rfl
    right_inv _ := rfl })
  simpa [Nat.card_fun, Nat.card_eq_fintype_card] using h

/-- X²−2 at the even lower root has no correction digit modulo two. -/
theorem obstructed_square_digit_count :
    Nat.card (DigitSolutions 2 squareMinusTwo (fun _ => 0) (fun _ => -1)) = 0 := by
  apply Nat.card_eq_zero.mpr
  left
  refine ⟨fun t => ?_⟩
  have h := congrFun t.property 0
  change ((-1 : ℤ) : ZMod 2) +
    (∑ k : Fin 1, (eval (fun _ : Fin 1 => (0 : ℤ))
      (pderiv k (squareMinusTwo 0)) : ZMod 2) * t.val k) = 0 at h
  simp only [squareMinusTwo, map_sub, pderiv_pow, pderiv_C] at h
  norm_num at h

/-- X² has the same zero Jacobian but both correction digits lift. -/
theorem singular_square_digit_count :
    Nat.card (DigitSolutions 2 squareSystem (fun _ => 0) (fun _ => 0)) = 2 := by
  have h := Nat.card_congr (show DigitSolutions 2 squareSystem (fun _ => 0) (fun _ => 0) ≃
      (Fin 1 → ZMod 2) from {
    toFun := Subtype.val
    invFun t := ⟨t, by ext i; simp [reduction, digitJacobian, squareSystem]⟩
    left_inv _ := rfl
    right_inv _ := rfl })
  simpa [Nat.card_fun, Nat.card_eq_fintype_card] using h

/-- The linear count applies to actual next-level polynomial residue classes. -/
theorem linear_lift_count (q L : ℕ) (hq : 0 < q) (hL : 1 ≤ L) :
    Nat.card (PolynomialLiftCounts.ActualLifts q L linearSystem (fun _ => 0)) = 1 := by
  rw [← Nat.card_congr (PolynomialLiftCounts.digitEquivLifts q L hq hL
    linearSystem (fun _ => 0) (fun _ => 0) (by ext i; simp [evalSystem, linearSystem]))]
  exact linear_digit_count q

/-- A zero equation leaves q actual next-level residue classes over the root. -/
theorem zero_lift_count (q L : ℕ) (hq : 0 < q) (hL : 1 ≤ L) :
    Nat.card (PolynomialLiftCounts.ActualLifts q L zeroSystem (fun _ => 0)) = q := by
  rw [← Nat.card_congr (PolynomialLiftCounts.digitEquivLifts q L hq hL
    zeroSystem (fun _ => 0) (fun _ => 0) (by ext i; simp [evalSystem, zeroSystem]))]
  exact zero_digit_count q hq

/-- An even root of X²−2 modulo two has zero actual lifts modulo four. -/
theorem obstructed_square_lift_count :
    Nat.card (PolynomialLiftCounts.ActualLifts 2 1 squareMinusTwo (fun _ => 0)) = 0 := by
  rw [← Nat.card_congr (PolynomialLiftCounts.digitEquivLifts 2 1 (by decide) (by decide)
    squareMinusTwo (fun _ => 0) (fun _ => -1)
    (by
      ext i
      simp only [evalSystem, squareMinusTwo, map_sub, map_pow, eval_X, eval_C,
        Pi.smul_apply, smul_eq_mul]
      norm_num))]
  exact obstructed_square_digit_count

/-- A singular even root of X² modulo two has exactly two lifts modulo four. -/
theorem singular_square_lift_count :
    Nat.card (PolynomialLiftCounts.ActualLifts 2 1 squareSystem (fun _ => 0)) = 2 := by
  rw [← Nat.card_congr (PolynomialLiftCounts.digitEquivLifts 2 1 (by decide) (by decide)
    squareSystem (fun _ => 0) (fun _ => 0)
    (by ext i; norm_num [evalSystem, squareSystem]))]
  exact singular_square_digit_count

/-- There are four unrestricted roots of the zero equation modulo four.
The prescribed even lower residue retains only two of them. -/
theorem unrestricted_zero_root_count :
    Nat.card {y : Fin 1 → ZMod 4 //
      ∀ i, (4 : ℤ) ∣ eval (fun k => ((y k).val : ℤ)) (zeroSystem i)} = 4 := by
  have h := Nat.card_congr (show {y : Fin 1 → ZMod 4 //
      ∀ i, (4 : ℤ) ∣ eval (fun k => ((y k).val : ℤ)) (zeroSystem i)} ≃
      (Fin 1 → ZMod 4) from {
    toFun := Subtype.val
    invFun t := ⟨t, by intro i; simp [zeroSystem]⟩
    left_inv _ := rfl
    right_inv _ := rfl })
  simpa [Nat.card_fun, Nat.card_eq_fintype_card] using h

end Komorebi.PolynomialCountControls
