import Mathlib.Data.Nat.Factorial.Basic
import Mathlib.Data.Nat.Choose.Basic
import Mathlib.Algebra.BigOperators.Group.Finset.Basic
import Mathlib.Algebra.BigOperators.Ring.Finset
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Ring
import Lean.Elab.Tactic.Omega

/-!
# Exact reconstruction from factorial lanes

Formal companion to `docs/demonstrations/FACTORIAL_LANES.md`, Sections 2–5.
The lane index `r` below runs from `0` to `N - 1`, so its starting factor
`j + 1 + r` runs from `j + 1` to `j + N` as in the reading edition.
The empty product is one. The reconstruction theorem also covers zero
steps, zero lanes, and arbitrary natural offsets.
-/

set_option autoImplicit false

namespace Komorebi.Reader.FactorialLanes

/-- The step factorial `(a)_(n;N)`, as an actual finite product. -/
def stepFactorial (a n N : ℕ) : ℕ :=
  ∏ k ∈ Finset.range n, (a + N * k)

/-- All `N` multiplicative lanes starting after the initial `j!`. -/
def laneProduct (N j n : ℕ) : ℕ :=
  ∏ r ∈ Finset.range N, stepFactorial (j + 1 + r) n N

theorem stepFactorial_zero (a N : ℕ) : stepFactorial a 0 N = 1 := by
  simp [stepFactorial]

theorem stepFactorial_succ (a n N : ℕ) :
    stepFactorial a (n + 1) N = stepFactorial a n N * (a + N * n) := by
  simp [stepFactorial, Finset.prod_range_succ]

