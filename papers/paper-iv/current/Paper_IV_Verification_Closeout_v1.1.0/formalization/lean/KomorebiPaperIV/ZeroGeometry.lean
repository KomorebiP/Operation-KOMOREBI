/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.EntireBridge
import Mathlib.Analysis.SpecialFunctions.Complex.LogBounds
import Mathlib.Analysis.SpecialFunctions.Trigonometric.ComplexDeriv
import Mathlib.Analysis.Analytic.Order

/-! # Exact zero geometry and quantitative two-exponential cancellation

This module begins the formalization of Section 11. The cancellation estimate
uses the principal logarithm near one and gives universal explicit constants.
-/

namespace Komorebi.PaperIV
noncomputable section

/-- The exact order-two denominator, independently of the choices of roots. -/
theorem entireSigned_two_eq_cos {omega rho : ℂ}
    (homega : IsPrimitiveRoot omega 2) (hrho : rho ^ 2 = -1) (z : ℂ) :
    entireSigned 2 0 omega rho z = Complex.cos z := by
  rw [entireSigned_independent_roots (by decide) (by decide) homega
    (IsPrimitiveRoot.neg_one 0 (by decide)) hrho Complex.I_sq,
    entireSigned_zero_eq_average]
  simp [Finset.sum_range_succ, Complex.cos, mul_comm]
  ring

/-- Every complex zero in order two, with no omitted exceptional zeros. -/
theorem entireSigned_two_zero_iff {omega rho z : ℂ}
    (homega : IsPrimitiveRoot omega 2) (hrho : rho ^ 2 = -1) :
    entireSigned 2 0 omega rho z = 0 ↔
      ∃ k : ℤ, z = (2 * k + 1) * (Real.pi : ℂ) / 2 := by
  rw [entireSigned_two_eq_cos homega hrho, Complex.cos_eq_zero_iff]

/-- At every order-two zero the derivative is nonzero, hence the zero is simple. -/
theorem entireSigned_two_zero_derivative_ne_zero {omega rho z : ℂ}
    (homega : IsPrimitiveRoot omega 2) (hrho : rho ^ 2 = -1)
    (hz : entireSigned 2 0 omega rho z = 0) :
    deriv (entireSigned 2 0 omega rho) z ≠ 0 := by
  have he : entireSigned 2 0 omega rho = Complex.cos :=
    funext (entireSigned_two_eq_cos homega hrho)
  rw [he, Complex.deriv_cos]
  rw [he] at hz
  have hs : Complex.sin z ≠ 0 := by
    intro hs
    have h := Complex.sin_sq_add_cos_sq z
    simp [hs, hz] at h
  exact neg_ne_zero.mpr hs

/-- The positive/negative natural-number parametrization used in the paper. -/
theorem entireSigned_two_zero_iff_nat {omega rho z : ℂ}
    (homega : IsPrimitiveRoot omega 2) (hrho : rho ^ 2 = -1) :
    entireSigned 2 0 omega rho z = 0 ↔
      ∃ m : ℕ, z = ((m : ℂ) + 1 / 2) * (Real.pi : ℂ) ∨
        z = -(((m : ℂ) + 1 / 2) * (Real.pi : ℂ)) := by
  rw [entireSigned_two_zero_iff homega hrho]
  constructor
  · rintro ⟨k, rfl⟩
    cases k with
    | ofNat m =>
      refine ⟨m, Or.inl ?_⟩
      change (2 * (m : ℂ) + 1) * (Real.pi : ℂ) / 2 = ((m : ℂ) + 1 / 2) * (Real.pi : ℂ)
      ring
    | negSucc m =>
      refine ⟨m, Or.inr ?_⟩
      push_cast
      ring
  · rintro ⟨m, rfl | rfl⟩
    · refine ⟨(m : ℤ), ?_⟩
      push_cast
      ring
    · refine ⟨-(m : ℤ) - 1, ?_⟩
      push_cast
      ring

/-- All order-two zeros have analytic multiplicity exactly one. -/
theorem entireSigned_two_zero_order_one {omega rho z : ℂ}
    (homega : IsPrimitiveRoot omega 2) (hrho : rho ^ 2 = -1)
    (hz : entireSigned 2 0 omega rho z = 0) :
    analyticOrderAt (entireSigned 2 0 omega rho) z = 1 :=
  (analyticAt_entireSigned 2 0 omega rho z).analyticOrderAt_eq_one_of_zero_deriv_ne_zero
    hz (entireSigned_two_zero_derivative_ne_zero homega hrho hz)

