module
public import PolynomialTaylorRing

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace Komorebi.PolynomialTaylorDisplacement
open scoped BigOperators
open MvPolynomial
variable {R : Type*} [CommRing R] {d : ℕ}

/-- The Taylor error is divisible by the square of any common divisor of the
actual coordinate displacement. The Jacobian entries are evaluated derivatives. -/
theorem taylor_remainder_dvd (P : MvPolynomial (Fin d) R)
    (a b : Fin d → R) (c : R) (h : ∀ i, c ∣ b i - a i) :
    c ^ 2 ∣ eval b P - eval a P -
      ∑ i, eval a (pderiv i P) * (b i - a i) := by
  choose u hu using h
  have hb : b = fun i => a i + c * u i := by
    funext i
    linear_combination hu i
  obtain ⟨Q, hQ, _⟩ := PolynomialTaylorRing.exists_eval_scaled_remainder P a c
  have hsum : (∑ i, eval a (pderiv i P) * (b i - a i)) =
      c * (∑ i, eval a (pderiv i P) * u i) := by
    rw [Finset.mul_sum]
    apply Finset.sum_congr rfl
    intro i _
    rw [hu i]
    ring
  refine ⟨eval u Q, ?_⟩
  rw [hsum, hb, hQ]
  ring

end Komorebi.PolynomialTaylorDisplacement
