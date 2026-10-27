import Mathlib.Basic.Real.Basic
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Positivity
import Mathlib.Algebra.BigOperators.Fin
import Lean.Elab.Tactic.Omega
import Mathlib.Analysis.Complex.Basic
import Mathlib.Analysis.SpecificLimits.Normed

/-!
# Coupled special functions: recurrence, local convergence, and parameter recovery

Source: Special Functions, Appendix F (recurrence and local coefficient bounds)
and Appendix G (degree-seven parameter recovery and the exceptional surfaces).
The coordinate maps are linked to a recursively constructed infinite sequence.
All parameters in the inverse theorem are positive real numbers. The local
convergence theorem additionally assumes that every scale is at most one.

This module does not assert entire continuation, the differential-equation
identification of the sums, or the Perron growth law. The precise claim map
and restart point are in `formalization/Block01/`.
-/

set_option autoImplicit false
set_option maxHeartbeats 800000

noncomputable section

namespace Komorebi.SpecialFunctions.Coupled

/-- Two weighted observations and the product recover a positive first coordinate,
provided the coefficient discriminant is nonzero. No root-selection oracle is used. -/
theorem positive_pair_recovery {p k u v x y X Y : ℝ}
    (hk : k ≠ 0) (hx : 0 < x) (hX : 0 < X)
    (hprod : x * y = X * Y)
    (hlin : p * x + k * y = p * X + k * Y)
    (hquad : u * x ^ 2 + v * y ^ 2 = u * X ^ 2 + v * Y ^ 2)
    (hD : k ^ 2 * u - p ^ 2 * v ≠ 0) : x = X ∧ y = Y := by
  have hfirst : x = X := by
    by_contra hn
    have hfactor : (x - X) * (p * X - k * y) = 0 := by
      calc
        _ = X * ((p * x + k * y) - (p * X + k * Y)) -
            k * (x * y - X * Y) := by ring
        _ = 0 := by rw [hlin, hprod]; ring
    have hc1 : p * X = k * y :=
      sub_eq_zero.mp ((mul_eq_zero.mp hfactor).resolve_left (sub_ne_zero.mpr hn))
    have hc2 : p * x = k * Y := by linarith only [hlin, hc1]
    have hc1sq := congrArg (fun t : ℝ => t ^ 2) hc1
    have hc2sq := congrArg (fun t : ℝ => t ^ 2) hc2
    have hs : k ^ 2 * (y ^ 2 - Y ^ 2) + p ^ 2 * (x ^ 2 - X ^ 2) = 0 := by
      nlinarith only [hc1sq, hc2sq]
    have hz : (k ^ 2 * u - p ^ 2 * v) * (x ^ 2 - X ^ 2) = 0 := by
      calc
        _ = k ^ 2 * ((u * x ^ 2 + v * y ^ 2) - (u * X ^ 2 + v * Y ^ 2)) -
            v * (k ^ 2 * (y ^ 2 - Y ^ 2) + p ^ 2 * (x ^ 2 - X ^ 2)) := by ring
        _ = 0 := by rw [hquad, hs]; ring
    have hsq : x ^ 2 = X ^ 2 :=
      sub_eq_zero.mp ((mul_eq_zero.mp hz).resolve_left hD)
    have hdiff : (x - X) * (x + X) = 0 := by nlinarith only [hsq]
    exact hn (sub_eq_zero.mp ((mul_eq_zero.mp hdiff).resolve_right (ne_of_gt (add_pos hx hX))))
  refine ⟨hfirst, ?_⟩
  apply mul_left_cancel₀ hk
  rw [hfirst] at hlin
  linarith only [hlin]

structure Scales where
  q : ℝ
  r : ℝ
  a : ℝ
  b : ℝ

namespace Scales

def positive (s : Scales) : Prop := 0 < s.q ∧ 0 < s.r ∧ 0 < s.a ∧ 0 < s.b

def p (s : Scales) : ℝ := s.q * s.r

def k (s : Scales) : ℝ := s.a * s.b

def u1 (s : Scales) : ℝ := s.p / 3

def v1 (s : Scales) : ℝ := s.k / 3

def u2 (s : Scales) : ℝ := s.p / 15 * (s.p * s.q ^ 2 + s.k * s.r ^ 2)

