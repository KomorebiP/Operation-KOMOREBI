import Mathlib.Probability.Distributions.Gaussian.Real
import Mathlib.Probability.Kernel.Posterior
import Komorebi.GeneralScalarGaussianConditioning
import Komorebi.BayesianMultiscaleKalmanPosteriorPerturbation

noncomputable section
set_option autoImplicit false

namespace Komorebi.ScalarGaussianPosteriorPerturbationBridge

open Komorebi.GeneralScalarGaussianBayes
open Komorebi.BayesianPosteriorPerturb
open MeasureTheory ProbabilityTheory
open scoped ENNReal NNReal

/-- Multiplication by a real scalar as a bounded operator on the one-dimensional real Hilbert space. -/
def scalarOp (a : ℝ) : ℝ →L[ℝ] ℝ := a • ContinuousLinearMap.id ℝ ℝ

@[simp] theorem scalarOp_apply (a x : ℝ) : scalarOp a x = a * x := by
  simp [scalarOp]

@[simp] theorem scalarOp_adjoint (a : ℝ) : (scalarOp a).adjoint = scalarOp a := by
  simp only [scalarOp, map_smul]
  rw [ContinuousLinearMap.adjoint_id]

@[simp] theorem scalarOp_comp (a b : ℝ) :
    (scalarOp a).comp (scalarOp b) = scalarOp (a * b) := by
  apply ContinuousLinearMap.ext
  intro x
  simp [scalarOp]
  ring

@[simp] theorem scalarOp_add (a b : ℝ) :
    scalarOp a + scalarOp b = scalarOp (a + b) := by
  simp [scalarOp, add_smul]

@[simp] theorem scalarOp_sub (a b : ℝ) :
    scalarOp a - scalarOp b = scalarOp (a - b) := by
  exact (sub_smul a b (ContinuousLinearMap.id ℝ ℝ)).symm

@[simp] theorem scalarOp_one : scalarOp 1 = ContinuousLinearMap.id ℝ ℝ := by
  simp [scalarOp]

/-- Real innovation variance coefficient corresponding to `innovationVar`. -/
def innovationReal (h : ℝ) (p r : NNReal) : ℝ :=
  h^2 * (p : ℝ) + (r : ℝ)

@[simp] theorem innovationReal_eq_coe (h : ℝ) (p r : NNReal) :
    innovationReal h p r = (innovationVar h p r : ℝ) := by
  simp [innovationReal, coe_innovationVar]

/-- Scalar specialization of the coordinate-free innovation covariance. -/
theorem kalmanInnovationOp_scalar (h : ℝ) (p r : NNReal) :
    kalmanInnovationOp (scalarOp h) (scalarOp (p : ℝ)) (scalarOp (r : ℝ)) =
      scalarOp (innovationReal h p r) := by
  apply ContinuousLinearMap.ext
  intro x
  simp [kalmanInnovationOp, innovationReal]
  left
  ring

/-- The reciprocal innovation scalar is an exact inverse operator when `r>0`. -/
theorem innovationInverse_scalar
    (h : ℝ) (p r : NNReal) (hr : r ≠ 0) :
    (scalarOp (1 / innovationReal h p r)).comp
        (kalmanInnovationOp (scalarOp h) (scalarOp (p : ℝ)) (scalarOp (r : ℝ))) =
      ContinuousLinearMap.id ℝ ℝ := by
  rw [kalmanInnovationOp_scalar]
  rw [scalarOp_comp]
  have hSnn : innovationVar h p r ≠ 0 := innovationVar_ne_zero h p r hr
  have hS : innovationReal h p r ≠ 0 := by
    simpa [innovationReal_eq_coe] using NNReal.coe_ne_zero.mpr hSnn
  have hsimp : (1 / innovationReal h p r) * innovationReal h p r = 1 := by
    exact one_div_mul_cancel hS
  rw [hsimp, scalarOp_one]

