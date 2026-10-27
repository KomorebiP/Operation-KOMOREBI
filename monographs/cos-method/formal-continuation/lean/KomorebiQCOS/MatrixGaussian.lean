import KomorebiQCOS.SpectralGaussian
import Mathlib.Analysis.Matrix.Hermitian

/-!
# The existing finite matrix interface reaches the Gaussian spectral law

This module connects the unchanged finite Gram definitions to the Euclidean
operator used by the spectral reduction. It does not replace numerical
spectral inclusion with an assumption that computed eigenvalues are exact.
-/

namespace KomorebiQCOS
open MeasureTheory ProbabilityTheory
open scoped BigOperators

variable {Row Variant : Type*} [Fintype Row] [DecidableEq Row]

/-- The baseline finite quadratic statistic agrees with the Euclidean operator form. -/
theorem matrix_operatorQuadratic_eq (K : Matrix Row Row ℝ) (z : Row → ℝ) :
    operatorQuadratic K.toEuclideanLin (WithLp.toLp 2 z) = quadraticForm K z := by
  simp only [operatorQuadratic, EuclideanSpace.inner_eq_star_dotProduct,
    Matrix.ofLp_toLpLin, Matrix.toLin'_apply,
    quadraticForm, matrixAction, Matrix.mulVec, dotProduct, Pi.star_apply, star_trivial]
  apply Finset.sum_congr rfl
  intro i _
  exact mul_comm _ _

/-- The finite matrix statistic has the same actual law as its Euclidean realization. -/
theorem matrix_quadratic_gaussian_law (K : Matrix Row Row ℝ) :
    (standardGaussianProduct Row).map (quadraticForm K) =
      (stdGaussian (EuclideanSpace ℝ Row)).map (operatorQuadratic K.toEuclideanLin) := by
  rw [← map_pi_eq_stdGaussian,
    Measure.map_map (operatorQuadratic_measurable K.toEuclideanLin) (by fun_prop)]
  unfold standardGaussianProduct
  congr 1
  funext z
  exact (matrix_operatorQuadratic_eq K z).symm

/-- Exact symmetric-matrix reduction, including signed and zero eigenvalues. -/
theorem matrix_quadratic_spectral_law (K : Matrix Row Row ℝ) (hK : K.IsHermitian) :
    (standardGaussianProduct Row).map (quadraticForm K) =
      gaussianQuadraticLaw
        ((Matrix.isSymmetric_toEuclideanLin_iff.mpr hK).eigenvalues rfl) := by
  rw [matrix_quadratic_gaussian_law]
  exact symmetric_operatorQuadratic_law _ (Matrix.isSymmetric_toEuclideanLin_iff.mpr hK)

/-- The finite Gram entry function, explicitly typed as a matrix. -/
def gramMatrix (s : Finset Variant) (A : Row → Variant → ℝ) : Matrix Row Row ℝ :=
  gramEntry s A

omit [Fintype Row] [DecidableEq Row] in
/-- Symmetry of the original finite Gram matrix follows from its entries. -/
theorem gramEntry_isHermitian (s : Finset Variant) (A : Row → Variant → ℝ) :
    (gramMatrix s A).IsHermitian := by
  ext i j
  change star (gramEntry s A j i) = gramEntry s A i j
  rw [star_trivial, gramEntry_symm]

/-- The original streamed-factor representation reaches the spectral probability law. -/
theorem gram_quadratic_spectral_law (s : Finset Variant) (A : Row → Variant → ℝ) :
    (standardGaussianProduct Row).map (quadraticForm (gramEntry s A)) =
      gaussianQuadraticLaw
        ((Matrix.isSymmetric_toEuclideanLin_iff.mpr (gramEntry_isHermitian s A)).eigenvalues rfl) :=
  matrix_quadratic_spectral_law _ (gramEntry_isHermitian s A)

/-- Tail identity for the exact finite Gram form used by the original companion. -/
theorem gram_quadratic_spectral_tail (s : Finset Variant) (A : Row → Variant → ℝ) (q : ℝ) :
    tailProbability (standardGaussianProduct Row) (quadraticForm (gramEntry s A)) q =
      gaussianWeightedTail
        ((Matrix.isSymmetric_toEuclideanLin_iff.mpr (gramEntry_isHermitian s A)).eigenvalues rfl) q := by
  have hm : Measurable (quadraticForm (gramEntry s A)) :=
    measurable_quadraticForm_gram s A id (fun i => measurable_pi_apply i)
  calc
    tailProbability (standardGaussianProduct Row) (quadraticForm (gramEntry s A)) q =
        ((standardGaussianProduct Row).map (quadraticForm (gramEntry s A))).real (Set.Ici q) :=
      tailProbability_eq_map _ hm q
    _ = (gaussianQuadraticLaw
        ((Matrix.isSymmetric_toEuclideanLin_iff.mpr (gramEntry_isHermitian s A)).eigenvalues rfl)).real
          (Set.Ici q) := congrArg (fun ν : Measure ℝ => ν.real (Set.Ici q))
            (gram_quadratic_spectral_law s A)
    _ = _ := (gaussianWeightedTail_eq_law _ q).symm

/-- The existing exact Gram input, spectral bounds, analytic endpoint enclosures,
and an executable rational acceptance decision compose into one theorem. -/
theorem gram_quadratic_rational_acceptance (s : Finset Variant) (A : Row → Variant → ℝ)
    (lower upper : Fin (Module.finrank ℝ (EuclideanSpace ℝ Row)) → ℝ)
    (hl : ∀ i, lower i ≤
      (Matrix.isSymmetric_toEuclideanLin_iff.mpr (gramEntry_isHermitian s A)).eigenvalues rfl i)
    (hu : ∀ i,
      (Matrix.isSymmetric_toEuclideanLin_iff.mpr (gramEntry_isHermitian s A)).eigenvalues rfl i ≤ upper i)
    (q : ℝ) (L U tolerance : ℚ) (estimate : ℝ)
    (hL : (L : ℝ) ≤ gaussianWeightedTail lower q)
    (hU : gaussianWeightedTail upper q ≤ (U : ℝ))
    (he : Enclosed estimate (L : ℝ) (U : ℝ))
    (ha : acceptsRational L U tolerance = true) :
    0 < tailProbability (standardGaussianProduct Row) (quadraticForm (gramEntry s A)) q ∧
      |estimate - tailProbability (standardGaussianProduct Row) (quadraticForm (gramEntry s A)) q| /
        tailProbability (standardGaussianProduct Row) (quadraticForm (gramEntry s A)) q ≤
          (tolerance : ℝ) := by
  rw [gram_quadratic_spectral_tail]
  exact gaussianWeightedTail_rational_acceptance lower _ upper hl hu q L U tolerance
    estimate hL hU he ha

end KomorebiQCOS
