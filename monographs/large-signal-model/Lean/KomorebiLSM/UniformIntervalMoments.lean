import KomorebiLSM.AveragedCongruence
import Mathlib.Algebra.Polynomial.OfFn
import Mathlib.Algebra.Polynomial.Roots

/-! Exact power moments and positive polynomial Gram matrices for the actual
normalized Lebesgue measure on `[-1,1]`. Endpoints have zero Lebesgue mass. -/
set_option autoImplicit false
open MeasureTheory Matrix Polynomial
open scoped BigOperators ENNReal

namespace Komorebi.LSM.UniformIntervalMoments

noncomputable def measure : Measure ℝ := AveragedCongruence.uniformInterval (-1) 1

instance measure_isProbability : IsProbabilityMeasure measure :=
  AveragedCongruence.uniformInterval_isProbability (by norm_num)

/-- Integration is against the specified probability measure, not a formal moment oracle. -/
theorem integral_eq (f : ℝ → ℝ) :
    (∫ x, f x ∂measure) = (1 / 2 : ℝ) * ∫ x in (-1 : ℝ)..1, f x := by
  rw [measure, AveragedCongruence.integral_uniformInterval (by norm_num)]
  norm_num

theorem continuous_integrable {f : ℝ → ℝ} (hf : Continuous f) : Integrable f measure := by
  unfold measure AveragedCongruence.uniformInterval ProbabilityTheory.cond
  exact (hf.intervalIntegrable (-1) 1).1.smul_measure (by simp)

noncomputable def moment (k : ℕ) : ℝ := ∫ x, x ^ k ∂measure

theorem moment_formula (k : ℕ) :
    moment k = (1 - (-1 : ℝ) ^ (k + 1)) / (2 * (k + 1)) := by
  rw [moment, integral_eq, integral_pow]
  simp only [one_pow]
  field_simp

@[simp] theorem moment_even {k : ℕ} (hk : Even k) : moment k = 1 / (k + 1) := by
  rw [moment_formula, pow_succ, hk.neg_pow]
  simp only [one_pow, one_mul]
  field_simp
  norm_num

@[simp] theorem moment_odd {k : ℕ} (hk : Odd k) : moment k = 0 := by
  rw [moment_formula, pow_succ, hk.neg_pow]
  simp

@[simp] theorem moment_zero : moment 0 = 1 := by norm_num [moment_formula]

@[simp] theorem moment_one : moment 1 = 0 := by norm_num [moment_formula]

@[simp] theorem moment_two : moment 2 = 1 / 3 := by norm_num [moment_formula]

/-- A finite power expansion has the expected exact integral. -/
theorem integral_power_sum {n : ℕ} (c : Fin n → ℝ) :
    (∫ x, ∑ k : Fin n, c k * x ^ (k : ℕ) ∂measure) =
      ∑ k : Fin n, c k * moment k := by
  rw [integral_finsetSum (f := fun k x => c k * x ^ (k : ℕ)) _ (fun k _ =>
    continuous_integrable (continuous_const.mul (continuous_id.pow k))) ]
  simp only [integral_const_mul, moment]

/-- Finite coefficient vectors are represented by genuine polynomials. -/
theorem eval_ofFn {n : ℕ} (c : Fin n → ℝ) (x : ℝ) :
    (Polynomial.ofFn n c).eval x = ∑ k : Fin n, c k * x ^ (k : ℕ) := by
  rw [Polynomial.ofFn_eq_sum_monomial]
  simp only [Polynomial.eval_finsetSum, Polynomial.eval_monomial]

/-- Every nonzero polynomial has a positive squared integral for this measure. -/
theorem polynomial_square_integral_pos (p : ℝ[X]) (hp : p ≠ 0) :
    0 < ∫ x, (p.eval x) ^ 2 ∂measure := by
  obtain ⟨x, hx, hroot⟩ := ((Set.Ioo_infinite (by norm_num : (-1 : ℝ) < 1)).sdiff
    (Polynomial.finite_setOfPred_isRoot hp)).nonempty
  rw [integral_eq]
  apply mul_pos (by norm_num)
  apply intervalIntegral.integral_pos (by norm_num)
  · exact (p.continuous.pow 2).continuousOn
  · intro y _
    positivity
  · exact ⟨x, ⟨hx.1.le, hx.2.le⟩, sq_pos_of_ne_zero hroot⟩

/-- The `(D+1)` by `(D+1)` moment Gram matrix. -/
noncomputable def gram (D : ℕ) : Matrix (Fin (D + 1)) (Fin (D + 1)) ℝ :=
  fun j k => moment ((j : ℕ) + k)

/-- Its quadratic form is exactly the integral of the squared coefficient polynomial. -/
theorem gram_quadratic (D : ℕ) (c : Fin (D + 1) → ℝ) :
    star c ⬝ᵥ (gram D *ᵥ c) =
      ∫ x, ((Polynomial.ofFn (D + 1) c).eval x) ^ 2 ∂measure := by
  simp only [dotProduct, Matrix.mulVec, gram, Pi.star_apply, star_trivial]
  simp_rw [Finset.mul_sum]
  rw [show (fun x => ((Polynomial.ofFn (D + 1) c).eval x) ^ 2) =
      (fun x => ∑ j : Fin (D + 1), ∑ k : Fin (D + 1),
        (c j * c k) * x ^ ((j : ℕ) + k)) by
    funext x
    rw [eval_ofFn, pow_two, Finset.sum_mul]
    apply Finset.sum_congr rfl
    intro j _
    rw [Finset.mul_sum]
    apply Finset.sum_congr rfl
    intro k _
    rw [pow_add]
    ring]
  rw [integral_finsetSum _ (fun j _ => continuous_integrable (by fun_prop))]
  apply Finset.sum_congr rfl
  intro j _
  rw [integral_finsetSum (f := fun k x => (c j * c k) * x ^ ((j : ℕ) + k)) _
    (fun k _ => continuous_integrable (by fun_prop))]
  apply Finset.sum_congr rfl
  intro k _
  rw [integral_const_mul]
  change c j * (moment ((j : ℕ) + k) * c k) = (c j * c k) * moment ((j : ℕ) + k)
  ring

/-- Positive definiteness is proved from the nonzero-polynomial square integral. -/
theorem gram_posDef (D : ℕ) : (gram D).PosDef := by
  apply Matrix.PosDef.of_dotProduct_mulVec_pos
  · ext j k
    simp [gram, Nat.add_comm]
  · intro c hc
    rw [gram_quadratic]
    apply polynomial_square_integral_pos
    intro hz
    apply hc
    apply (Polynomial.injective_ofFn (D + 1))
    simpa using hz

theorem gram_isUnit (D : ℕ) : IsUnit (gram D) := (gram_posDef D).isUnit

theorem gram_mul_inv (D : ℕ) : gram D * (gram D)⁻¹ = 1 :=
  Matrix.mul_nonsing_inv _ ((Matrix.isUnit_iff_isUnit_det _).mp (gram_isUnit D))

theorem gram_inv_mul (D : ℕ) : (gram D)⁻¹ * gram D = 1 :=
  Matrix.nonsing_inv_mul _ ((Matrix.isUnit_iff_isUnit_det _).mp (gram_isUnit D))

end Komorebi.LSM.UniformIntervalMoments
