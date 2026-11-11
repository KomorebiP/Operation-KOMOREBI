import SmithFourier
import SmithAnalyticFourier
import Mathlib.Analysis.Complex.Basic
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Ring

open scoped BigOperators

namespace SmithParseval

noncomputable def phase (w : ℂˣ) (j k : ℕ) : ℂ := (((w : ℂ) ^ j)⁻¹) ^ k
noncomputable def packet (w : ℂˣ) (N j : ℕ) (f : ℕ → ℂ) : ℂ :=
  (N : ℂ)⁻¹ * ∑ k ∈ Finset.range N, phase w j k * f k

theorem root_norm_one (w : ℂˣ) {N : ℕ} (hN : 0 < N) (hw : orderOf w = N) :
    ‖(w : ℂ)‖ = 1 := by
  have h : (w : ℂ) ^ N = 1 := by
    have hu : w ^ N = 1 := by simpa [hw] using pow_orderOf_eq_one w
    simpa using congrArg (fun v : ℂˣ => (v : ℂ)) hu
  exact Complex.norm_eq_one_of_pow_eq_one h hN.ne'

theorem conjugate_phase (w : ℂˣ) {N : ℕ} (hN : 0 < N) (hw : orderOf w = N)
    (j k : ℕ) : (starRingEnd ℂ) (phase w j k) = ((w : ℂ) ^ j) ^ k := by
  have hc : (starRingEnd ℂ) (w : ℂ) = (w : ℂ)⁻¹ :=
    (Complex.inv_eq_conj (root_norm_one w hN hw)).symm
  simp [phase, hc]

theorem phase_pair (w : ℂˣ) (j k l : ℕ) (a b : ℂ) :
    (phase w j k * a) * (((w : ℂ) ^ j) ^ l * b) =
      (a * b) * ((((w : ℂ) ^ l) / ((w : ℂ) ^ k)) ^ j) := by
  simp only [phase, div_pow, inv_pow, ← pow_mul]
  rw [Nat.mul_comm j k, Nat.mul_comm j l]
  ring

theorem expansion (w : ℂˣ) {N : ℕ} (hN : 0 < N) (hw : orderOf w = N)
    (j : ℕ) (f : ℕ → ℂ) :
    packet w N j f * (starRingEnd ℂ) (packet w N j f) =
      ((N : ℂ)⁻¹) ^ 2 * (∑ k ∈ Finset.range N, ∑ l ∈ Finset.range N,
        (f k * (starRingEnd ℂ) (f l)) * ((((w : ℂ) ^ l) / ((w : ℂ) ^ k)) ^ j)) := by
  unfold packet
  simp only [map_mul, map_inv₀, map_natCast, map_sum, conjugate_phase w hN hw]
  have he : (∑ k ∈ Finset.range N, phase w j k * f k) *
      (∑ l ∈ Finset.range N, ((w : ℂ) ^ j) ^ l * (starRingEnd ℂ) (f l)) =
      ∑ k ∈ Finset.range N, ∑ l ∈ Finset.range N,
        (f k * (starRingEnd ℂ) (f l)) * ((((w : ℂ) ^ l) / ((w : ℂ) ^ k)) ^ j) := by
    rw [Finset.sum_mul]
    apply Finset.sum_congr rfl
    intro k hk
    rw [Finset.mul_sum]
    apply Finset.sum_congr rfl
    intro l hl
    exact phase_pair w j k l (f k) ((starRingEnd ℂ) (f l))
  calc
    _ = ((N : ℂ)⁻¹) ^ 2 * ((∑ k ∈ Finset.range N, phase w j k * f k) *
      (∑ l ∈ Finset.range N, ((w : ℂ) ^ j) ^ l * (starRingEnd ℂ) (f l))) := by ring
    _ = _ := by rw [he]

