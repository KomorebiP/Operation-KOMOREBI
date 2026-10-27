import Komorebi.PosteriorOutputSolver
import Komorebi.RoundedSolverPosterior
import Komorebi.RationalSolverDecidable
import Mathlib.LinearAlgebra.Matrix.Notation

set_option autoImplicit false
set_option maxRecDepth 65536
set_option maxHeartbeats 8000000
namespace Komorebi.RoundoffSolver.GeneratedOutputScalar
open Komorebi.ExactPosterior Komorebi.RoundedPosterior Komorebi.QuadraticTransport

def model : RationalModel (Fin 1) (Fin 1) (Fin 1) (Fin 1) where
  observationMatrix := !![1]
  priorFactor := !![1]
  noiseFactor := !![0]
  noiseFloor := 1
  mean := ![0]
  observation := ![1]

def outputs : Fin 1 → Matrix (Fin 1) (Fin 1) ℚ := ![!![1]]
def inputs : Fin 1 → Matrix (Fin 1) (Fin 1) ℚ := ![!![1]]
def initial : Matrix (Fin 1) (Fin 1) ℚ := !![0]
def finalGain : Matrix (Fin 1) (Fin 1) ℚ := !![(16967772033/34359738368)]
def certificate := roundedCandidate 12 model outputs inputs finalGain

theorem accuracy_computed : updateAccuracy model (1/20) = 20 := by decide +kernel
theorem fuel_computed : roundedFuel model initial (1/20) = 23040 := by decide +kernel
theorem rounded_iterate_computed : roundedGain model 20 initial 4 = finalGain := by decide +kernel
theorem score_computed : candidateScore model certificate = (729/2097152) := by decide +kernel

theorem rounded_return :
    solveRounded model outputs inputs (1/20) [4, 12] initial = some (12,certificate) := by
  decide +kernel

theorem posterior_tolerance :
    wasserstein2 model.posterior (model.approximation certificate.gain) ≤
      ENNReal.ofReal (((1/20) : ℚ) : ℝ) := by
  exact rounded_solver_return_bounds_posterior model outputs inputs (1/20) [4, 12] initial
    12 certificate rounded_return


open Komorebi.PosteriorOutput

def outputArrays := represent model finalGain (1/1000)
theorem output_precision_computed : outputPrecision model finalGain (1/1000) = 27 := by decide +kernel
theorem mean_centers_computed : (fun i => (outputArrays.mean i).center) = ![(66280359/134217728)] := by decide +kernel
theorem mean_radii_computed : (fun i => (outputArrays.mean i).radius) = ![(1/134217728)] := by decide +kernel
theorem covariance_centers_computed : (fun i j => (outputArrays.covariance i j).center) = !![(16779773/33554432)] := by funext i j; fin_cases i <;> fin_cases j <;> decide +kernel
theorem covariance_radii_computed : (fun i j => (outputArrays.covariance i j).radius) = !![(1/33554432)] := by funext i j; fin_cases i <;> fin_cases j <;> decide +kernel

def outputResult : Result (Fin 1) (Fin 1) (Fin 1) (Fin 1) :=
  ⟨12,certificate,outputPrecision model finalGain (1/1000),outputArrays⟩

theorem output_return : run model outputs inputs (1/20) (1/1000) [4, 12] initial = some outputResult := by
  simp only [run, ite_eq_left (show (0 : ℚ) < (1/1000) by norm_num), rounded_return]
  rfl

theorem output_valid : ResultValid model outputs inputs (1/20) (1/1000) outputResult :=
  run_sound model outputs inputs (1/20) (1/1000) [4, 12] initial outputResult output_return

end Komorebi.RoundoffSolver.GeneratedOutputScalar
