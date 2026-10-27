module

public import PolynomialWeightedNormalization

@[expose] public section

noncomputable section
set_option autoImplicit false

namespace Komorebi.PolynomialMotionNormalization

open scoped BigOperators
open MvPolynomial
open Komorebi.PolynomialTaylorRing Komorebi.PolynomialWeightedInverse
open Komorebi.PolynomialWeightedNormalization

variable {d : ℕ}

/-- The actual polynomial perturbation, including its specified power of the prime. -/
def perturbSystem (p M : ℕ) [Fact (Nat.Prime p)]
    (F H : Fin d → MvPolynomial (Fin d) ℤ_[p]) :
    Fin d → MvPolynomial (Fin d) ℤ_[p] :=
  fun i => F i + C ((p : ℤ_[p]) ^ M) * H i

/-- Evaluation retains exactly the requested perturbation. -/
theorem eval_perturbSystem (p M : ℕ) [Fact (Nat.Prime p)]
    (F H : Fin d → MvPolynomial (Fin d) ℤ_[p]) (z : Fin d → ℤ_[p]) (i : Fin d) :
    eval z (perturbSystem p M F H i) =
      eval z (F i) + (p : ℤ_[p]) ^ M * eval z (H i) := by
  simp [perturbSystem]

/-- Constant matrix preconditioning commutes with the actual perturbation. -/
theorem precondition_perturbSystem (p M : ℕ) [Fact (Nat.Prime p)]
    (A : Matrix (Fin d) (Fin d) ℤ_[p])
    (F H : Fin d → MvPolynomial (Fin d) ℤ_[p]) (i : Fin d) :
    precondition A (perturbSystem p M F H) i =
      precondition A F i + C ((p : ℤ_[p]) ^ M) * precondition A H i := by
  simp only [precondition, perturbSystem, mul_add, Finset.sum_add_distrib,
    Finset.mul_sum]
  congr 1
  apply Finset.sum_congr rfl
  intro j _
  ring

/-- Scaled polynomial differences have a polynomial quotient vanishing at zero. -/
theorem exists_eval_scaled_difference {R : Type*} [CommRing R]
    (P : MvPolynomial (Fin d) R) (a : Fin d → R) (c : R) :
    ∃ Q : MvPolynomial (Fin d) R,
      (∀ u : Fin d → R, eval (fun i => a i + c * u i) P =
        eval a P + c * eval u Q) ∧
      eval (0 : Fin d → R) Q = 0 := by
  obtain ⟨Q, hQ, hQ0⟩ := exists_eval_scaled_remainder P a c
  refine ⟨linearPart P a + C c * Q, ?_, ?_⟩
  · intro u
    rw [hQ u]
    simp only [map_add, map_mul, eval_C, eval_linearPart]
    ring
  · simp only [map_add, map_mul, eval_C, eval_zero_linearPart, hQ0, mul_zero, add_zero]

/-- Normalization uses the original Jacobian certificate. No Jacobian assumption
on the perturbed system is needed. -/
theorem exists_motion_normalization (p s M : ℕ) [Fact (Nat.Prime p)]
    (hr : 2 * s < M) (F H : Fin d → MvPolynomial (Fin d) ℤ_[p])
    (a : Fin d → ℤ_[p]) (A : Matrix (Fin d) (Fin d) ℤ_[p])
    (hAJ : A * jacobian F a = (p : ℤ_[p]) ^ s •
      (1 : Matrix (Fin d) (Fin d) ℤ_[p]))
    (hF : ∀ i, eval a (F i) = 0) :
    ∃ C₀ : Fin d → ℤ_[p], ∃ Q : Fin d → MvPolynomial (Fin d) ℤ_[p],
      (∀ i, (p : ℤ_[p]) ^ (M - (2 * s + 1)) ∣ C₀ i) ∧
      (∀ i, eval (0 : Fin d → ℤ_[p]) (Q i) = 0) ∧
      (∀ (u : Fin d → ℤ_[p]) i,
        eval (fun j => a j + (p : ℤ_[p]) ^ (s + 1) * u j)
          (precondition A (perturbSystem p M F H) i) =
          (p : ℤ_[p]) ^ (2 * s + 1) *
            (C₀ i + u i + (p : ℤ_[p]) * eval u (Q i))) := by
  have hAF : ∀ i, eval a (precondition A F i) = 0 := by
    intro i
    simp [precondition, hF]
  choose QF hQF hQF0 using fun i => exists_eval_scaled_remainder
    (precondition A F i) a ((p : ℤ_[p]) ^ (s + 1))
  choose QH hQH hQH0 using fun i => exists_eval_scaled_difference
    (precondition A H i) a ((p : ℤ_[p]) ^ (s + 1))
  refine ⟨fun i => (p : ℤ_[p]) ^ (M - (2 * s + 1)) *
      eval a (precondition A H i),
    fun i => QF i + C ((p : ℤ_[p]) ^ (M - (s + 1))) * QH i,
    fun i => dvd_mul_right _ _, ?_, ?_⟩
  · intro i
    simp only [map_add, map_mul, eval_C, hQF0, hQH0, mul_zero, add_zero]
  · intro u i
    rw [precondition_perturbSystem]
    simp only [map_add, map_mul, eval_C]
    rw [hQF i u, hQH i u, hAF i, precondition_directional p s F a A hAJ]
    have hpow₀ : (p : ℤ_[p]) ^ (2 * s + 1) *
        (p : ℤ_[p]) ^ (M - (2 * s + 1)) = (p : ℤ_[p]) ^ M := by
      rw [← pow_add, Nat.add_sub_of_le (by omega)]
    have hpow₁ : (p : ℤ_[p]) ^ (s + 1) * (p : ℤ_[p]) ^ s =
        (p : ℤ_[p]) ^ (2 * s + 1) := by
      rw [← pow_add]
      congr 1
      omega
    have hpow₂ : ((p : ℤ_[p]) ^ (s + 1)) ^ 2 =
        (p : ℤ_[p]) ^ (2 * s + 1) * (p : ℤ_[p]) := by
      rw [← pow_mul, ← pow_succ]
      congr 1
      omega
    have hpow₃ : (p : ℤ_[p]) ^ (2 * s + 1) * (p : ℤ_[p]) *
        (p : ℤ_[p]) ^ (M - (s + 1)) =
        (p : ℤ_[p]) ^ M * (p : ℤ_[p]) ^ (s + 1) := by
      rw [← pow_succ, ← pow_add, ← pow_add]
      congr 1
      omega
    rw [hpow₂]
    linear_combination -(eval a (precondition A H i)) * hpow₀ +
      (u i) * hpow₁ - (eval u (QH i)) * hpow₃

end Komorebi.PolynomialMotionNormalization
