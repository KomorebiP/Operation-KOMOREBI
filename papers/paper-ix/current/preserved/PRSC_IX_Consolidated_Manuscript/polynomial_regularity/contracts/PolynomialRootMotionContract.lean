module
public import PolynomialRootMotion

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace Komorebi.PolynomialRootMotionContract
open MvPolynomial
variable {d : ℕ}

/-- The original actual Jacobian certificate constructs a perturbed root and gives
its integral first-order error. All polynomial evaluations are written out. -/
theorem original_jacobian_integral_error (p s M : ℕ) [Fact p.Prime]
    (hM : 2 * s < M) (F H : Fin d → MvPolynomial (Fin d) ℤ_[p])
    (a : Fin d → ℤ_[p]) (A : Matrix (Fin d) (Fin d) ℤ_[p])
    (hAJ : A * (Matrix.of fun i j => eval a (pderiv j (F i))) =
      (p : ℤ_[p]) ^ s • (1 : Matrix (Fin d) (Fin d) ℤ_[p]))
    (hJA : (Matrix.of fun i j => eval a (pderiv j (F i))) * A =
      (p : ℤ_[p]) ^ s • (1 : Matrix (Fin d) (Fin d) ℤ_[p]))
    (hFa : ∀ i, eval a (F i) = 0) :
    ∃ b : Fin d → ℤ_[p],
      (∀ i, eval b (F i) + (p : ℤ_[p]) ^ M * eval b (H i) = 0) ∧
      (∀ i, (p : ℤ_[p]) ^ (M - s) ∣ b i - a i) ∧
      (∀ i, (p : ℤ_[p]) ^ (s + 1) ∣ b i - a i) ∧
      (∀ z : Fin d → ℤ_[p],
        (∀ i, eval z (F i) + (p : ℤ_[p]) ^ M * eval z (H i) = 0) →
        (∀ i, (p : ℤ_[p]) ^ (s + 1) ∣ z i - a i) → z = b) ∧
      (∀ i, (p : ℤ_[p]) ^ (2 * M - 3 * s) ∣
        b i - a i + (p : ℤ_[p]) ^ (M - s) * A.mulVec (fun j => eval a (H j)) i) := by
  obtain ⟨b, hb, hdepth, hball, huniq⟩ :=
    PolynomialRootMotion.exists_perturbed_root_certificate p s M hM F H a A hAJ hJA hFa
  have hroot : ∀ i, eval b (F i) + (p : ℤ_[p]) ^ M * eval b (H i) = 0 := by
    simpa only [PolynomialMotionNormalization.eval_perturbSystem] using hb
  refine ⟨b, hroot, hdepth, hball, ?_, ?_⟩
  · intro z hz hzb
    apply huniq z _ hzb
    simpa only [PolynomialMotionNormalization.eval_perturbSystem] using hz
  · exact PolynomialMotionEstimate.first_order_error_dvd p s M F H a b A
      hM hAJ hFa hroot hdepth

/-- The exact rational formula uses the actual original derivative matrix and the
actual perturbation. Full-ball unique existence comes before the extra precision,
so uniqueness is not restricted to roots already satisfying the error estimate. -/
theorem original_jacobian_rational_motion (p s M : ℕ) [Fact p.Prime]
    (hM : 2 * s < M) (F H : Fin d → MvPolynomial (Fin d) ℤ_[p])
    (a : Fin d → ℤ_[p]) (hFa : ∀ i, eval a (F i) = 0)
    (hJ : IsUnit ((algebraMap ℤ_[p] ℚ_[p]).mapMatrix
      (fun i j => eval a (pderiv j (F i)))))
    (hbound : ∃ A : Matrix (Fin d) (Fin d) ℤ_[p],
      (algebraMap ℤ_[p] ℚ_[p]).mapMatrix A = (p : ℚ_[p]) ^ s •
        ((algebraMap ℤ_[p] ℚ_[p]).mapMatrix (fun i j => eval a (pderiv j (F i))))⁻¹) :
    (∃! b : Fin d → ℤ_[p],
      (∀ i, eval b (F i) + (p : ℤ_[p]) ^ M * eval b (H i) = 0) ∧
      (∀ i, (p : ℤ_[p]) ^ (s + 1) ∣ b i - a i)) ∧
    (∀ b : Fin d → ℤ_[p],
      (∀ i, eval b (F i) + (p : ℤ_[p]) ^ M * eval b (H i) = 0) →
      (∀ i, (p : ℤ_[p]) ^ (s + 1) ∣ b i - a i) →
      (∀ i, (p : ℤ_[p]) ^ (M - s) ∣ b i - a i) ∧
      (∃ ε : Fin d → ℤ_[p], (∀ i, (p : ℤ_[p]) ^ (2 * M - 3 * s) ∣ ε i) ∧
        ∀ i, (b i : ℚ_[p]) - (a i : ℚ_[p]) =
          -(p : ℚ_[p]) ^ M *
            (((algebraMap ℤ_[p] ℚ_[p]).mapMatrix
              (fun k j => eval a (pderiv j (F k))))⁻¹).mulVec
              (fun j => (eval a (H j) : ℚ_[p])) i + (ε i : ℚ_[p]))) := by
  have result := PolynomialRootMotion.exists_unique_root_motion p s M hM F H a hFa hJ hbound
  unfold PolynomialWeightedInverse.rationalMatrix at result
  unfold PolynomialWeightedInverse.jacobian at result
  simpa only [PolynomialMotionNormalization.eval_perturbSystem] using result

end Komorebi.PolynomialRootMotionContract
