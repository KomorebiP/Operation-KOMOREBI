import SmithAnalyticFourier
import SmithParseval
import Mathlib.Analysis.SpecialFunctions.Complex.Log

/-! The exact root displayed in the laboratory has the required order. -/

open scoped BigOperators

namespace SmithCanonicalRoot

noncomputable def omega (N : ℕ) : ℂ := Complex.exp (2 * Real.pi * Complex.I / N)

noncomputable def omegaUnit (N : ℕ) : ℂˣ :=
  Units.mk0 (omega N) (Complex.exp_ne_zero _)

theorem omega_pow_eq_one_iff {N : ℕ} (hN : 0 < N) (k : ℕ) :
    omega N ^ k = 1 ↔ N ∣ k := by
  unfold omega
  rw [← Complex.exp_nat_mul]
  have he : (k : ℂ) * (2 * Real.pi * Complex.I / N) =
      2 * Real.pi * Complex.I * k / N := by ring
  rw [he]
  exact Complex.exp_two_pi_mul_I_mul_div_eq_one_iff hN.ne'

theorem omega_unit_order {N : ℕ} (hN : 0 < N) : orderOf (omegaUnit N) = N := by
  apply (orderOf_eq_iff hN).2
  constructor
  · apply Units.ext
    change omega N ^ N = 1
    exact (omega_pow_eq_one_iff hN N).2 (dvd_refl N)
  · intro m hm hmpos he
    have he' : omega N ^ m = 1 := by
      have hc := congrArg (fun v : ℂˣ => (v : ℂ)) he
      change omega N ^ m = 1 at hc
      exact hc
    have hle : N ≤ m := Nat.le_of_dvd hmpos ((omega_pow_eq_one_iff hN m).1 he')
    exact (not_le_of_gt hm) hle

theorem canonical_average_eq_packet {N j : ℕ} (hN : 0 < N) (hj : j < N)
    {t : ℂ} (ht : ‖t‖ < 1) :
    SmithAnalyticFourier.average (omegaUnit N) N j t = SmithChart.impedancePacket N j t :=
  SmithAnalyticFourier.average_eq_packet (omegaUnit N) hN (omega_unit_order hN) hj ht

theorem canonical_orbit_parseval {N : ℕ} (hN : 0 < N) {t : ℂ} (ht : ‖t‖ < 1) :
    (∑ j ∈ Finset.range N, ‖SmithChart.impedancePacket N j t‖ ^ 2) =
      (∑ k ∈ Finset.range N,
        ‖SmithChart.impedance (((omegaUnit N : ℂˣ) : ℂ) ^ k * t)‖ ^ 2) / N :=
  SmithParseval.impedance_orbit_parseval (omegaUnit N) hN (omega_unit_order hN) ht

end SmithCanonicalRoot