/-- The same reciprocal is also a right inverse; this is useful for the second model in the
checked perturbation theorem, whose inverse hypothesis is oriented oppositely. -/
theorem innovationInverse_scalar_right
    (h : ℝ) (p r : NNReal) (hr : r ≠ 0) :
    (kalmanInnovationOp (scalarOp h) (scalarOp (p : ℝ)) (scalarOp (r : ℝ))).comp
        (scalarOp (1 / innovationReal h p r)) =
      ContinuousLinearMap.id ℝ ℝ := by
  rw [kalmanInnovationOp_scalar]
  rw [scalarOp_comp]
  have hSnn : innovationVar h p r ≠ 0 := innovationVar_ne_zero h p r hr
  have hS : innovationReal h p r ≠ 0 := by
    simpa [innovationReal_eq_coe] using NNReal.coe_ne_zero.mpr hSnn
  have hsimp : innovationReal h p r * (1 / innovationReal h p r) = 1 := by
    exact mul_one_div_cancel hS
  rw [hsimp, scalarOp_one]

/-- Scalar specialization of the coordinate-free Kalman gain. -/
theorem kalmanGainOp_scalar
    (h : ℝ) (p r : NNReal) :
    kalmanGainOp (scalarOp (p : ℝ)) (scalarOp h)
        (scalarOp (1 / innovationReal h p r)) =
      scalarOp (kalmanGain h p r) := by
  apply ContinuousLinearMap.ext
  intro x
  simp [kalmanGainOp, kalmanGain, innovationReal]
  left
  ring

/-- The coordinate-free posterior mean update is exactly the Gaussian posterior mean parameter. -/
theorem kalmanPosteriorMean_scalar
    (h m y : ℝ) (p r : NNReal) :
    kalmanPosteriorMean
        (kalmanGainOp (scalarOp (p : ℝ)) (scalarOp h)
          (scalarOp (1 / innovationReal h p r)))
        (scalarOp h) m y = posteriorMean h m y p r := by
  rw [kalmanGainOp_scalar]
  simp [kalmanPosteriorMean, posteriorMean]

/-- Coercion of the Gaussian posterior variance to the real coefficient used by scalar operators. -/
theorem coe_posteriorVar
    (h : ℝ) (p r : NNReal) :
    (posteriorVar h p r : ℝ) =
      (p : ℝ) * (r : ℝ) / innovationReal h p r := by
  simp only [posteriorVar, NNReal.coe_div, NNReal.coe_mul, coe_innovationVar, innovationReal]

/-- Scalar Joseph covariance identity: the coordinate-free Joseph update has exactly the
variance parameter of the Gaussian conditional posterior. -/
theorem josephPosteriorCov_scalar
    (h : ℝ) (p r : NNReal) (hr : r ≠ 0) :
    josephPosteriorCov
        (kalmanGainOp (scalarOp (p : ℝ)) (scalarOp h)
          (scalarOp (1 / innovationReal h p r)))
        (scalarOp h) (scalarOp (p : ℝ)) (scalarOp (r : ℝ)) =
      scalarOp (posteriorVar h p r : ℝ) := by
  rw [kalmanGainOp_scalar]
  apply ContinuousLinearMap.ext
  intro x
  simp [josephPosteriorCov, kalmanClosedLoop, coe_posteriorVar,
    kalmanGain, innovationReal]
  have hSnn : innovationVar h p r ≠ 0 := innovationVar_ne_zero h p r hr
  have hS : h ^ 2 * (p : ℝ) + (r : ℝ) ≠ 0 := by
    simpa [coe_innovationVar] using NNReal.coe_ne_zero.mpr hSnn
  rw [ContinuousLinearMap.adjoint_id]
  field_simp [hS]
  simp only [ContinuousLinearMap.id_apply]
  ring



