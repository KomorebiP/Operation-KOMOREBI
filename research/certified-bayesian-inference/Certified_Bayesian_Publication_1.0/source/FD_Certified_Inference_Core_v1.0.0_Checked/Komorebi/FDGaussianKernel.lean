import Komorebi.FDGaussianTransport
import Mathlib.Probability.Kernel.Posterior

noncomputable section
set_option autoImplicit false
namespace Komorebi.FiniteDimensionalGaussianKalman
open Matrix ProbabilityTheory MeasureTheory
open scoped RealInnerProductSpace Matrix

variable {ι κ : Type*} [Fintype ι] [Fintype κ] [DecidableEq ι] [DecidableEq κ]

/-- The genuine affine Gaussian observation kernel, not an algebraic surrogate. -/
def gaussianAffineKernel (A : Matrix κ ι ℝ) (c : EuclideanSpace ℝ κ)
    (R : Matrix κ κ ℝ) : Kernel (EuclideanSpace ℝ ι) (EuclideanSpace ℝ κ) :=
  ⟨fun x => multivariateGaussian (c + matrixCLM A x) R,
    by
      have hpair : Measurable (fun x : EuclideanSpace ℝ ι =>
          (c + matrixCLM A x, R)) := by fun_prop
      exact measurable_multivariateGaussian.comp hpair⟩

@[simp] theorem gaussianAffineKernel_apply
    (A : Matrix κ ι ℝ) (c : EuclideanSpace ℝ κ) (R : Matrix κ κ ℝ)
    (x : EuclideanSpace ℝ ι) :
    gaussianAffineKernel A c R x = multivariateGaussian (c + matrixCLM A x) R := rfl

instance gaussianAffineKernel_isMarkov
    (A : Matrix κ ι ℝ) (c : EuclideanSpace ℝ κ) (R : Matrix κ κ ℝ) :
    IsMarkovKernel (gaussianAffineKernel A c R) := by
  constructor
  intro x
  change IsProbabilityMeasure (multivariateGaussian (c + matrixCLM A x) R)
  infer_instance

/-- Prior/likelihood composition is exactly independent-noise generation. -/
theorem compProd_gaussianAffineKernel
    (μ : Measure (EuclideanSpace ℝ ι)) [SFinite μ]
    (A : Matrix κ ι ℝ) (c : EuclideanSpace ℝ κ) (R : Matrix κ κ ℝ)
    (hR : R.PosSemidef) :
    μ ⊗ₘ gaussianAffineKernel A c R =
      (μ.prod (multivariateGaussian 0 R)).map
        (fun z => (z.1, c + matrixCLM A z.1 + z.2)) := by
  have hgen : Measurable (fun z : EuclideanSpace ℝ ι × EuclideanSpace ℝ κ =>
      (z.1, c + matrixCLM A z.1 + z.2)) := by fun_prop
  ext s hs
  rw [Measure.compProd_apply hs, Measure.map_apply hgen hs,
    Measure.prod_apply (hs.preimage hgen)]
  apply lintegral_congr
  intro x
  rw [gaussianAffineKernel_apply]
  have hshift : (multivariateGaussian 0 R).map
      (fun z => (c + matrixCLM A x) + z) =
        multivariateGaussian (c + matrixCLM A x) R := by
    simpa only [add_zero] using
      multivariateGaussian_map_const_add (c + matrixCLM A x) 0 R hR
  rw [← hshift, Measure.map_apply (by fun_prop) (hs.preimage (by fun_prop))]
  rfl

end Komorebi.FiniteDimensionalGaussianKalman
