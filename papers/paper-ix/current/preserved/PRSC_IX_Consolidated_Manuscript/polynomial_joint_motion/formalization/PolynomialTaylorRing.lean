module

public import Mathlib.Algebra.MvPolynomial.PDeriv
public import Mathlib.Algebra.MvPolynomial.Monad
public import Mathlib.Tactic

@[expose] public section

noncomputable section
set_option autoImplicit false

namespace Komorebi.PolynomialTaylorRing

open scoped BigOperators
open MvPolynomial

variable {R : Type*} [CommRing R] {d : ℕ}

/-- The polynomial linear part formed from the actual partial derivatives. -/
def linearPart (P : MvPolynomial (Fin d) R) (a : Fin d → R) :
    MvPolynomial (Fin d) R :=
  ∑ i, C (eval a (pderiv i P)) * X i

@[simp] theorem linearPart_C (r : R) (a : Fin d → R) :
    linearPart (C r) a = 0 := by
  simp [linearPart]

@[simp] theorem linearPart_add (P Q : MvPolynomial (Fin d) R) (a : Fin d → R) :
    linearPart (P + Q) a = linearPart P a + linearPart Q a := by
  simp [linearPart, map_add, add_mul, Finset.sum_add_distrib]

theorem linearPart_mul (P Q : MvPolynomial (Fin d) R) (a : Fin d → R) :
    linearPart (P * Q) a = linearPart P a * C (eval a Q) +
      C (eval a P) * linearPart Q a := by
  simp only [linearPart, pderiv_mul, map_add, map_mul, add_mul,
    Finset.sum_add_distrib, Finset.sum_mul, Finset.mul_sum]
  congr 1 <;> apply Finset.sum_congr rfl <;> intro i hi <;> ring

@[simp] theorem linearPart_X (j : Fin d) (a : Fin d → R) :
    linearPart (X j) a = X j := by
  classical
  simp [linearPart, pderiv_X, Pi.single_apply, apply_ite]

@[simp] theorem eval_zero_linearPart (P : MvPolynomial (Fin d) R) (a : Fin d → R) :
    eval (0 : Fin d → R) (linearPart P a) = 0 := by
  simp [linearPart]

@[simp] theorem eval_linearPart (P : MvPolynomial (Fin d) R) (a u : Fin d → R) :
    eval u (linearPart P a) = ∑ i, eval a (pderiv i P) * u i := by
  simp [linearPart]

/-- Polynomial Taylor normalization, with a polynomial remainder whose constant term is zero. -/
theorem exists_scaled_remainder (P : MvPolynomial (Fin d) R) (a : Fin d → R) (c : R) :
    ∃ Q : MvPolynomial (Fin d) R,
      bind₁ (fun i => C (a i) + C c * X i) P =
        C (eval a P) + C c * linearPart P a + C (c ^ 2) * Q ∧
      eval (0 : Fin d → R) Q = 0 := by
  induction P using MvPolynomial.induction_on with
  | C r => exact ⟨0, by simp, by simp⟩
  | add P S hP hS =>
    obtain ⟨Q, hQ, hQ0⟩ := hP
    obtain ⟨T, hT, hT0⟩ := hS
    refine ⟨Q + T, ?_, by simp only [map_add, hQ0, hT0, add_zero]⟩
    simp only [map_add, linearPart_add]
    rw [hQ, hT]
    ring
  | mul_X P j hP =>
    obtain ⟨Q, hQ, hQ0⟩ := hP
    refine ⟨Q * (C (a j) + C c * X j) + linearPart P a * X j, ?_, ?_⟩
    · simp only [map_mul, bind₁_X_right, eval_X, linearPart_mul, linearPart_X]
      rw [hQ]
      simp only [map_pow]
      ring
    · simp only [map_add, map_mul, eval_C, eval_X, Pi.zero_apply, hQ0,
        mul_zero, add_zero, zero_mul]

/-- Evaluation of the scaled substitution. -/
theorem eval_scaled_bind (P : MvPolynomial (Fin d) R) (a u : Fin d → R) (c : R) :
    eval u (bind₁ (fun i => C (a i) + C c * X i) P) =
      eval (fun i => a i + c * u i) P := by
  change eval₂Hom (RingHom.id R) u (bind₁ _ P) = _
  rw [eval₂Hom_bind₁]
  simp only [map_add, map_mul, eval₂Hom_C, eval₂Hom_X', RingHom.id_apply]
  rfl

/-- The same remainder works at every point, rather than being chosen after evaluation. -/
theorem exists_eval_scaled_remainder (P : MvPolynomial (Fin d) R)
    (a : Fin d → R) (c : R) :
    ∃ Q : MvPolynomial (Fin d) R,
      (∀ u : Fin d → R, eval (fun i => a i + c * u i) P =
        eval a P + c * (∑ i, eval a (pderiv i P) * u i) + c ^ 2 * eval u Q) ∧
      eval (0 : Fin d → R) Q = 0 := by
  obtain ⟨Q, hQ, hQ0⟩ := exists_scaled_remainder P a c
  refine ⟨Q, ?_, hQ0⟩
  intro u
  have h := congrArg (eval u) hQ
  simpa only [eval_scaled_bind, map_add, map_mul, eval_C, eval_linearPart] using h

/-- Polynomial evaluation respects divisibility of all coordinate differences over any commutative ring. -/
theorem eval_dvd_of_dvd (P : MvPolynomial (Fin d) R) (x y : Fin d → R)
    (c : R) (h : ∀ i, c ∣ y i - x i) :
    c ∣ eval y P - eval x P := by
  induction P using MvPolynomial.induction_on with
  | C r => simp
  | add P Q hP hQ =>
    simp only [map_add]
    convert dvd_add hP hQ using 2
    ring
  | mul_X P j hP =>
    obtain ⟨r, hr⟩ := hP
    obtain ⟨s, hs⟩ := h j
    refine ⟨r * y j + eval x P * s, ?_⟩
    simp only [map_mul, eval_X]
    linear_combination y j * hr + eval x P * hs

end Komorebi.PolynomialTaylorRing