/-- The posterior covariance-error operator used by the checked multiscale theorem is,
in the scalar linear-Gaussian specialization, exactly multiplication by the difference
of the two Gaussian conditional posterior variance parameters. -/
theorem posteriorCovErrorOp_scalar_semantic
    (h h0 : ℝ) (p p0 r r0 : NNReal) (hr : r ≠ 0) (hr0 : r0 ≠ 0) :
    posteriorCovErrorOp
        (kalmanGainOp (scalarOp (p : ℝ)) (scalarOp h)
          (scalarOp (1 / innovationReal h p r)))
        (kalmanGainOp (scalarOp (p0 : ℝ)) (scalarOp h0)
          (scalarOp (1 / innovationReal h0 p0 r0)))
        (scalarOp h) (scalarOp h0)
        (scalarOp (p : ℝ)) (scalarOp (p0 : ℝ))
        (scalarOp (r : ℝ)) (scalarOp (r0 : ℝ)) =
      scalarOp ((posteriorVar h p r : ℝ) - (posteriorVar h0 p0 r0 : ℝ)) := by
  unfold posteriorCovErrorOp
  rw [josephPosteriorCov_scalar h p r hr, josephPosteriorCov_scalar h0 p0 r0 hr0]
  exact scalarOp_sub _ _

/-- End-to-end posterior-mean perturbation bound, now stated directly on the Gaussian
conditional posterior means.  Its right-hand side is exactly the primitive-residual
budget from the already checked coordinate-free Kalman theorem. -/
theorem gaussianPosteriorMean_sub_norm_le_residual_budget
    (h h0 m m0 y y0 : ℝ) (p p0 r r0 : NNReal)
    (hr : r ≠ 0) (hr0 : r0 ≠ 0) :
    let H := scalarOp h
    let H0 := scalarOp h0
    let P := scalarOp (p : ℝ)
    let P0 := scalarOp (p0 : ℝ)
    let R := scalarOp (r : ℝ)
    let R0 := scalarOp (r0 : ℝ)
    let Sinv := scalarOp (1 / innovationReal h p r)
    let Sinv0 := scalarOp (1 / innovationReal h0 p0 r0)
    let K0 := kalmanGainOp P0 H0 Sinv0
    let gB := gainPerturbBudget H H0 P P0 R R0 Sinv Sinv0
    ‖posteriorMean h m y p r - posteriorMean h0 m0 y0 p0 r0‖ ≤
      ‖m - m0‖ +
      gB * ‖y - H m‖ +
      ‖K0‖ * (‖y - y0‖ + ‖H - H0‖ * ‖m‖ + ‖H0‖ * ‖m - m0‖) := by
  dsimp only
  have hb := kalmanPosteriorMean_sub_norm_le_residual_budget
    (H := scalarOp h) (H0 := scalarOp h0)
    (P := scalarOp (p : ℝ)) (P0 := scalarOp (p0 : ℝ))
    (R := scalarOp (r : ℝ)) (R0 := scalarOp (r0 : ℝ))
    (Sinv := scalarOp (1 / innovationReal h p r))
    (Sinv0 := scalarOp (1 / innovationReal h0 p0 r0))
    (m := m) (m0 := m0) (y := y) (y0 := y0)
    (innovationInverse_scalar h p r hr)
    (innovationInverse_scalar_right h0 p0 r0 hr0)
  dsimp only at hb
  rw [kalmanPosteriorMean_scalar h m y p r,
      kalmanPosteriorMean_scalar h0 m0 y0 p0 r0] at hb
  exact hb