def v2 (s : Scales) : ℝ := s.k / 15 * (s.p * s.a ^ 2 + s.k * s.b ^ 2)

def u3 (s : Scales) : ℝ := s.p / 7 *
  (s.q ^ 4 * s.u2 + s.p ^ 2 * s.u1 * s.v1 + s.r ^ 4 * s.v2)

def v3 (s : Scales) : ℝ := s.k / 7 *
  (s.a ^ 4 * s.u2 + s.k ^ 2 * s.u1 * s.v1 + s.b ^ 4 * s.v2)

def defect (s : Scales) : ℝ := s.k ^ 2 * s.u2 - s.p ^ 2 * s.v2

def sameJet (s t : Scales) : Prop :=
  s.u1 = t.u1 ∧ s.v1 = t.v1 ∧ s.u2 = t.u2 ∧ s.v2 = t.v2 ∧ s.u3 = t.u3 ∧ s.v3 = t.v3

theorem defect_factor (s : Scales) :
    s.defect = (s.p * s.k * s.a * s.r / 15) *
      (s.q ^ 2 - s.b ^ 2) * (s.q * s.b - s.a * s.r) := by
  unfold defect u2 v2 p k
  ring

theorem defect_eq_zero_iff (s : Scales) (h : s.positive) :
    s.defect = 0 ↔ s.q = s.b ∨ s.q * s.b = s.a * s.r := by
  rcases h with ⟨hq, hr, ha, hb⟩
  have hpk : s.p * s.k * s.a * s.r / 15 ≠ 0 := by
    unfold p k
    positivity
  rw [defect_factor]
  rw [mul_eq_zero, mul_eq_zero]
  simp only [hpk, false_or, sub_eq_zero]
  have heq : s.q ^ 2 = s.b ^ 2 ↔ s.q = s.b := by
    constructor
    · intro hs
      have ht : (s.q - s.b) * (s.q + s.b) = 0 := by nlinarith only [hs]
      exact sub_eq_zero.mp ((mul_eq_zero.mp ht).resolve_right (ne_of_gt (add_pos hq hb)))
    · intro hs; rw [hs]
  rw [heq]


/-- Equality of positive squares recovers the signed scale, not just its magnitude. -/
theorem positive_square_injective {x y : ℝ} (hx : 0 < x) (hy : 0 < y)
    (h : x ^ 2 = y ^ 2) : x = y := by
  have hf : (x - y) * (x + y) = 0 := by nlinarith only [h]
  exact sub_eq_zero.mp ((mul_eq_zero.mp hf).resolve_right (ne_of_gt (add_pos hx hy)))

