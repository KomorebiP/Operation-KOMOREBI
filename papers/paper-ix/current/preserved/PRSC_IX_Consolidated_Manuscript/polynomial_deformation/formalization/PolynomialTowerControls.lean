module
public import PolynomialIntegerTower
public import PadicTowerLimit
public import Mathlib.Tactic

@[expose] public section
noncomputable section
set_option autoImplicit false
namespace Komorebi.PolynomialTowerControls
open MvPolynomial PolynomialObstruction PolynomialDigitBridge

def squareMinusFive : Fin 1 → MvPolynomial (Fin 1) ℤ := fun _ => X 0 ^ 2 - C 5

/-- The singular lower root one already lifts from modulus two to modulus four. -/
theorem square_minus_five_lower_steps :
    (2 : ℤ) ∣ eval (fun _ : Fin 1 => 1) (squareMinusFive 0) ∧
    (4 : ℤ) ∣ eval (fun _ : Fin 1 => 1) (squareMinusFive 0) := by
  norm_num [squareMinusFive]

/-- The very next level is impossible, even without a prescribed lower residue. -/
theorem square_minus_five_no_mod_eight (x : ℤ) : ¬ (8 : ℤ) ∣ x ^ 2 - 5 := by
  intro h
  have hz : ((x : ZMod 8) ^ 2 - 5) = 0 := by
    simpa using (ZMod.intCast_zmod_eq_zero_iff_dvd (x ^ 2 - 5) 8).mpr h
  have hn : ∀ t : ZMod 8, t ^ 2 - 5 ≠ 0 := by decide
  exact hn (x : ZMod 8) hz

/-- One successful singular lift does not furnish roots through all levels. -/
theorem square_minus_five_no_tower :
    ¬ ∃ z : ℕ → Fin 1 → ℤ,
      ∀ n i, (2 : ℤ) ^ (1+n) ∣ eval (z n) (squareMinusFive i) := by
  rintro ⟨z, hz⟩
  have h := hz 2 0
  norm_num [squareMinusFive] at h
  exact square_minus_five_no_mod_eight (z 2 0) h

def projectionSystem : Fin 1 → MvPolynomial (Fin 2) ℤ := fun _ => X 0

/-- A rectangular Jacobian can be surjective while leaving a free coordinate. -/
theorem projection_jacobian_surjective (q : ℕ) (x : Fin 2 → ℤ) :
    Function.Surjective (digitJacobian q projectionSystem x) := by
  intro y
  refine ⟨fun _ => y 0, ?_⟩
  ext i
  simp [digitJacobian, projectionSystem, Fin.sum_univ_two, Fin.eq_zero i]

/-- Surjectivity does not imply uniqueness: both roots have the same residue modulo two. -/
theorem projection_two_padic_roots :
    ∃ a b : Fin 2 → ℤ_[2], a ≠ b ∧
      (∀ i, eval₂ (Int.castRingHom ℤ_[2]) a (projectionSystem i) = 0) ∧
      (∀ i, eval₂ (Int.castRingHom ℤ_[2]) b (projectionSystem i) = 0) ∧
      (∀ i, (2 : ℤ_[2]) ∣ b i - a i) := by
  let a : Fin 2 → ℤ_[2] := fun _ => 0
  let b : Fin 2 → ℤ_[2] := ![0, 2]
  refine ⟨a, b, ?_, ?_, ?_, ?_⟩
  · intro h
    have h1 := congrFun h 1
    norm_num [a, b] at h1
  · intro i
    simp [a, projectionSystem]
  · intro i
    simp [b, projectionSystem]
  · intro i
    fin_cases i <;> simp [a, b]

def linearMinusTwo : Fin 1 → MvPolynomial (Fin 1) ℤ := fun _ => X 0 - C 2

/-- A nonsingular lower root can require changing the very next binary digit. -/
theorem linear_shift_nonsingular_lower_root :
    (2 : ℤ) ∣ eval (fun _ : Fin 1 => 0) (linearMinusTwo 0) ∧
    Function.Surjective (digitJacobian 2 linearMinusTwo (fun _ => 0)) ∧
    eval (fun _ : Fin 1 => 2) (linearMinusTwo 0) = 0 := by
  refine ⟨?_, ?_, ?_⟩
  · change (2 : ℤ) ∣ eval (fun _ : Fin 1 => 0) (X 0 - C 2)
    simp only [map_sub, eval_X, eval_C]
    norm_num
  · intro y
    refine ⟨y, ?_⟩
    ext i
    change (∑ k : Fin 1, (eval (fun _ : Fin 1 => (0 : ℤ))
      (pderiv k (X 0 - C 2)) : ZMod 2) * y k) = y i
    simp only [map_sub, pderiv_C, sub_zero,
      Fin.sum_univ_one, pderiv_X_self, map_one, Int.cast_one, one_mul, Fin.eq_zero i]
  · change eval (fun _ : Fin 1 => (2 : ℤ)) (X 0 - C 2) = 0
    simp only [map_sub, eval_X, eval_C, sub_self]

/-- The resulting exact integer root need not retain one extra digit of the initial point. -/
theorem linear_shift_no_extra_precision :
    ¬ ∃ y : Fin 1 → ℤ,
      eval y (linearMinusTwo 0) = 0 ∧ (4 : ℤ) ∣ y 0 := by
  rintro ⟨y, hy, hd⟩
  have h2 : y 0 = 2 := by
    change eval y (X 0 - C 2) = 0 at hy
    simpa only [map_sub, eval_X, eval_C, sub_eq_zero] using hy
  rw [h2] at hd
  norm_num at hd

end Komorebi.PolynomialTowerControls
