import Mathlib.Analysis.Complex.Basic
import Mathlib.Analysis.SpecificLimits.Normed
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Ring
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Positivity

/-!
An independent companion to the Smith chart demonstration at Operation-KOMOREBI
revision ae02554bc86f30626fd9fad8d64b60854e307a80.

The existing Paper V SmithAction/SmithCyclic modules cover the homogeneous
cyclic action. This file connects the actual residue-class power series to its
closed form in the open reflection disk. See README.md for exact scope.
-/

open scoped BigOperators

namespace SmithChart

noncomputable def impedance (t : ℂ) : ℂ := (1 + t) / (1 - t)
noncomputable def admittance (t : ℂ) : ℂ := (1 - t) / (1 + t)

/-- The nonzero-exponent part of one residue lane, including its actual sum. -/
noncomputable def residueSeries (N j : ℕ) (t : ℂ) : ℂ :=
  ∑' m : ℕ, (2 : ℂ) * t ^ (j + m * N)

/-- The constant coefficient of impedance is one rather than two. -/
noncomputable def impedancePacket (N j : ℕ) (t : ℂ) : ℂ :=
  if j = 0 then 1 + residueSeries N N t else residueSeries N j t

theorem norm_pow_lt_one {t : ℂ} (ht : ‖t‖ < 1) {N : ℕ} (hN : 0 < N) :
    ‖t ^ N‖ < 1 := by
  rw [norm_pow]
  exact pow_lt_one₀ (norm_nonneg t) ht hN.ne'

theorem one_sub_pow_ne_zero {t : ℂ} (ht : ‖t‖ < 1) {N : ℕ} (hN : 0 < N) :
    1 - t ^ N ≠ 0 := by
  have hn := norm_pow_lt_one ht hN
  have hne : t ^ N ≠ 1 := by
    intro he
    rw [he, norm_one] at hn
    exact (lt_irrefl 1) hn
  exact sub_ne_zero.mpr hne.symm

/-- This is a convergent infinite sum, not a finite polynomial fixture. -/
theorem residue_hasSum {t : ℂ} (ht : ‖t‖ < 1) {N : ℕ} (hN : 0 < N) (j : ℕ) :
    HasSum (fun m : ℕ => (2 : ℂ) * t ^ (j + m * N))
      ((2 : ℂ) * t ^ j / (1 - t ^ N)) := by
  have hs := (hasSum_geometric_of_norm_lt_one (norm_pow_lt_one ht hN)).mul_left
    ((2 : ℂ) * t ^ j)
  have hf : (fun m : ℕ => (2 : ℂ) * t ^ (j + m * N)) =
      (fun m : ℕ => ((2 : ℂ) * t ^ j) * (t ^ N) ^ m) := by
    funext m
    rw [pow_add, Nat.mul_comm m N, pow_mul]
    ring
  rw [hf]
  simpa only [div_eq_mul_inv] using hs

theorem residue_closed {t : ℂ} (ht : ‖t‖ < 1) {N : ℕ} (hN : 0 < N) (j : ℕ) :
    residueSeries N j t = (2 : ℂ) * t ^ j / (1 - t ^ N) :=
  (residue_hasSum ht hN j).tsum_eq

theorem packet_zero {t : ℂ} (ht : ‖t‖ < 1) {N : ℕ} (hN : 0 < N) :
    impedancePacket N 0 t = (1 + t ^ N) / (1 - t ^ N) := by
  simp only [impedancePacket, ↓reduceIte, residue_closed ht hN N]
  have hd := one_sub_pow_ne_zero ht hN
  field_simp [hd]; ring

theorem packet_nonzero {t : ℂ} (ht : ‖t‖ < 1) {N j : ℕ} (hN : 0 < N)
    (hj : j ≠ 0) :
    impedancePacket N j t = (2 : ℂ) * t ^ j / (1 - t ^ N) := by
  simp only [impedancePacket, hj, ↓reduceIte, residue_closed ht hN j]

/-- The admittance lane selects the coefficients of z(-t) = y(t). -/
noncomputable def admittancePacket (N j : ℕ) (t : ℂ) : ℂ :=
  impedancePacket N j (-t)

theorem admittance_as_neg_impedance (t : ℂ) : admittance t = impedance (-t) := by
  simp [admittance, impedance, sub_eq_add_neg]

theorem admittance_inverse (t : ℂ) : admittance t = (impedance t)⁻¹ := by
  simp [admittance, impedance, div_eq_mul_inv]