/-- The algebraic inverse theorem corresponding to Appendix G.2.
This proves injectivity of the six-coefficient map on positive scales off D=0. -/
theorem seven_jet_injective {s t : Scales} (hs : s.positive) (ht : t.positive)
    (hD : s.defect ≠ 0) (hj : s.sameJet t) : s = t := by
  rcases hs with ⟨hq, hr, ha, hb⟩
  rcases ht with ⟨tq, tr, ta, tb⟩
  rcases hj with ⟨hu1, hv1, hu2, hv2, hu3, hv3⟩
  have hp : s.p = t.p := by unfold u1 at hu1; linarith only [hu1]
  have hk : s.k = t.k := by unfold v1 at hv1; linarith only [hv1]
  have hp0 : s.p ≠ 0 := ne_of_gt (mul_pos hq hr)
  have hk0 : s.k ≠ 0 := ne_of_gt (mul_pos ha hb)
  have hl1 : s.p * s.q ^ 2 + s.k * s.r ^ 2 = s.p * t.q ^ 2 + s.k * t.r ^ 2 := by
    have h := hu2
    simp only [u2, ← hp, ← hk] at h
    exact mul_left_cancel₀ (div_ne_zero hp0 (by norm_num)) h
  have hl2 : s.p * s.a ^ 2 + s.k * s.b ^ 2 = s.p * t.a ^ 2 + s.k * t.b ^ 2 := by
    have h := hv2
    simp only [v2, ← hp, ← hk] at h
    exact mul_left_cancel₀ (div_ne_zero hk0 (by norm_num)) h
  have hquad1 : s.u2 * (s.q ^ 2) ^ 2 + s.v2 * (s.r ^ 2) ^ 2 =
      s.u2 * (t.q ^ 2) ^ 2 + s.v2 * (t.r ^ 2) ^ 2 := by
    have h := hu3
    simp only [u3, ← hp, ← hu1, ← hv1, ← hu2, ← hv2] at h
    have hc := mul_left_cancel₀ (div_ne_zero hp0 (by norm_num : (7 : ℝ) ≠ 0)) h
    nlinarith only [hc]
  have hquad2 : s.u2 * (s.a ^ 2) ^ 2 + s.v2 * (s.b ^ 2) ^ 2 =
      s.u2 * (t.a ^ 2) ^ 2 + s.v2 * (t.b ^ 2) ^ 2 := by
    have h := hv3
    simp only [v3, ← hk, ← hu1, ← hv1, ← hu2, ← hv2] at h
    have hc := mul_left_cancel₀ (div_ne_zero hk0 (by norm_num : (7 : ℝ) ≠ 0)) h
    nlinarith only [hc]
  have hprod1 : s.q ^ 2 * s.r ^ 2 = t.q ^ 2 * t.r ^ 2 := by
    have h := congrArg (fun x : ℝ => x ^ 2) hp
    unfold p at h
    nlinarith only [h]
  have hprod2 : s.a ^ 2 * s.b ^ 2 = t.a ^ 2 * t.b ^ 2 := by
    have h := congrArg (fun x : ℝ => x ^ 2) hk
    unfold k at h
    nlinarith only [h]
  have hrow1 := positive_pair_recovery hk0 (sq_pos_of_pos hq) (sq_pos_of_pos tq)
    hprod1 hl1 hquad1 hD
  have hrow2 := positive_pair_recovery hk0 (sq_pos_of_pos ha) (sq_pos_of_pos ta)
    hprod2 hl2 hquad2 hD
  have hqeq := positive_square_injective hq tq hrow1.1
  have hreq := positive_square_injective hr tr hrow1.2
  have haeq := positive_square_injective ha ta hrow2.1
  have hbeq := positive_square_injective hb tb hrow2.2
  cases s
  cases t
  simp_all


/-- The next odd coefficient: n indexes the previously available coefficients. -/
def nextCoefficient (x y : ℝ) (f : ℕ → ℝ × ℝ) (n : ℕ) : ℝ :=
  (∑ i : Fin (n + 1), x ^ (2 * i.val + 1) * y ^ (2 * (n - i.val) + 1) *
    (f i.val).1 * (f (n - i.val)).2) / (2 * (n : ℝ) + 3)

/-- The simultaneous, uniquely determined infinite coefficient sequence.
The n-th pair multiplies z^(2*n+1). No convergence is included in this definition. -/
def coefficients (s : Scales) : ℕ → ℝ × ℝ
  | 0 => (1, 1)
  | n + 1 =>
    ((∑ i : Fin (n + 1), s.q ^ (2 * i.val + 1) * s.r ^ (2 * (n - i.val) + 1) *
      (coefficients s i.val).1 * (coefficients s (n - i.val)).2) / (2 * (n : ℝ) + 3),
     (∑ i : Fin (n + 1), s.a ^ (2 * i.val + 1) * s.b ^ (2 * (n - i.val) + 1) *
      (coefficients s i.val).1 * (coefficients s (n - i.val)).2) / (2 * (n : ℝ) + 3))
termination_by n => n
decreasing_by all_goals omega

/-- Recurrence contract. It does not assume a particular formula for later coefficients. -/
def IsCoefficientSolution (s : Scales) (f : ℕ → ℝ × ℝ) : Prop :=
  f 0 = (1, 1) ∧ ∀ n, f (n + 1) =
    (nextCoefficient s.q s.r f n, nextCoefficient s.a s.b f n)

theorem coefficients_solution (s : Scales) : s.IsCoefficientSolution s.coefficients := by
  constructor
  · rw [coefficients]
  · intro n
    rw [coefficients]
    rfl