theorem cross_sum (w : ℂˣ) {N : ℕ} (hN : 0 < N) (hw : orderOf w = N)
    (f : ℕ → ℂ) {k : ℕ} (hk : k < N) :
    (∑ l ∈ Finset.range N, (f k * (starRingEnd ℂ) (f l)) *
      (∑ j ∈ Finset.range N, (((w : ℂ) ^ l) / ((w : ℂ) ^ k)) ^ j)) =
      (N : ℂ) * (f k * (starRingEnd ℂ) (f k)) := by
  have hs : (∑ l ∈ Finset.range N, (f k * (starRingEnd ℂ) (f l)) *
      (∑ j ∈ Finset.range N, (((w : ℂ) ^ l) / ((w : ℂ) ^ k)) ^ j)) =
      ∑ l ∈ Finset.range N, if l = k then (f k * (starRingEnd ℂ) (f l)) * N else 0 := by
    apply Finset.sum_congr rfl
    intro l hl
    rw [SmithFourier.character_sum w hN hw l k]
    simp [Nat.mod_eq_of_lt (Finset.mem_range.mp hl), Nat.mod_eq_of_lt hk]
  rw [hs, Finset.sum_ite_eq']
  simp [Finset.mem_range.mpr hk, mul_comm]

theorem interchange (w : ℂˣ) (N : ℕ) (f : ℕ → ℂ) :
    (∑ j ∈ Finset.range N, ∑ k ∈ Finset.range N, ∑ l ∈ Finset.range N,
      (f k * (starRingEnd ℂ) (f l)) * ((((w : ℂ) ^ l) / ((w : ℂ) ^ k)) ^ j)) =
    ∑ k ∈ Finset.range N, ∑ l ∈ Finset.range N, (f k * (starRingEnd ℂ) (f l)) *
      (∑ j ∈ Finset.range N, (((w : ℂ) ^ l) / ((w : ℂ) ^ k)) ^ j) := by
  rw [Finset.sum_comm]
  apply Finset.sum_congr rfl
  intro k hk
  rw [Finset.sum_comm]
  apply Finset.sum_congr rfl
  intro l hl
  rw [Finset.mul_sum]

theorem complex_parseval (w : ℂˣ) {N : ℕ} (hN : 0 < N) (hw : orderOf w = N)
    (f : ℕ → ℂ) :
    (∑ j ∈ Finset.range N, packet w N j f * (starRingEnd ℂ) (packet w N j f)) =
      (N : ℂ)⁻¹ * ∑ k ∈ Finset.range N, f k * (starRingEnd ℂ) (f k) := by
  simp_rw [expansion w hN hw]
  rw [← Finset.mul_sum, interchange]
  have hs : (∑ k ∈ Finset.range N, ∑ l ∈ Finset.range N,
      (f k * (starRingEnd ℂ) (f l)) *
        (∑ j ∈ Finset.range N, (((w : ℂ) ^ l) / ((w : ℂ) ^ k)) ^ j)) =
      (N : ℂ) * ∑ k ∈ Finset.range N, f k * (starRingEnd ℂ) (f k) := by
    rw [Finset.mul_sum]
    apply Finset.sum_congr rfl
    intro k hk
    exact cross_sum w hN hw f (Finset.mem_range.mp hk)
  rw [hs]
  have hn : (N : ℂ) ≠ 0 := by exact_mod_cast hN.ne'
  field_simp [hn]

theorem self_conjugate (z : ℂ) :
    z * (starRingEnd ℂ) z = ((‖z‖ ^ 2 : ℝ) : ℂ) := by
  rw [Complex.sq_norm, Complex.normSq_eq_conj_mul_self]
  ring

/-- Parseval for any finite complex sample orbit and an exact-order phase. -/
theorem finite_parseval (w : ℂˣ) {N : ℕ} (hN : 0 < N) (hw : orderOf w = N)
    (f : ℕ → ℂ) :
    (∑ j ∈ Finset.range N, ‖packet w N j f‖ ^ 2) =
      (∑ k ∈ Finset.range N, ‖f k‖ ^ 2) / N := by
  have hc := complex_parseval w hN hw f
  simp_rw [self_conjugate] at hc
  push_cast at hc
  have hr : (∑ j ∈ Finset.range N, ‖packet w N j f‖ ^ 2) =
      (N : ℝ)⁻¹ * (∑ k ∈ Finset.range N, ‖f k‖ ^ 2) := by
    apply Complex.ofReal_injective
    push_cast
    exact hc
  simpa [div_eq_mul_inv, mul_comm] using hr

/-- Parseval specialized to the actual analytic impedance packets. -/
theorem impedance_orbit_parseval (w : ℂˣ) {N : ℕ} (hN : 0 < N) (hw : orderOf w = N)
    {t : ℂ} (ht : ‖t‖ < 1) :
    (∑ j ∈ Finset.range N, ‖SmithChart.impedancePacket N j t‖ ^ 2) =
      (∑ k ∈ Finset.range N, ‖SmithChart.impedance (((w : ℂ) ^ k) * t)‖ ^ 2) / N := by
  let f : ℕ → ℂ := fun k => SmithChart.impedance (((w : ℂ) ^ k) * t)
  have hp (j : ℕ) (hj : j < N) : packet w N j f = SmithChart.impedancePacket N j t := by
    exact SmithAnalyticFourier.average_eq_packet w hN hw hj ht
  calc
    _ = ∑ j ∈ Finset.range N, ‖packet w N j f‖ ^ 2 := by
      apply Finset.sum_congr rfl
      intro j hj
      rw [hp j (Finset.mem_range.mp hj)]
    _ = _ := finite_parseval w hN hw f

end SmithParseval
