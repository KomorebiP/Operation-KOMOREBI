import Komorebi.RationalCertificateChecker
import Komorebi.GramNoiseFloor
import Komorebi.FDResidualPacketCertificate

noncomputable section
set_option autoImplicit false
namespace Komorebi.ExactPosterior
open Matrix MeasureTheory Komorebi.PacketEnergy Komorebi.FiniteDimensionalGaussianKalman

variable {ι κ υ ω : Type*}
variable [Fintype ι] [Fintype κ] [Fintype υ] [Fintype ω]
variable [DecidableEq ι] [DecidableEq κ]

/-- Rational coordinates embedded in the actual Euclidean Hilbert space. -/
def realVector {η : Type*} [Fintype η] (v : η → ℚ) : EuclideanSpace ℝ η :=
  WithLp.toLp 2 (fun i => (v i : ℝ))

@[simp] theorem realVector_apply {η : Type*} [Fintype η] (v : η → ℚ) (i : η) :
    realVector v i = (v i : ℝ) := rfl

theorem rationalVectorEnergy_cast {η : Type*} [Fintype η] (v : η → ℚ) :
    (rationalVectorEnergy v : ℝ) = ‖realVector v‖^2 := by
  rw [EuclideanSpace.real_norm_sq_eq]
  simp [rationalVectorEnergy, realVector]

namespace RationalModel

omit [Fintype κ] [Fintype ω] [DecidableEq ι] [DecidableEq κ] in
theorem prior_real_posSemidef (M : RationalModel ι κ υ ω) :
    (realMatrix M.prior).PosSemidef := by
  rw [prior, realMatrix_mul, realMatrix_transpose]
  exact gram_posSemidef _

omit [Fintype ι] [Fintype υ] [DecidableEq ι] in
theorem noise_real_posDef (M : RationalModel ι κ υ ω) (hs : 0 < M.noiseFloor) :
    (realMatrix M.noise).PosDef := by
  simp only [noise, realMatrix_add, realMatrix_mul, realMatrix_transpose,
    realMatrix_smul, realMatrix_one]
  exact gram_noise_posDef _ _ (by exact_mod_cast hs)

omit [Fintype ι] [Fintype υ] [DecidableEq ι] in
theorem noise_real_floor (M : RationalModel ι κ υ ω) :
    QuadraticLowerBound (realMatrix M.noise) (M.noiseFloor : ℝ) := by
  simp only [noise, realMatrix_add, realMatrix_mul, realMatrix_transpose,
    realMatrix_smul, realMatrix_one]
  exact gram_noise_floor _ _

omit [Fintype κ] [DecidableEq ι] in
@[simp] theorem real_innovation (M : RationalModel ι κ υ ω) :
    realMatrix M.innovation = innovationMatrix (realMatrix M.observationMatrix)
      (realMatrix M.prior) (realMatrix M.noise) := by
  simp only [innovation, innovationMatrix, realMatrix_add, realMatrix_mul, realMatrix_transpose]

omit [DecidableEq ι] in
@[simp] theorem real_residual (M : RationalModel ι κ υ ω) (B : Matrix ι κ ℚ) :
    realMatrix (M.residual B) = gainResidual (realMatrix M.observationMatrix)
      (realMatrix M.prior) (realMatrix M.noise) (realMatrix B) := by
  simp only [residual, gainResidual, realMatrix_sub, realMatrix_mul,
    realMatrix_transpose, real_innovation]

omit [Fintype υ] [Fintype ω] [DecidableEq κ] in
theorem real_innovationVector (M : RationalModel ι κ υ ω) :
    realVector M.innovationVector =
      realVector M.observation - matrixCLM (realMatrix M.observationMatrix) (realVector M.mean) := by
  ext i
  simp [realVector, innovationVector, matrixCLM_apply, rational_mulVec_cast]

/-- Explicit posterior version of the exact real model represented by rational inputs. -/
def posterior (M : RationalModel ι κ υ ω) : Measure (EuclideanSpace ℝ ι) :=
  fdPosteriorKernel (realMatrix M.observationMatrix) (realVector M.mean)
    (realMatrix M.prior) (realMatrix M.noise) (realVector M.observation)

/-- Joseph-form approximation for the exact rational candidate gain. -/
def approximation (M : RationalModel ι κ υ ω) (B : Matrix ι κ ℚ) : Measure (EuclideanSpace ℝ ι) :=
  gainPosteriorLaw (realMatrix M.observationMatrix) (realVector M.mean)
    (realMatrix M.prior) (realMatrix M.noise) (realMatrix B) (realVector M.observation)

end RationalModel
end Komorebi.ExactPosterior