theorem nextCoefficient_congr {x y : ℝ} {f g : ℕ → ℝ × ℝ} {n : ℕ}
    (h : ∀ j, j ≤ n → f j = g j) : nextCoefficient x y f n = nextCoefficient x y g n := by
  unfold nextCoefficient
  congr 1
  apply Finset.sum_congr rfl
  intro i _
  rw [h i.val (by omega), h (n - i.val) (Nat.sub_le _ _)]

theorem coefficient_solution_unique {s : Scales} {f g : ℕ → ℝ × ℝ}
    (hf : s.IsCoefficientSolution f) (hg : s.IsCoefficientSolution g) : f = g := by
  funext n
  induction n using Nat.strong_induction_on with
  | h n ih =>
    cases n with
    | zero => exact hf.1.trans hg.1.symm
    | succ n =>
      rw [hf.2, hg.2]
      have hl : ∀ j, j ≤ n → f j = g j := fun j hj => ih j (by omega)
      rw [nextCoefficient_congr hl, nextCoefficient_congr hl]

theorem coefficient_solution_exists_unique (s : Scales) : ∃! f, s.IsCoefficientSolution f := by
  refine ⟨s.coefficients, s.coefficients_solution, ?_⟩
  intro g hg
  exact coefficient_solution_unique hg s.coefficients_solution

theorem coefficients_zero (s : Scales) : s.coefficients 0 = (1, 1) := by rw [coefficients]

theorem coefficients_one (s : Scales) : s.coefficients 1 = (s.u1, s.v1) := by
  simp [coefficients, u1, v1, p, k]

theorem coefficients_two (s : Scales) : s.coefficients 2 = (s.u2, s.v2) := by
  rw [s.coefficients_solution.2]
  simp [nextCoefficient, Fin.sum_univ_succ, coefficients_zero, coefficients_one,
    u1, v1, u2, v2, p, k]
  constructor <;> ring

theorem coefficients_three (s : Scales) : s.coefficients 3 = (s.u3, s.v3) := by
  rw [s.coefficients_solution.2]
  simp [nextCoefficient, Fin.sum_univ_succ, coefficients_zero, coefficients_one, coefficients_two,
    u1, v1, u2, v2, u3, v3, p, k]
  constructor <;> ring

theorem nextCoefficient_positive {x y : ℝ} {f : ℕ → ℝ × ℝ} {n : ℕ}
    (hx : 0 < x) (hy : 0 < y)
    (hf : ∀ j, j ≤ n → 0 < (f j).1 ∧ 0 < (f j).2) :
    0 < nextCoefficient x y f n := by
  unfold nextCoefficient
  apply div_pos
  · apply Finset.sum_pos
    · intro i _
      have hfi := (hf i.val (by omega)).1
      have hfj := (hf (n - i.val) (Nat.sub_le _ _)).2
      positivity
    · exact Finset.univ_nonempty
  · positivity

theorem coefficients_positive (s : Scales) (hs : s.positive) (n : ℕ) :
    0 < (s.coefficients n).1 ∧ 0 < (s.coefficients n).2 := by
  induction n using Nat.strong_induction_on with
  | h n ih =>
    cases n with
    | zero => rw [coefficients_zero]; norm_num
    | succ n =>
      rw [s.coefficients_solution.2]
      have hl : ∀ j, j ≤ n → 0 < (s.coefficients j).1 ∧ 0 < (s.coefficients j).2 :=
        fun j hj => ih j (by omega)
      exact ⟨nextCoefficient_positive hs.1 hs.2.1 hl,
        nextCoefficient_positive hs.2.2.1 hs.2.2.2 hl⟩


