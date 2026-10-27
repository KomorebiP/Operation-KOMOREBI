module

public import Mathlib.Algebra.MvPolynomial.PDeriv
public import Mathlib.Tactic

@[expose] public section

namespace Komorebi.PolynomialTaylor

open scoped BigOperators
open MvPolynomial

/-- The actual directional derivative formed from the partial derivatives. -/
noncomputable def directional {d : ℕ} (P : MvPolynomial (Fin d) ℤ)
    (x t : Fin d → ℤ) : ℤ :=
  ∑ i, eval x (pderiv i P) * t i

theorem directional_C {d : ℕ} (c : ℤ) (x t : Fin d → ℤ) :
    directional (C c) x t = 0 := by
  simp [directional]

theorem directional_add {d : ℕ} (P Q : MvPolynomial (Fin d) ℤ)
    (x t : Fin d → ℤ) :
    directional (P + Q) x t = directional P x t + directional Q x t := by
  simp [directional, map_add, add_mul, Finset.sum_add_distrib]

theorem directional_mul {d : ℕ} (P Q : MvPolynomial (Fin d) ℤ)
    (x t : Fin d → ℤ) :
    directional (P * Q) x t =
      directional P x t * eval x Q + eval x P * directional Q x t := by
  simp only [directional, pderiv_mul, map_add, map_mul, add_mul,
    Finset.sum_add_distrib, Finset.sum_mul, Finset.mul_sum]
  congr 1 <;> apply Finset.sum_congr rfl <;> intro i hi <;> ring

theorem directional_X {d : ℕ} (j : Fin d) (x t : Fin d → ℤ) :
    directional (X j) x t = t j := by
  classical
  simp [directional, pderiv_X, Pi.single_apply, apply_ite]

/-- Integral first-order Taylor formula, with an actual divisible remainder. -/
theorem taylor_dvd {d : ℕ} (P : MvPolynomial (Fin d) ℤ)
    (x t : Fin d → ℤ) (a : ℤ) :
    a ^ 2 ∣ eval (fun i => x i + a * t i) P - eval x P - a * directional P x t := by
  induction P using MvPolynomial.induction_on with
  | C c => simp [directional]
  | add P Q hP hQ =>
    simp only [map_add, directional_add]
    convert dvd_add hP hQ using 2 <;> first | rfl | ring
  | mul_X P j hP =>
    obtain ⟨r, hr⟩ := hP
    refine ⟨r * (x j + a * t j) + directional P x t * t j, ?_⟩
    simp only [map_mul, eval_X, directional_mul, directional_X]
    linear_combination (x j + a * t j) * hr

/-- At positive depth the quadratic remainder vanishes at the next precision. -/
theorem taylor_step_dvd {d : ℕ} (P : MvPolynomial (Fin d) ℤ)
    (x t : Fin d → ℤ) (q L : ℕ) (hL : 1 ≤ L) :
    (q : ℤ) ^ (L + 1) ∣
      eval (fun i => x i + (q : ℤ) ^ L * t i) P - eval x P -
        (q : ℤ) ^ L * directional P x t := by
  apply dvd_trans (b := ((q : ℤ) ^ L) ^ 2) ?_ (taylor_dvd P x t _)
  rw [← pow_mul]
  exact pow_dvd_pow _ (by omega)

/-- Integral polynomial evaluation respects every coordinate congruence. -/
theorem eval_dvd_of_dvd {d : ℕ} (P : MvPolynomial (Fin d) ℤ)
    (x y : Fin d → ℤ) (a : ℤ) (h : ∀ i, a ∣ y i - x i) :
    a ∣ eval y P - eval x P := by
  induction P using MvPolynomial.induction_on with
  | C c => simp
  | add P Q hP hQ =>
    simp only [map_add]
    convert dvd_add hP hQ using 2 <;> first | rfl | ring
  | mul_X P j hP =>
    obtain ⟨r, hr⟩ := hP
    obtain ⟨s, hs⟩ := h j
    refine ⟨r * y j + eval x P * s, ?_⟩
    simp only [map_mul, eval_X]
    linear_combination y j * hr + eval x P * hs

/-- In particular, an integral Jacobian is constant modulo the base modulus. -/
theorem pderiv_eval_dvd_of_dvd {d : ℕ} (P : MvPolynomial (Fin d) ℤ)
    (x y : Fin d → ℤ) (a : ℤ) (h : ∀ i, a ∣ y i - x i) (j : Fin d) :
    a ∣ eval y (pderiv j P) - eval x (pderiv j P) :=
  eval_dvd_of_dvd (pderiv j P) x y a h

end Komorebi.PolynomialTaylor
