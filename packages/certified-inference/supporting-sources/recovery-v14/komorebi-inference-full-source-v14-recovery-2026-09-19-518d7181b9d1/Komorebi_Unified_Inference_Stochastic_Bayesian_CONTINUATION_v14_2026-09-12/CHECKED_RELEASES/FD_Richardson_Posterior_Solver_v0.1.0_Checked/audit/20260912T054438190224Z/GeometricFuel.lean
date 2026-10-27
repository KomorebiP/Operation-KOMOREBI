import Mathlib.Data.Rat.Floor
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Positivity

set_option autoImplicit false
namespace Komorebi.GainSolver

/-- A rational geometric decay has a square-root/logarithm-free rational envelope. -/
theorem geometric_bernoulli (q : ℚ) (hq : 0 ≤ q) (h1 : q < 1) (n : ℕ) :
    q^n * (1 + (n : ℚ)*(1-q)) ≤ 1 := by
  induction n with
  | zero => simp
  | succ n ih =>
    have hn : 0 ≤ (n : ℚ) := Nat.cast_nonneg n
    have hd : 0 ≤ 1-q := sub_nonneg.mpr h1.le
    have he : q * (1 + ((n : ℚ)+1)*(1-q)) ≤ 1 + (n : ℚ)*(1-q) := by
      nlinarith [mul_nonneg (show 0 ≤ (n : ℚ)+1 by positivity) (sq_nonneg (1-q))]
    calc
      q^(n+1)*(1+((n+1 : ℕ) : ℚ)*(1-q)) =
          q^n*(q*(1+((n : ℚ)+1)*(1-q))) := by rw [pow_succ, Nat.cast_add, Nat.cast_one]; ring
      _ ≤ q^n*(1+(n : ℚ)*(1-q)) :=
        mul_le_mul_of_nonneg_left he (pow_nonneg hq n)
      _ ≤ 1 := ih

/-- A conservative finite rational fuel bound. The operational solver may stop earlier. -/
def toleranceFuel (q a ε : ℚ) : ℕ := Nat.ceil (a / (ε^2 * (1-q)))

/-- At the explicit fuel, any geometric score envelope is below a positive squared tolerance. -/
theorem geometric_fuel_sufficient (q a ε : ℚ) (hq : 0 ≤ q) (h1 : q < 1)
    (ha : 0 ≤ a) (hε : 0 < ε) (n : ℕ) (hn : toleranceFuel q a ε ≤ n) :
    q^n*a ≤ ε^2 := by
  have hd : 0 < 1-q := sub_pos.mpr h1
  have hp : 0 < ε^2*(1-q) := mul_pos (sq_pos_of_pos hε) hd
  have hceil : a / (ε^2*(1-q)) ≤ (n : ℚ) :=
    (Nat.le_ceil _).trans (by exact_mod_cast hn)
  have ham : a ≤ (n : ℚ)*(ε^2*(1-q)) := (div_le_iff₀ hp).mp hceil
  have he := geometric_bernoulli q hq h1 n
  have he' := mul_le_mul_of_nonneg_left he (sq_nonneg ε)
  have hmul := mul_le_mul_of_nonneg_left ham (pow_nonneg hq n)
  have hpos : 0 ≤ q^n*ε^2 := mul_nonneg (pow_nonneg hq n) (sq_nonneg ε)
  nlinarith

/-- The finite fuel covers every rational geometric sequence, including contraction factor zero. -/
theorem exists_geometric_tolerance (q a ε : ℚ) (hq : 0 ≤ q) (h1 : q < 1)
    (ha : 0 ≤ a) (hε : 0 < ε) : ∃ n : ℕ, q^n*a ≤ ε^2 :=
  ⟨toleranceFuel q a ε, geometric_fuel_sufficient q a ε hq h1 ha hε _ le_rfl⟩
end Komorebi.GainSolver