/-- Uniform coefficient bound for one recurrence step. -/
theorem nextCoefficient_le_geometric {x y : ℝ} {f : ℕ → ℝ × ℝ} {n : ℕ}
    (hx : 0 < x) (hy : 0 < y) (hx1 : x ≤ 1) (hy1 : y ≤ 1)
    (hf : ∀ j, j ≤ n → 0 ≤ (f j).1 ∧ (f j).1 ≤ (1 / 2 : ℝ) ^ j ∧
      0 ≤ (f j).2 ∧ (f j).2 ≤ (1 / 2 : ℝ) ^ j) :
    nextCoefficient x y f n ≤ (1 / 2 : ℝ) ^ (n + 1) := by
  have hterm (i : Fin (n + 1)) :
      x ^ (2 * i.val + 1) * y ^ (2 * (n - i.val) + 1) *
        (f i.val).1 * (f (n - i.val)).2 ≤ (1 / 2 : ℝ) ^ n := by
    have hi : i.val ≤ n := by omega
    have hj : n - i.val ≤ n := Nat.sub_le _ _
    have hp : x ^ (2 * i.val + 1) * y ^ (2 * (n - i.val) + 1) ≤ 1 := by
      calc
        _ ≤ (1 : ℝ) * 1 := mul_le_mul (pow_le_one₀ hx.le hx1)
          (pow_le_one₀ hy.le hy1) (by positivity) (by norm_num)
        _ = 1 := by norm_num
    have hc : (f i.val).1 * (f (n - i.val)).2 ≤
        (1 / 2 : ℝ) ^ i.val * (1 / 2 : ℝ) ^ (n - i.val) :=
      mul_le_mul (hf i.val hi).2.1 (hf (n - i.val) hj).2.2.2
        (hf (n - i.val) hj).2.2.1 (by positivity)
    calc
      _ = (x ^ (2 * i.val + 1) * y ^ (2 * (n - i.val) + 1)) *
          ((f i.val).1 * (f (n - i.val)).2) := by ring
      _ ≤ 1 * ((1 / 2 : ℝ) ^ i.val * (1 / 2 : ℝ) ^ (n - i.val)) :=
        mul_le_mul hp hc (mul_nonneg (hf i.val hi).1 (hf (n - i.val) hj).2.2.1)
          (by norm_num)
      _ = (1 / 2 : ℝ) ^ n := by rw [one_mul, ← pow_add, Nat.add_sub_of_le hi]
  have hsum : (∑ i : Fin (n + 1), x ^ (2 * i.val + 1) * y ^ (2 * (n - i.val) + 1) *
      (f i.val).1 * (f (n - i.val)).2) ≤ ((n : ℝ) + 1) * (1 / 2 : ℝ) ^ n := by
    calc
      _ ≤ ∑ _i : Fin (n + 1), (1 / 2 : ℝ) ^ n :=
        Finset.sum_le_sum (fun i _ => hterm i)
      _ = ((n : ℝ) + 1) * (1 / 2 : ℝ) ^ n := by simp
  unfold nextCoefficient
  apply (div_le_iff₀ (by positivity : (0 : ℝ) < 2 * (n : ℝ) + 3)).2
  rw [pow_succ]
  have hnonneg : 0 ≤ (1 / 2 : ℝ) ^ n := by positivity
  nlinarith only [hsum, hnonneg]

/-- Both coefficient sequences have the common geometric majorant 2^(-n).
This is a coefficient estimate, not an entire-function assertion. -/
theorem coefficients_le_geometric (s : Scales) (hs : s.positive)
    (hsmall : s.q ≤ 1 ∧ s.r ≤ 1 ∧ s.a ≤ 1 ∧ s.b ≤ 1) (n : ℕ) :
    (s.coefficients n).1 ≤ (1 / 2 : ℝ) ^ n ∧
      (s.coefficients n).2 ≤ (1 / 2 : ℝ) ^ n := by
  induction n using Nat.strong_induction_on with
  | h n ih =>
    cases n with
    | zero => rw [coefficients_zero]; norm_num
    | succ n =>
      have hl : ∀ j, j ≤ n → 0 ≤ (s.coefficients j).1 ∧
          (s.coefficients j).1 ≤ (1 / 2 : ℝ) ^ j ∧
          0 ≤ (s.coefficients j).2 ∧ (s.coefficients j).2 ≤ (1 / 2 : ℝ) ^ j := by
        intro j hj
        exact ⟨(s.coefficients_positive hs j).1.le, (ih j (by omega)).1,
          (s.coefficients_positive hs j).2.le, (ih j (by omega)).2⟩
      rw [s.coefficients_solution.2]
      exact ⟨nextCoefficient_le_geometric hs.1 hs.2.1 hsmall.1 hsmall.2.1 hl,
        nextCoefficient_le_geometric hs.2.2.1 hs.2.2.2 hsmall.2.2.1 hsmall.2.2.2 hl⟩


