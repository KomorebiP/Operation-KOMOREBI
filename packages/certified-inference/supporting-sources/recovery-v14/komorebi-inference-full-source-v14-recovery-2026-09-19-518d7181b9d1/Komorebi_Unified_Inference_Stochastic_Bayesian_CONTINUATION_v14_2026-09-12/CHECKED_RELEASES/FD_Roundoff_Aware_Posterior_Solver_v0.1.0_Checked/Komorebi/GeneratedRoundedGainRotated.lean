import Komorebi.RoundedSolverPosterior
import Komorebi.RationalSolverDecidable
import Mathlib.LinearAlgebra.Matrix.Notation

set_option autoImplicit false
set_option maxRecDepth 65536
set_option maxHeartbeats 8000000
namespace Komorebi.RoundoffSolver.GeneratedRoundedGainRotated
open Komorebi.ExactPosterior Komorebi.RoundedPosterior Komorebi.QuadraticTransport

def model : RationalModel (Fin 2) (Fin 2) (Fin 1) (Fin 1) where
  observationMatrix := !![1, 0; 0, 1]
  priorFactor := !![1; 1]
  noiseFactor := !![0; 0]
  noiseFloor := 1
  mean := ![0, 0]
  observation := ![1, -1]

def outputs : Fin 2 → Matrix (Fin 2) (Fin 2) ℚ := ![!![(1/2), (1/2); (1/2), (1/2)], !![(1/2), (-1/2); (-1/2), (1/2)]]
def inputs : Fin 2 → Matrix (Fin 2) (Fin 2) ℚ := ![!![(1/2), (1/2); (1/2), (1/2)], !![(1/2), (-1/2); (-1/2), (1/2)]]
def initial : Matrix (Fin 2) (Fin 2) ℚ := !![0, 0; 0, 0]
def finalGain : Matrix (Fin 2) (Fin 2) ℚ := !![(1372190511463/4398046511104), (1372190511463/4398046511104); (1372190511463/4398046511104), (1372190511463/4398046511104)]
def certificate := roundedCandidate 12 model outputs inputs finalGain

theorem accuracy_computed : updateAccuracy model (1/4) = 21 := by decide +kernel
theorem fuel_computed : roundedFuel model initial (1/4) = 8534 := by decide +kernel
theorem rounded_iterate_computed : roundedGain model 21 initial 3 = finalGain := by decide +kernel
theorem score_computed : candidateScore model certificate = (215859/4194304) := by decide +kernel

theorem rounded_return :
    solveRounded model outputs inputs (1/4) [4, 12] initial = some (12,certificate) := by
  decide +kernel

theorem posterior_tolerance :
    wasserstein2 model.posterior (model.approximation certificate.gain) ≤
      ENNReal.ofReal (((1/4) : ℚ) : ℝ) := by
  exact rounded_solver_return_bounds_posterior model outputs inputs (1/4) [4, 12] initial
    12 certificate rounded_return

end Komorebi.RoundoffSolver.GeneratedRoundedGainRotated
