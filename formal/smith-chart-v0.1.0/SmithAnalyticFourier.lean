import SmithPackets
import SmithFourier

/-! The actual analytic impedance packet equals its phase-orbit average. -/

open scoped BigOperators

namespace SmithAnalyticFourier

noncomputable def phase (w : ℂˣ) (j k : ℕ) : ℂ := (((w : ℂ) ^ j)⁻¹) ^ k

noncomputable def average (w : ℂˣ) (N j : ℕ) (t : ℂ) : ℂ :=
  (N : ℂ)⁻¹ * ∑ k ∈ Finset.range N,
    phase w j k * SmithChart.impedance (((w : ℂ) ^ k) * t)

theorem order_pow (w : ℂˣ) {N : ℕ} (hw : orderOf w = N) : (w : ℂ) ^ N = 1 := by
  have hwN : w ^ N = 1 := by simpa [hw] using pow_orderOf_eq_one w
  simpa using congrArg (fun v : ℂˣ => (v : ℂ)) hwN

theorem rotated_pow (w : ℂˣ) {N : ℕ} (hw : orderOf w = N) (k : ℕ) (t : ℂ) :
    (((w : ℂ) ^ k) * t) ^ N = t ^ N := by
  rw [mul_pow, ← pow_mul, Nat.mul_comm k N, pow_mul, order_pow w hw, one_pow, one_mul]

theorem rotated_norm_lt_one (w : ℂˣ) {N : ℕ} (hN : 0 < N)
    (hw : orderOf w = N) (k : ℕ) {t : ℂ} (ht : ‖t‖ < 1) :
    ‖((w : ℂ) ^ k) * t‖ < 1 := by
  rw [norm_mul, norm_pow, Complex.norm_eq_one_of_pow_eq_one (order_pow w hw) hN.ne',
    one_pow, one_mul]
  exact ht

theorem polynomial_selection (w : ℂˣ) {N : ℕ} (hN : 0 < N)
    (hw : orderOf w = N) {j : ℕ} (hj : j < N) (t : ℂ) :
    (N : ℂ)⁻¹ * (∑ k ∈ Finset.range N, phase w j k *
      (∑ m ∈ Finset.range N, (((w : ℂ) ^ k) * t) ^ m)) = t ^ j := by
  have hs := SmithFourier.phase_average_finite w hN hw N j (fun _ => (1 : ℂ)) t
  simp only [one_mul] at hs
  have hselect : (∑ m ∈ Finset.range N, if m % N = j % N then t ^ m else 0) = t ^ j := by
    rw [Finset.sum_eq_single j]
    · simp
    · intro m hm hmj
      have hmlt : m < N := Finset.mem_range.mp hm
      simp [Nat.mod_eq_of_lt hmlt, Nat.mod_eq_of_lt hj, hmj]
    · intro hjnot
      exact False.elim (hjnot (Finset.mem_range.mpr hj))
  rw [hselect] at hs
  exact hs

theorem constant_selection (w : ℂˣ) {N : ℕ} (hN : 0 < N)
    (hw : orderOf w = N) {j : ℕ} (hj : j < N) :
    (N : ℂ)⁻¹ * (∑ k ∈ Finset.range N, phase w j k) =
      if j = 0 then 1 else 0 := by
  have hs := SmithFourier.normalized_character_filter w hN hw 0 j
  simpa [phase, Nat.mod_eq_of_lt hj, eq_comm] using hs

theorem scaled_impedance (w : ℂˣ) {N : ℕ} (hN : 0 < N)
    (hw : orderOf w = N) (k : ℕ) {t : ℂ} (ht : ‖t‖ < 1) :
    (1 - t ^ N) * SmithChart.impedance (((w : ℂ) ^ k) * t) =
      2 * (∑ m ∈ Finset.range N, (((w : ℂ) ^ k) * t) ^ m) - (1 - t ^ N) := by
  have hd := SmithChart.one_sub_pow_ne_zero (rotated_norm_lt_one w hN hw k ht)
    (N := 1) (by decide)
  simp only [pow_one] at hd
  have hg := geom_sum_mul_neg (((w : ℂ) ^ k) * t) N
  rw [rotated_pow w hw k t] at hg
  unfold SmithChart.impedance
  field_simp [hd]
  linear_combination -2 * hg

theorem average_eq_packet (w : ℂˣ) {N : ℕ} (hN : 0 < N)
    (hw : orderOf w = N) {j : ℕ} (hj : j < N) {t : ℂ} (ht : ‖t‖ < 1) :
    average w N j t = SmithChart.impedancePacket N j t := by
  have hpoly := polynomial_selection w hN hw hj t
  have hconst := constant_selection w hN hw hj
  have hd := SmithChart.one_sub_pow_ne_zero ht hN
  have hscaled : (1 - t ^ N) * average w N j t =
      2 * t ^ j - (1 - t ^ N) * (if j = 0 then 1 else 0) := by
    calc
      _ = (N : ℂ)⁻¹ * ∑ k ∈ Finset.range N, phase w j k *
          ((1 - t ^ N) * SmithChart.impedance (((w : ℂ) ^ k) * t)) := by
            unfold average
            simp_rw [Finset.mul_sum]
            apply Finset.sum_congr rfl
            intro k hk
            ring
      _ = 2 * ((N : ℂ)⁻¹ * ∑ k ∈ Finset.range N, phase w j k *
            (∑ m ∈ Finset.range N, (((w : ℂ) ^ k) * t) ^ m)) -
          (1 - t ^ N) * ((N : ℂ)⁻¹ * ∑ k ∈ Finset.range N, phase w j k) := by
            simp_rw [scaled_impedance w hN hw _ ht, mul_sub]
            rw [Finset.sum_sub_distrib]
            have hfirst : (∑ k ∈ Finset.range N, phase w j k *
                (2 * ∑ m ∈ Finset.range N, (((w : ℂ) ^ k) * t) ^ m)) =
                2 * (∑ k ∈ Finset.range N, phase w j k *
                  (∑ m ∈ Finset.range N, (((w : ℂ) ^ k) * t) ^ m)) := by
              rw [Finset.mul_sum]
              apply Finset.sum_congr rfl
              intro k hk
              ring
            have hsecond : (∑ k ∈ Finset.range N, (phase w j k * 1 - phase w j k * t ^ N)) =
                (1 - t ^ N) * (∑ k ∈ Finset.range N, phase w j k) := by
              calc
                _ = ∑ k ∈ Finset.range N, phase w j k * (1 - t ^ N) := by
                  apply Finset.sum_congr rfl
                  intro k hk
                  ring
                _ = _ := by
                  rw [Finset.mul_sum]
                  apply Finset.sum_congr rfl
                  intro k hk
                  ring
            rw [hfirst, hsecond]
            ring
      _ = _ := by rw [hpoly, hconst]
  rw [SmithChart.packet_uniform ht hN j]
  apply (mul_left_cancel₀ hd)
  rw [hscaled]
  field_simp [hd]

end SmithAnalyticFourier
