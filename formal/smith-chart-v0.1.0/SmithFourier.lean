import Mathlib.Analysis.Complex.Basic
import Mathlib.GroupTheory.OrderOfElement
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Ring
import Mathlib.Tactic.NormNum

/-!
The finite character filter for an arbitrary complex unit of exact order N.
The exact-order hypothesis is explicit; no assertion about a particular
implementation of exp or a floating-point root is smuggled into the result.
-/

open scoped BigOperators

namespace SmithFourier

theorem geometric_character_sum {u : ℂ} {N : ℕ} (hu : u ^ N = 1) :
    (∑ k ∈ Finset.range N, u ^ k) = if u = 1 then (N : ℂ) else 0 := by
  by_cases h : u = 1
  · simp [h]
  · have hg := geom_sum_mul u N
    rw [hu, sub_self] at hg
    have hz : (∑ k ∈ Finset.range N, u ^ k) = 0 :=
      (mul_eq_zero.mp hg).resolve_right (sub_ne_zero.mpr h)
    simp [h, hz]

theorem character_sum (w : ℂˣ) {N : ℕ} (_hN : 0 < N) (hw : orderOf w = N)
    (m j : ℕ) :
    (∑ k ∈ Finset.range N, (((w : ℂ) ^ m) / ((w : ℂ) ^ j)) ^ k) =
      if m % N = j % N then (N : ℂ) else 0 := by
  have hwN' : w ^ N = 1 := by simpa [hw] using pow_orderOf_eq_one w
  have hwN : (w : ℂ) ^ N = 1 := by
    simpa using congrArg (fun v : ℂˣ => (v : ℂ)) hwN'
  have hwne : (w : ℂ) ≠ 0 := w.ne_zero
  have hwm : ((w : ℂ) ^ m) ^ N = 1 := by
    rw [← pow_mul, Nat.mul_comm m N, pow_mul, hwN, one_pow]
  have hwj : ((w : ℂ) ^ j) ^ N = 1 := by
    rw [← pow_mul, Nat.mul_comm j N, pow_mul, hwN, one_pow]
  have hu : (((w : ℂ) ^ m) / ((w : ℂ) ^ j)) ^ N = 1 := by
    simp only [div_pow, hwm, hwj, div_self one_ne_zero]
  have heq : ((w : ℂ) ^ m) / ((w : ℂ) ^ j) = 1 ↔ m % N = j % N := by
    rw [div_eq_one_iff_eq (pow_ne_zero _ hwne)]
    constructor
    · intro he
      have he' : w ^ m = w ^ j := Units.ext he
      simpa only [hw] using (pow_inj_mod.mp he')
    · intro he
      have he' : w ^ m = w ^ j := pow_inj_mod.mpr (by simpa only [hw] using he)
      exact congrArg Units.val he'
  rw [geometric_character_sum hu]
  by_cases he : m % N = j % N <;> simp [heq, he]

theorem normalized_character_filter (w : ℂˣ) {N : ℕ} (hN : 0 < N)
    (hw : orderOf w = N) (m j : ℕ) :
    (N : ℂ)⁻¹ * (∑ k ∈ Finset.range N, (((w : ℂ) ^ m) / ((w : ℂ) ^ j)) ^ k) =
      if m % N = j % N then 1 else 0 := by
  rw [character_sum w hN hw m j]
  have hn : (N : ℂ) ≠ 0 := by exact_mod_cast hN.ne'
  split_ifs <;> simp [hn]

/-- A finite phase average selects exactly one residue class. -/
theorem finite_coefficient_filter (w : ℂˣ) {N : ℕ} (hN : 0 < N)
    (hw : orderOf w = N) (M j : ℕ) (a : ℕ → ℂ) :
    (N : ℂ)⁻¹ * (∑ k ∈ Finset.range N, ∑ m ∈ Finset.range M,
        a m * (((w : ℂ) ^ m) / ((w : ℂ) ^ j)) ^ k) =
      ∑ m ∈ Finset.range M, if m % N = j % N then a m else 0 := by
  calc
    _ = ∑ m ∈ Finset.range M, a m * ((N : ℂ)⁻¹ *
        ∑ k ∈ Finset.range N, (((w : ℂ) ^ m) / ((w : ℂ) ^ j)) ^ k) := by
          rw [Finset.sum_comm, Finset.mul_sum]
          apply Finset.sum_congr rfl
          intro m hm
          rw [← Finset.mul_sum]
          ring
    _ = _ := by
      apply Finset.sum_congr rfl
      intro m hm
      rw [normalized_character_filter w hN hw m j]
      split_ifs <;> simp

/-- A monomial in the algebraic filter is the corresponding phase rotation. -/
theorem phase_monomial (w : ℂˣ) (k m j : ℕ) (a t : ℂ) :
    (((w : ℂ) ^ j)⁻¹) ^ k * (a * (((w : ℂ) ^ k) * t) ^ m) =
      (a * t ^ m) * ((((w : ℂ) ^ m) / ((w : ℂ) ^ j)) ^ k) := by
  simp only [mul_pow, div_pow, inv_pow, ← pow_mul]
  rw [Nat.mul_comm k m]
  ring

/-- The usual finite phase-orbit average equals polynomial coefficient selection. -/
theorem phase_average_finite (w : ℂˣ) {N : ℕ} (hN : 0 < N)
    (hw : orderOf w = N) (M j : ℕ) (a : ℕ → ℂ) (t : ℂ) :
    (N : ℂ)⁻¹ * (∑ k ∈ Finset.range N, (((w : ℂ) ^ j)⁻¹) ^ k *
      (∑ m ∈ Finset.range M, a m * (((w : ℂ) ^ k) * t) ^ m)) =
      ∑ m ∈ Finset.range M, if m % N = j % N then a m * t ^ m else 0 := by
  have hs : (∑ k ∈ Finset.range N, (((w : ℂ) ^ j)⁻¹) ^ k *
      (∑ m ∈ Finset.range M, a m * (((w : ℂ) ^ k) * t) ^ m)) =
      ∑ k ∈ Finset.range N, ∑ m ∈ Finset.range M,
        (a m * t ^ m) * (((w : ℂ) ^ m) / ((w : ℂ) ^ j)) ^ k := by
    apply Finset.sum_congr rfl
    intro k hk
    rw [Finset.mul_sum]
    apply Finset.sum_congr rfl
    intro m hm
    exact phase_monomial w k m j (a m) t
  rw [hs]
  exact finite_coefficient_filter w hN hw M j (fun m => a m * t ^ m)

end SmithFourier