/-- The geometric bound controls the actual complex odd-series terms. -/
theorem odd_series_norm_bound {c : ℕ → ℝ}
    (hc : ∀ n, 0 ≤ c n ∧ c n ≤ (1 / 2 : ℝ) ^ n) (z : ℂ) (n : ℕ) :
    ‖(c n : ℂ) * z ^ (2 * n + 1)‖ ≤ ‖z‖ * (‖z‖ ^ 2 / 2) ^ n := by
  rw [norm_mul, Complex.norm_of_nonneg (hc n).1, norm_pow]
  calc
    _ ≤ (1 / 2 : ℝ) ^ n * ‖z‖ ^ (2 * n + 1) :=
      mul_le_mul_of_nonneg_right (hc n).2 (by positivity)
    _ = ‖z‖ * (‖z‖ ^ 2 / 2) ^ n := by
      simp only [pow_add, pow_one, pow_mul, div_pow, one_pow]
      ring

/-- Absolute convergence on the open disk norm(z)^2 < 2. -/
theorem odd_series_norm_summable {c : ℕ → ℝ}
    (hc : ∀ n, 0 ≤ c n ∧ c n ≤ (1 / 2 : ℝ) ^ n)
    (z : ℂ) (hz : ‖z‖ ^ 2 < 2) :
    Summable (fun n => ‖(c n : ℂ) * z ^ (2 * n + 1)‖) := by
  have hr0 : 0 ≤ ‖z‖ ^ 2 / 2 := by positivity
  have hr1 : ‖z‖ ^ 2 / 2 < 1 := by linarith only [hz]
  have hg := (summable_geometric_of_lt_one hr0 hr1).mul_left ‖z‖
  exact Summable.of_nonneg_of_le (fun n => norm_nonneg _) (odd_series_norm_bound hc z) hg

theorem odd_series_summable {c : ℕ → ℝ}
    (hc : ∀ n, 0 ≤ c n ∧ c n ≤ (1 / 2 : ℝ) ^ n)
    (z : ℂ) (hz : ‖z‖ ^ 2 < 2) :
    Summable (fun n => (c n : ℂ) * z ^ (2 * n + 1)) :=
  (odd_series_norm_summable hc z hz).of_norm

/-- Both recurrence series converge absolutely on the stated disk.
This does not yet assert differentiability or continuation to the entire plane. -/
theorem coefficient_series_absolutely_convergent (s : Scales) (hs : s.positive)
    (hsmall : s.q ≤ 1 ∧ s.r ≤ 1 ∧ s.a ≤ 1 ∧ s.b ≤ 1)
    (z : ℂ) (hz : ‖z‖ ^ 2 < 2) :
    Summable (fun n => ‖((s.coefficients n).1 : ℂ) * z ^ (2 * n + 1)‖) ∧
    Summable (fun n => ‖((s.coefficients n).2 : ℂ) * z ^ (2 * n + 1)‖) := by
  constructor
  · apply odd_series_norm_summable _ z hz
    intro n
    exact ⟨(s.coefficients_positive hs n).1.le, (s.coefficients_le_geometric hs hsmall n).1⟩
  · apply odd_series_norm_summable _ z hz
    intro n
    exact ⟨(s.coefficients_positive hs n).2.le, (s.coefficients_le_geometric hs hsmall n).2⟩


