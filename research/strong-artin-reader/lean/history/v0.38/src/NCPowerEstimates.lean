import Mathlib.Analysis.Normed.Group.Ultra
import Mathlib.Tactic

namespace Komorebi.StrongArtin.MatrixHensel

section Algebra
variable {E : Type*} [Ring E]

/-- The full noncommutative power derivative, in a recursive order-preserving form. -/
def tangent (A : E) : ℕ → E → E
  | 0, _ => 0
  | d + 1, h => tangent A d h * A + A ^ d * h

theorem tangent_zero (A : E) (d : ℕ) : tangent A d 0 = 0 := by
  induction d with
  | zero => rfl
  | succ d ih => simp [tangent, ih]

theorem tangent_add (A : E) (d : ℕ) (h k : E) :
    tangent A d (h + k) = tangent A d h + tangent A d k := by
  induction d with
  | zero => simp [tangent]
  | succ d ih => simp only [tangent, ih]; noncomm_ring

def tangentHom (A : E) (d : ℕ) : E →+ E where
  toFun := tangent A d
  map_zero' := tangent_zero A d
  map_add' := tangent_add A d

theorem tangent_sub (A : E) (d : ℕ) (h k : E) :
    tangent A d (h - k) = tangent A d h - tangent A d k :=
  (tangentHom A d).map_sub h k

def remainder (A : E) (d : ℕ) (h : E) : E := (A + h) ^ d - A ^ d - tangent A d h

theorem remainder_zero (A : E) (d : ℕ) : remainder A d 0 = 0 := by
  simp [remainder, tangent_zero]

theorem remainder_succ (A : E) (d : ℕ) (h : E) :
    remainder A (d + 1) h = remainder A d h * (A + h) + tangent A d h * h := by
  simp only [remainder, tangent, pow_succ]
  noncomm_ring

theorem remainder_difference_succ (A : E) (d : ℕ) (h k : E) :
    remainder A (d + 1) h - remainder A (d + 1) k =
      (remainder A d h - remainder A d k) * (A + h) + remainder A d k * (h - k) +
      (tangent A d h - tangent A d k) * h + tangent A d k * (h - k) := by
  rw [remainder_succ, remainder_succ]
  noncomm_ring

theorem tangent_eq_sum (A : E) (d : ℕ) (h : E) :
    tangent A d h = ∑ i ∈ Finset.range d, A ^ i * h * A ^ (d - 1 - i) := by
  induction d with
  | zero => simp [tangent]
  | succ d ih =>
    rw [tangent, ih, Finset.sum_mul, Finset.sum_range_succ]
    congr 1
    · apply Finset.sum_congr rfl
      intro i hi
      have hi' := Finset.mem_range.mp hi
      have he : d + 1 - 1 - i = (d - 1 - i) + 1 := by omega
      rw [he, pow_succ]
      simp only [mul_assoc]
    · simp
end Algebra

section Estimates
variable {E : Type*} [NormedRing E] [NormOneClass E] [IsUltrametricDist E]

omit [NormOneClass E] in
theorem norm_ultra_add (x y : E) : ‖x + y‖ ≤ max ‖x‖ ‖y‖ :=
  IsUltrametricDist.norm_add_le_max x y

omit [NormOneClass E] in
theorem norm_add_bound {x y : E} {r : ℝ} (hx : ‖x‖ ≤ r) (hy : ‖y‖ ≤ r) :
    ‖x + y‖ ≤ r := (norm_ultra_add x y).trans (max_le hx hy)

omit [IsUltrametricDist E] in
theorem norm_power_le_one (A : E) (hA : ‖A‖ ≤ 1) (d : ℕ) : ‖A ^ d‖ ≤ 1 := by
  calc
    ‖A ^ d‖ ≤ ‖A‖ ^ d := norm_pow_le _ _
    _ ≤ 1 := pow_le_one₀ (norm_nonneg _) hA