theorem packet_uniform {t : ℂ} (ht : ‖t‖ < 1) {N : ℕ} (hN : 0 < N) (j : ℕ) :
    impedancePacket N j t =
      ((2 : ℂ) * t ^ j / (1 - t ^ N)) - (if j = 0 then 1 else 0) := by
  by_cases hj : j = 0
  · subst j
    rw [packet_zero ht hN]
    simp only [pow_zero, mul_one, ↓reduceIte]
    have hd := one_sub_pow_ne_zero ht hN
    field_simp [hd]; ring
  · rw [packet_nonzero ht hN hj]
    simp [hj]

/-- Even-order admittance packets have the same denominator and a parity sign. -/
theorem even_admittance_duality {t : ℂ} (ht : ‖t‖ < 1) {N : ℕ} (hN : 0 < N)
    (hEven : Even N) (j : ℕ) :
    admittancePacket N j t = (-1 : ℂ) ^ j * impedancePacket N j t := by
  have hnt : ‖-t‖ < 1 := by simpa using ht
  by_cases hj : j = 0
  · subst j
    simp only [admittancePacket, packet_zero hnt hN, packet_zero ht hN,
      pow_zero, one_mul, hEven.neg_pow]
  · rw [admittancePacket, packet_nonzero hnt hN hj, packet_nonzero ht hN hj]
    rw [hEven.neg_pow, neg_pow]
    ring

theorem odd_admittance_zero {t : ℂ} (ht : ‖t‖ < 1) {N : ℕ} (hN : 0 < N)
    (hOdd : Odd N) :
    admittancePacket N 0 t = (1 - t ^ N) / (1 + t ^ N) := by
  have hnt : ‖-t‖ < 1 := by simpa using ht
  rw [admittancePacket, packet_zero hnt hN, hOdd.neg_pow]
  simp [sub_eq_add_neg]

theorem odd_admittance_nonzero {t : ℂ} (ht : ‖t‖ < 1) {N j : ℕ}
    (hN : 0 < N) (hOdd : Odd N) (hj : j ≠ 0) :
    admittancePacket N j t = (2 : ℂ) * (-1 : ℂ) ^ j * t ^ j / (1 + t ^ N) := by
  have hnt : ‖-t‖ < 1 := by simpa using ht
  rw [admittancePacket, packet_nonzero hnt hN hj, hOdd.neg_pow, neg_pow]
  ring

/-- All N analytic residue lanes reconstruct normalized impedance. -/
theorem packet_reconstruction {t : ℂ} (ht : ‖t‖ < 1) {N : ℕ} (hN : 0 < N) :
    (∑ j ∈ Finset.range N, impedancePacket N j t) = impedance t := by
  have hsum : (∑ j ∈ Finset.range N, impedancePacket N j t) =
      (2 / (1 - t ^ N)) * (∑ j ∈ Finset.range N, t ^ j) - 1 := by
    simp_rw [packet_uniform ht hN]
    rw [Finset.sum_sub_distrib]
    have hf : (∑ j ∈ Finset.range N, (2 : ℂ) * t ^ j / (1 - t ^ N)) =
        (2 / (1 - t ^ N)) * (∑ j ∈ Finset.range N, t ^ j) := by
      rw [Finset.mul_sum]
      apply Finset.sum_congr rfl
      intro j hj
      ring
    rw [hf]
    simp [hN]
  rw [hsum]
  have hd := one_sub_pow_ne_zero ht hN
  have htne : 1 - t ≠ 0 := by
    simpa using (one_sub_pow_ne_zero ht (N := 1) (by decide))
  have hgeom := geom_sum_mul_neg t N
  unfold impedance
  field_simp [hd, htne]
  linear_combination 2 * hgeom

/-- A lane at order N is the sum of its two order-2N descendants. -/
theorem packet_dyadic_refinement {t : ℂ} (ht : ‖t‖ < 1) {N j : ℕ}
    (hN : 0 < N) :
    impedancePacket N j t =
      impedancePacket (2 * N) j t + impedancePacket (2 * N) (j + N) t := by
  have h2 : 0 < 2 * N := by omega
  have hd := one_sub_pow_ne_zero ht hN
  have hd2 := one_sub_pow_ne_zero ht h2
  have hp : t ^ (2 * N) = (t ^ N) ^ 2 := by rw [Nat.mul_comm 2 N, pow_mul]
  rw [hp] at hd2
  by_cases hj0 : j = 0
  · subst j
    simp only [Nat.zero_add]
    rw [packet_zero ht hN, packet_zero ht h2,
      packet_nonzero ht h2 hN.ne']
    rw [hp]
    field_simp [hd, hd2]; ring
  · have hjN : j + N ≠ 0 := by omega
    rw [packet_nonzero ht hN hj0, packet_nonzero ht h2 hj0,
      packet_nonzero ht h2 hjN]
    rw [hp, pow_add]
    field_simp [hd, hd2]; ring

end SmithChart