/-- The order-two lattice spacing is exactly pi. -/
theorem orderTwo_zero_spacing :
    Real.pi / Real.sin (Real.pi / 2) = Real.pi := by simp

/-- The centers of cancellation of two exponentials. -/
def oddExponentialCenter (k : ℤ) : ℂ := (2 * k + 1) * (Real.pi : ℂ) * Complex.I

/-- A quantitative logarithmic inverse near any cancellation center. -/
theorem near_cancellation_exists {w : ℂ} (hw : ‖1 + Complex.exp w‖ ≤ 1 / 2) :
    ∃ k : ℤ, ‖w - oddExponentialCenter k‖ ≤ (3 / 2 : ℝ) * ‖1 + Complex.exp w‖ := by
  let u : ℂ := -(1 + Complex.exp w)
  have hu : ‖u‖ ≤ 1 / 2 := by simpa only [u, norm_neg] using hw
  have hlog := Complex.norm_log_one_add_half_le_self hu
  have he : Complex.exp w =
      Complex.exp (Complex.log (-Complex.exp w) + (Real.pi : ℂ) * Complex.I) := by
    rw [Complex.exp_add, Complex.exp_log (neg_ne_zero.mpr (Complex.exp_ne_zero w)),
      Complex.exp_pi_mul_I]
    ring
  obtain ⟨k, hk⟩ := Complex.exp_eq_exp_iff_exists_int.mp he
  refine ⟨k, ?_⟩
  have hd : w - oddExponentialCenter k = Complex.log (-Complex.exp w) := by
    unfold oddExponentialCenter
    linear_combination hk
  rw [hd]
  have heq : (1 : ℂ) + u = -Complex.exp w := by dsimp [u]; ring
  rw [heq] at hlog
  simpa only [u, norm_neg] using hlog

/-- Distinct cancellation centers are separated by at least one full period. -/
theorem oddExponentialCenter_separation {k l : ℤ} (hkl : k ≠ l) :
    2 * Real.pi ≤ ‖oddExponentialCenter k - oddExponentialCenter l‖ := by
  have he : oddExponentialCenter k - oddExponentialCenter l =
      (((2 * Real.pi * ((k - l : ℤ) : ℝ)) : ℝ) : ℂ) * Complex.I := by
    push_cast
    unfold oddExponentialCenter
    ring
  rw [he, norm_mul, Complex.norm_I, mul_one, Complex.norm_real,
    Real.norm_eq_abs, abs_mul, abs_of_pos (by positivity : 0 < 2 * Real.pi)]
  have hi : (1 : ℝ) ≤ |((k - l : ℤ) : ℝ)| := by
    exact_mod_cast (Int.one_le_abs (sub_ne_zero.mpr hkl))
  nlinarith [Real.pi_pos]

/-- Lemma 11.6 with explicit universal constants: epsilon = 1/2 and C = 3/2.
No strip restriction is required. -/
theorem near_cancellation_unique {w : ℂ} (hw : ‖1 + Complex.exp w‖ ≤ 1 / 2) :
    ∃! k : ℤ, ‖w - oddExponentialCenter k‖ ≤ (3 / 2 : ℝ) * ‖1 + Complex.exp w‖ := by
  obtain ⟨k, hk⟩ := near_cancellation_exists hw
  refine ⟨k, hk, ?_⟩
  intro l hl
  by_contra hne
  have hsep := oddExponentialCenter_separation hne
  have htri : ‖oddExponentialCenter l - oddExponentialCenter k‖ ≤
      ‖w - oddExponentialCenter l‖ + ‖w - oddExponentialCenter k‖ := by
    calc
      _ = ‖-(w - oddExponentialCenter l) + (w - oddExponentialCenter k)‖ := by
        congr 1
        ring
      _ ≤ _ := by simpa only [norm_neg] using
        norm_add_le (-(w - oddExponentialCenter l)) (w - oddExponentialCenter k)
  nlinarith [Real.two_le_pi]

end
end Komorebi.PaperIV