theorem norm_tangent_le (A : E) (hA : ‖A‖ ≤ 1) (d : ℕ) (h : E) :
    ‖tangent A d h‖ ≤ ‖h‖ := by
  induction d with
  | zero => simp [tangent]
  | succ d ih =>
    apply norm_add_bound
    · calc
        ‖tangent A d h * A‖ ≤ ‖tangent A d h‖ * ‖A‖ := norm_mul_le _ _
        _ ≤ ‖h‖ * 1 := mul_le_mul ih hA (norm_nonneg _) (norm_nonneg _)
        _ = ‖h‖ := mul_one _
    · calc
        ‖A ^ d * h‖ ≤ ‖A ^ d‖ * ‖h‖ := norm_mul_le _ _
        _ ≤ 1 * ‖h‖ := mul_le_mul_of_nonneg_right (norm_power_le_one A hA d) (norm_nonneg _)
        _ = ‖h‖ := one_mul _

/-- The nonlinear remainder is rho-Lipschitz on the rho-ball, uniformly in degree. -/
theorem remainder_lipschitz (A : E) (hA : ‖A‖ ≤ 1) (ρ : ℝ)
    (hρ : 0 ≤ ρ) (hρ1 : ρ ≤ 1) (d : ℕ) :
    ∀ h k : E, ‖h‖ ≤ ρ → ‖k‖ ≤ ρ →
      ‖remainder A d h - remainder A d k‖ ≤ ρ * ‖h - k‖ := by
  induction d with
  | zero => intro h k _ _; simp [remainder, tangent, mul_nonneg hρ (norm_nonneg _)]
  | succ d ih =>
    intro h k hh hk
    have hrk : ‖remainder A d k‖ ≤ ρ * ‖k‖ := by
      simpa only [remainder_zero, sub_zero] using ih k 0 hk (by simpa using hρ)
    have hrk' : ‖remainder A d k‖ ≤ ρ := by nlinarith [norm_nonneg k]
    have hah : ‖A + h‖ ≤ 1 := norm_add_bound hA (hh.trans hρ1)
    have hDh : ‖tangent A d h - tangent A d k‖ ≤ ‖h - k‖ := by
      rw [← tangent_sub]
      exact norm_tangent_le A hA d (h-k)
    have hDk : ‖tangent A d k‖ ≤ ρ := (norm_tangent_le A hA d k).trans hk
    rw [remainder_difference_succ]
    apply norm_add_bound
    · apply norm_add_bound
      · apply norm_add_bound
        · calc
            ‖(remainder A d h - remainder A d k) * (A + h)‖ ≤
                ‖remainder A d h - remainder A d k‖ * ‖A+h‖ := norm_mul_le _ _
            _ ≤ (ρ * ‖h-k‖) * 1 := mul_le_mul (ih h k hh hk) hah
              (norm_nonneg _) (mul_nonneg hρ (norm_nonneg _))
            _ = _ := mul_one _
        · exact (norm_mul_le _ _).trans (mul_le_mul_of_nonneg_right hrk' (norm_nonneg _))
      · calc
          ‖(tangent A d h - tangent A d k) * h‖ ≤
              ‖tangent A d h - tangent A d k‖ * ‖h‖ := norm_mul_le _ _
          _ ≤ ‖h-k‖ * ρ := mul_le_mul hDh hh (norm_nonneg _) (norm_nonneg _)
          _ = _ := mul_comm _ _
    · exact (norm_mul_le _ _).trans (mul_le_mul_of_nonneg_right hDk (norm_nonneg _))

theorem remainder_bound (A : E) (hA : ‖A‖ ≤ 1) (ρ : ℝ)
    (hρ : 0 ≤ ρ) (hρ1 : ρ ≤ 1) (d : ℕ) (h : E) (hh : ‖h‖ ≤ ρ) :
    ‖remainder A d h‖ ≤ ρ * ‖h‖ := by
  simpa only [remainder_zero, sub_zero] using
    remainder_lipschitz A hA ρ hρ hρ1 d h 0 hh (by simpa using hρ)
end Estimates
end Komorebi.StrongArtin.MatrixHensel
