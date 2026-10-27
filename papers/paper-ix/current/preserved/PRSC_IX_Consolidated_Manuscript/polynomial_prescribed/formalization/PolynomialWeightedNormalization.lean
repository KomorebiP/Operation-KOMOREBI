module

public import PolynomialTaylorRing
public import PolynomialWeightedInverse

@[expose] public section

noncomputable section
set_option autoImplicit false

namespace Komorebi.PolynomialWeightedNormalization

open scoped BigOperators
open MvPolynomial
open Komorebi.PolynomialTaylorRing Komorebi.PolynomialWeightedInverse

variable {d : ℕ}

/-- The actual linear Taylor term of the preconditioned system is scalar multiplication. -/
theorem precondition_directional (p s : ℕ) [Fact (Nat.Prime p)]
    (F : Fin d → MvPolynomial (Fin d) ℤ_[p]) (a : Fin d → ℤ_[p])
    (A : Matrix (Fin d) (Fin d) ℤ_[p])
    (hAJ : A * jacobian F a = (p : ℤ_[p]) ^ s • (1 : Matrix (Fin d) (Fin d) ℤ_[p]))
    (u : Fin d → ℤ_[p]) (i : Fin d) :
    (∑ j, eval a (pderiv j (precondition A F i)) * u j) = (p : ℤ_[p]) ^ s * u i := by
  change (jacobian (precondition A F) a).mulVec u i = _
  rw [jacobian_precondition, hAJ, Matrix.smul_mulVec, Matrix.one_mulVec]
  rfl

/-- The actual nonlinear system admits an integral contraction normalization. The
remainder vanishes at zero, and the constant retains the exact excess residual precision. -/
theorem exists_normalization (p s r : ℕ) [Fact (Nat.Prime p)] (hr : 2 * s < r)
    (F : Fin d → MvPolynomial (Fin d) ℤ_[p]) (a : Fin d → ℤ_[p])
    (A : Matrix (Fin d) (Fin d) ℤ_[p])
    (hAJ : A * jacobian F a = (p : ℤ_[p]) ^ s • (1 : Matrix (Fin d) (Fin d) ℤ_[p]))
    (hF : ∀ i, (p : ℤ_[p]) ^ r ∣ eval a (F i)) :
    ∃ C₀ : Fin d → ℤ_[p], ∃ Q : Fin d → MvPolynomial (Fin d) ℤ_[p],
      (∀ i, (p : ℤ_[p]) ^ (r - (2 * s + 1)) ∣ C₀ i) ∧
      (∀ i, eval (0 : Fin d → ℤ_[p]) (Q i) = 0) ∧
      (∀ (u : Fin d → ℤ_[p]) i,
        eval (fun j => a j + (p : ℤ_[p]) ^ (s + 1) * u j) (precondition A F i) =
          (p : ℤ_[p]) ^ (2 * s + 1) *
            (C₀ i + u i + (p : ℤ_[p]) * eval u (Q i))) := by
  have hAF : ∀ i, (p : ℤ_[p]) ^ r ∣ eval a (precondition A F i) := by
    intro i
    have h := mulVec_preserves_dvd A ((p : ℤ_[p]) ^ r)
      (fun j => eval a (F j)) hF i
    rw [← eval_precondition A F a] at h
    exact h
  choose D hD using hAF
  choose Q hQ hQ0 using fun i => exists_eval_scaled_remainder
    (precondition A F i) a ((p : ℤ_[p]) ^ (s + 1))
  refine ⟨fun i => (p : ℤ_[p]) ^ (r - (2 * s + 1)) * D i, Q,
    fun i => dvd_mul_right _ _, hQ0, ?_⟩
  intro u i
  rw [hQ i u, hD i, precondition_directional p s F a A hAJ]
  have hpow₀ : (p : ℤ_[p]) ^ (2 * s + 1) * (p : ℤ_[p]) ^ (r - (2 * s + 1)) =
      (p : ℤ_[p]) ^ r := by
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
  rw [hpow₂]
  linear_combination -(D i) * hpow₀ + (u i) * hpow₁

end Komorebi.PolynomialWeightedNormalization