/-- End-to-end posterior-covariance perturbation bound, now stated on the actual
scalar Gaussian posterior variance coefficients.  The left-hand side is precisely
the semantic posterior covariance error; the right-hand side is the checked primitive
residual/conditioning budget. -/
theorem gaussianPosteriorVar_sub_norm_le_residual_budget
    (h h0 : ℝ) (p p0 r r0 : NNReal)
    (hr : r ≠ 0) (hr0 : r0 ≠ 0) :
    let H := scalarOp h
    let H0 := scalarOp h0
    let P := scalarOp (p : ℝ)
    let P0 := scalarOp (p0 : ℝ)
    let R := scalarOp (r : ℝ)
    let R0 := scalarOp (r0 : ℝ)
    let Sinv := scalarOp (1 / innovationReal h p r)
    let Sinv0 := scalarOp (1 / innovationReal h0 p0 r0)
    let K := kalmanGainOp P H Sinv
    let K0 := kalmanGainOp P0 H0 Sinv0
    let gB := gainPerturbBudget H H0 P P0 R R0 Sinv Sinv0
    let aB := closedLoopPerturbBudget K0 H H0 gB
    ‖scalarOp ((posteriorVar h p r : ℝ) - (posteriorVar h0 p0 r0 : ℝ))‖ ≤
      posteriorCovPerturbBudget K K0 H H0 P P0 R R0 gB aB := by
  dsimp only
  have hb := josephPosteriorCov_sub_norm_le_residual_budget
    (H := scalarOp h) (H0 := scalarOp h0)
    (P := scalarOp (p : ℝ)) (P0 := scalarOp (p0 : ℝ))
    (R := scalarOp (r : ℝ)) (R0 := scalarOp (r0 : ℝ))
    (Sinv := scalarOp (1 / innovationReal h p r))
    (Sinv0 := scalarOp (1 / innovationReal h0 p0 r0))
    (innovationInverse_scalar h p r hr)
    (innovationInverse_scalar_right h0 p0 r0 hr0)
  dsimp only at hb
  rw [josephPosteriorCov_scalar h p r hr,
      josephPosteriorCov_scalar h0 p0 r0 hr0] at hb
  simpa using hb

open scoped ProbabilityTheory

/-- **Semantic closure of the scalar Kalman perturbation variables.**  Under positive prior
and observation-noise variances, the exact coordinate-free `K/H/P/R` update used by the
checked perturbation theorem has the same mean and covariance parameters as the explicit
Gaussian conditional posterior.  That Gaussian kernel is a version of Mathlib's canonical
posterior (evidence-a.e.) and is also the normalized Bayes measure for every fixed `y`.

This theorem closes the semantic gap for scalar linear observations only. -/
theorem coordinateFree_scalar_update_is_actual_bayesian_posterior
    (h m : ℝ) (p r : NNReal) (hp : p ≠ 0) (hr : r ≠ 0) :
    let H := scalarOp h
    let P := scalarOp (p : ℝ)
    let R := scalarOp (r : ℝ)
    let Sinv := scalarOp (1 / innovationReal h p r)
    let K := kalmanGainOp P H Sinv
    (∀ y : ℝ, kalmanPosteriorMean K H m y = posteriorMean h m y p r) ∧
    josephPosteriorCov K H P R = scalarOp (posteriorVar h p r : ℝ) ∧
    (fun y => kalmanPosteriorKernel h m p r y) =ᵐ[gaussianReal (h*m) (innovationVar h p r)]
      (fun y => ProbabilityTheory.posterior (linearObservationKernel h r)
        (gaussianReal m p) y) ∧
    (∀ y : ℝ,
      volume.withDensity (fun x : ℝ =>
        (gaussianPDF m p x * gaussianPDF (h*x) r y) /
          gaussianPDF (h*m) (innovationVar h p r) y) =
        kalmanPosteriorKernel h m p r y) := by
  dsimp only
  refine ⟨?_, josephPosteriorCov_scalar h p r hr, ?_, ?_⟩
  · intro y
    exact kalmanPosteriorMean_scalar h m y p r
  · exact kalmanPosterior_ae_eq_canonicalPosterior h m p r hp hr
  · intro y
    exact normalized_bayes_measure_eq_kalman h m y p r hp hr

end Komorebi.ScalarGaussianPosteriorPerturbationBridge