/-- An explicit certified truncation bound, beginning at coefficient index N. -/
theorem odd_series_tail_bound {c : ℕ → ℝ}
    (hc : ∀ n, 0 ≤ c n ∧ c n ≤ (1 / 2 : ℝ) ^ n)
    (z : ℂ) (hz : ‖z‖ ^ 2 < 2) (N : ℕ) :
    ‖∑' n, (c (n + N) : ℂ) * z ^ (2 * (n + N) + 1)‖ ≤
      ‖z‖ * (‖z‖ ^ 2 / 2) ^ N / (1 - ‖z‖ ^ 2 / 2) := by
  let r : ℝ := ‖z‖ ^ 2 / 2
  have hr0 : 0 ≤ r := by dsimp [r]; positivity
  have hr1 : r < 1 := by dsimp [r]; linarith only [hz]
  have hg : HasSum (fun n : ℕ => (‖z‖ * r ^ N) * r ^ n)
      (‖z‖ * r ^ N / (1 - r)) := by
    simpa only [div_eq_mul_inv] using
      (hasSum_geometric_of_lt_one hr0 hr1).mul_left (‖z‖ * r ^ N)
  have hbound (n : ℕ) : ‖(c (n + N) : ℂ) * z ^ (2 * (n + N) + 1)‖ ≤
      (‖z‖ * r ^ N) * r ^ n := by
    calc
      _ ≤ ‖z‖ * r ^ (n + N) := odd_series_norm_bound hc z (n + N)
      _ = _ := by rw [pow_add]; ring
  have hf := Summable.of_norm_bounded hg.summable hbound
  exact hf.hasSum.norm_le_of_bounded hg hbound

/-- The explicit six-coordinate map is the actual jet of the infinite recurrence. -/
theorem sameJet_of_coefficients_eq {s t : Scales}
    (h : ∀ n, 1 ≤ n → n ≤ 3 → s.coefficients n = t.coefficients n) : s.sameJet t := by
  have h1 := h 1 (by omega) (by omega)
  have h2 := h 2 (by omega) (by omega)
  have h3 := h 3 (by omega) (by omega)
  rw [coefficients_one, coefficients_one, Prod.mk.injEq] at h1
  rw [coefficients_two, coefficients_two, Prod.mk.injEq] at h2
  rw [coefficients_three, coefficients_three, Prod.mk.injEq] at h3
  exact ⟨h1.1, h1.2, h2.1, h2.2, h3.1, h3.2⟩

/-- Parameter recovery directly from finite observations of the recurrence. -/
theorem parameters_of_jet_through_degree_seven {s t : Scales} (hs : s.positive) (ht : t.positive)
    (hD : s.defect ≠ 0)
    (h : ∀ n, 1 ≤ n → n ≤ 3 → s.coefficients n = t.coefficients n) : s = t :=
  seven_jet_injective hs ht hD (sameJet_of_coefficients_eq h)

/-- Generic injectivity of the full formal coefficient sequence. -/
theorem parameters_of_formal_pair_eq {s t : Scales} (hs : s.positive) (ht : t.positive)
    (hD : s.defect ≠ 0) (h : s.coefficients = t.coefficients) : s = t := by
  apply parameters_of_jet_through_degree_seven hs ht hD
  intro n _ _
  exact congrFun h n


/-- The nondegenerate rational example used in Appendix G. -/
def workedScales : Scales := ⟨1/5, 2/5, 3/5, 7/10⟩

theorem workedScales_positive : workedScales.positive := by
  norm_num [workedScales, positive]

theorem workedScales_defect : workedScales.defect = 189 / 7812500 := by
  norm_num [workedScales, defect, u2, v2, p, k]

theorem workedScales_recoverable {s : Scales} (hs : s.positive)
    (h : workedScales.sameJet s) : s = workedScales := by
  have hD : workedScales.defect ≠ 0 := by rw [workedScales_defect]; norm_num
  exact (seven_jet_injective workedScales_positive hs hD h).symm

/-- A genuine boundary collision demonstrates why the nonzero-defect guard matters. -/
def boundaryLeft : Scales := ⟨1/4, 1/2, 1/4, 1/2⟩

def boundaryRight : Scales := ⟨1/2, 1/4, 1/2, 1/4⟩

theorem boundary_collision : boundaryLeft.positive ∧ boundaryRight.positive ∧
    boundaryLeft.defect = 0 ∧ boundaryLeft.sameJet boundaryRight ∧ boundaryLeft ≠ boundaryRight := by
  constructor
  · norm_num [boundaryLeft, positive]
  constructor
  · norm_num [boundaryRight, positive]
  constructor
  · norm_num [boundaryLeft, defect, u2, v2, p, k]
  constructor
  · norm_num [sameJet, boundaryLeft, boundaryRight, u1, v1, u2, v2, u3, v3, p, k]
  · intro h
    have hq := congrArg Scales.q h
    norm_num [boundaryLeft, boundaryRight] at hq

end Scales
end Komorebi.SpecialFunctions.Coupled