/-- Appending a consecutive block of factors extends a factorial exactly. -/
theorem factorial_block (a N : ℕ) :
    Nat.factorial a * (∏ r ∈ Finset.range N, (a + 1 + r)) =
      Nat.factorial (a + N) := by
  induction N with
  | zero => simp
  | succ N ih =>
    rw [Finset.prod_range_succ, ← Nat.mul_assoc, ih]
    have h : a + (N + 1) = (a + N) + 1 := by omega
    rw [h, Nat.factorial_succ]
    have h' : a + 1 + N = a + N + 1 := by omega
    rw [h', Nat.mul_comm]

theorem laneProduct_zero (N j : ℕ) : laneProduct N j 0 = 1 := by
  simp [laneProduct, stepFactorial_zero]

/-- One more step contributes exactly the next block of `N` factors. -/
theorem laneProduct_succ (N j n : ℕ) :
    laneProduct N j (n + 1) = laneProduct N j n *
      (∏ r ∈ Finset.range N, (N * n + j + 1 + r)) := by
  simp only [laneProduct, stepFactorial_succ, Finset.prod_mul_distrib]
  congr 1
  apply Finset.prod_congr rfl
  intro r _
  omega

/-- Universal factorial reconstruction, including the empty-product case. -/
theorem factorial_lane_reconstruction (N j n : ℕ) :
    Nat.factorial j * laneProduct N j n = Nat.factorial (N * n + j) := by
  induction n with
  | zero => simp [laneProduct_zero]
  | succ n ih =>
    rw [laneProduct_succ, ← Nat.mul_assoc, ih, factorial_block]
    congr 1
    simp [Nat.mul_add, Nat.add_comm, Nat.add_left_comm]

/-- The displayed ten-lane identity is valid at every natural step. -/
theorem ten_lane_reconstruction (n : ℕ) :
    24 * laneProduct 10 4 n = Nat.factorial (10 * n + 4) := by
  exact factorial_lane_reconstruction 10 4 n

/-- The rising Pochhammer symbol over the exact rational numbers. -/
def pochhammer (a : ℚ) (n : ℕ) : ℚ :=
  ∏ k ∈ Finset.range n, (a + k)

theorem pochhammer_succ (a : ℚ) (n : ℕ) :
    pochhammer a (n + 1) = pochhammer a n * (a + n) := by
  simp [pochhammer, Finset.prod_range_succ]

/-- Moving one step-factorial lane to rational Pochhammer coordinates is exact. -/
theorem stepFactorial_scale (a n N : ℕ) (hN : 0 < N) :
    (stepFactorial a n N : ℚ) = (N : ℚ) ^ n * pochhammer ((a : ℚ) / N) n := by
  have hNq : (N : ℚ) ≠ 0 := by exact_mod_cast (Nat.ne_of_gt hN)
  induction n with
  | zero => simp [stepFactorial_zero, pochhammer]
  | succ n ih =>
    have ht : (a : ℚ) + (N : ℚ) * n = (N : ℚ) * ((a : ℚ) / N + n) := by
      field_simp
    rw [stepFactorial_succ, Nat.cast_mul, Nat.cast_add, Nat.cast_mul, ih,
        pochhammer_succ, pow_succ, ht]
    ring

/-- The lane with unit Pochhammer parameter supplies the ordinary `n!` factor. -/
theorem pochhammer_one (n : ℕ) : pochhammer 1 n = (Nat.factorial n : ℚ) := by
  induction n with
  | zero => simp [pochhammer]
  | succ n ih =>
    rw [pochhammer_succ, ih, Nat.factorial_succ]
    push_cast
    ring

/-- Rational hypergeometric coordinates reconstruct the same factorial at every
degree. This is a coefficient identity, with no analytic convergence premise. -/
theorem factorial_pochhammer (N j n : ℕ) (hN : 0 < N) :
    (Nat.factorial j : ℚ) * (N : ℚ) ^ (N * n) *
      (∏ r ∈ Finset.range N, pochhammer ((j + 1 + r : ℕ) / (N : ℚ)) n) =
      (Nat.factorial (N * n + j) : ℚ) := by
  have h := congrArg (fun t : ℕ => (t : ℚ)) (factorial_lane_reconstruction N j n)
  simp only [Nat.cast_mul, laneProduct, Finset.prod_natCast] at h
  simp_rw [stepFactorial_scale _ _ _ hN] at h
  simpa [Finset.prod_mul_distrib, ← pow_mul, Nat.mul_comm, mul_assoc] using h

/-- The factorial normalization is the reciprocal binomial coefficient. -/
theorem normalized_coefficient (m j : ℕ) :
    (Nat.factorial j : ℚ) * (Nat.factorial m : ℚ) /
      (Nat.factorial (m + j) : ℚ) = 1 / (Nat.choose (m + j) j : ℚ) := by
  have hf : (Nat.factorial (m + j) : ℚ) ≠ 0 := by
    exact_mod_cast Nat.factorial_ne_zero (m + j)
  have hc : (Nat.choose (m + j) j : ℚ) ≠ 0 := by
    exact_mod_cast (Nat.ne_of_gt (Nat.choose_pos (Nat.le_add_left j m)))
  have h : (Nat.choose (m + j) j : ℚ) * (Nat.factorial m : ℚ) *
      (Nat.factorial j : ℚ) = (Nat.factorial (m + j) : ℚ) := by
    exact_mod_cast Nat.add_choose_mul_factorial_mul_factorial m j
  apply (div_eq_div_iff hf hc).mpr
  calc
    _ = (Nat.choose (m + j) j : ℚ) * (Nat.factorial m : ℚ) *
        (Nat.factorial j : ℚ) := by ring
    _ = _ := by simpa using h

/-- The original and normalized reciprocal rows have the same coefficient
after division by the nonzero diagonal.  The degree `q` ranges over `0..m`. -/
theorem binomial_diagonal_bridge (m q j : ℕ) (hq : q ≤ m) :
    (Nat.choose (m + j) q : ℚ) / (Nat.choose (m + j) j : ℚ) =
      (Nat.choose m q : ℚ) / (Nat.choose (m - q + j) j : ℚ) := by
  have hd : (Nat.choose (m + j) j : ℚ) ≠ 0 := by
    exact_mod_cast (Nat.ne_of_gt (Nat.choose_pos (Nat.le_add_left j m)))
  have hi : (Nat.choose (m - q + j) j : ℚ) ≠ 0 := by
    exact_mod_cast (Nat.ne_of_gt (Nat.choose_pos (Nat.le_add_left j (m - q))))
  have hb := Nat.choose_mul (n := m + j) (k := m - q + j) (s := j)
    (show j ≤ m - q + j by omega)
  simp only [Nat.add_sub_cancel] at hb
  have hs : Nat.choose (m + j) (m - q + j) = Nat.choose (m + j) q :=
    Nat.choose_symm_of_eq_add (by omega)
  rw [hs, Nat.choose_symm hq] at hb
  have hbq : (Nat.choose (m + j) q : ℚ) * (Nat.choose (m - q + j) j : ℚ) =
      (Nat.choose (m + j) j : ℚ) * (Nat.choose m q : ℚ) := by
    exact_mod_cast hb
  apply (div_eq_div_iff hd hi).mpr
  simpa [mul_comm] using hbq

end Komorebi.Reader.FactorialLanes
