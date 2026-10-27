module
public import PolynomialWeightedInverse

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace Komorebi.PolynomialMotionRational
open Matrix Komorebi.PolynomialWeightedInverse
variable {d : ℕ}

/-- The inclusion of integral p-adic vectors commutes with matrix multiplication. -/
theorem coe_mulVec (p : ℕ) [Fact (Nat.Prime p)]
    (A : Matrix (Fin d) (Fin d) ℤ_[p]) (v : Fin d → ℤ_[p]) :
    (fun i => (A.mulVec v i : ℚ_[p])) =
      (rationalMatrix p A).mulVec (fun i => (v i : ℚ_[p])) := by
  ext i
  simp [Matrix.mulVec, dotProduct, rationalMatrix]

/-- The integral correction using a scaled inverse is exactly the rational Newton correction. -/
theorem scaled_inverse_mulVec (p s M : ℕ) [Fact (Nat.Prime p)] (hMs : s ≤ M)
    (J A : Matrix (Fin d) (Fin d) ℤ_[p])
    (hA : rationalMatrix p A = (p : ℚ_[p])^s • (rationalMatrix p J)⁻¹)
    (v : Fin d → ℤ_[p]) (i : Fin d) :
    (((p : ℤ_[p])^(M-s) * A.mulVec v i : ℤ_[p]) : ℚ_[p]) =
      (p : ℚ_[p])^M * ((rationalMatrix p J)⁻¹).mulVec
        (fun j => (v j : ℚ_[p])) i := by
  have hv := congrFun (coe_mulVec p A v) i
  rw [hA, Matrix.smul_mulVec] at hv
  simp only [Pi.smul_apply, smul_eq_mul] at hv
  push_cast
  rw [hv, ← mul_assoc, ← pow_add, Nat.sub_add_cancel hMs]

/-- A divisibility estimate on the integral correction yields the written first-order
formula over the fraction field, with an integral error of exactly the same depth. -/
theorem exists_rational_error (p s M N : ℕ) [Fact (Nat.Prime p)] (hMs : s ≤ M)
    (J A : Matrix (Fin d) (Fin d) ℤ_[p])
    (hA : rationalMatrix p A = (p : ℚ_[p])^s • (rationalMatrix p J)⁻¹)
    (a b v : Fin d → ℤ_[p])
    (herror : ∀ i, (p : ℤ_[p])^N ∣ b i - a i + (p : ℤ_[p])^(M-s) * A.mulVec v i) :
    ∃ ε : Fin d → ℤ_[p], (∀ i, (p : ℤ_[p])^N ∣ ε i) ∧
      ∀ i, (b i : ℚ_[p]) - (a i : ℚ_[p]) =
        -(p : ℚ_[p])^M * ((rationalMatrix p J)⁻¹).mulVec
          (fun j => (v j : ℚ_[p])) i + (ε i : ℚ_[p]) := by
  refine ⟨fun i => b i - a i + (p : ℤ_[p])^(M-s) * A.mulVec v i, herror, ?_⟩
  intro i
  have hscale := scaled_inverse_mulVec p s M hMs J A hA v i
  push_cast at hscale ⊢
  rw [hscale]
  ring

end Komorebi.PolynomialMotionRational
