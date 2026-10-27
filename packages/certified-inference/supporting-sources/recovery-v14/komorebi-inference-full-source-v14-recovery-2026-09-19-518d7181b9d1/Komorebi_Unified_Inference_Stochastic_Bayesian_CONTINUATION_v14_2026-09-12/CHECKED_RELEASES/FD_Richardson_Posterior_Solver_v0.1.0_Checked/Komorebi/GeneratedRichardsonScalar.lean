import Komorebi.RationalSolverPosterior
import Komorebi.RationalSolverDecidable
import Mathlib.LinearAlgebra.Matrix.Notation

set_option autoImplicit false
set_option maxRecDepth 16384
set_option maxHeartbeats 1200000
namespace Komorebi.ExactPosterior.GeneratedRichardsonScalar
open Komorebi.ExactPosterior Komorebi.QuadraticTransport

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
def finalGain : Matrix (Fin 1) (Fin 1) ℚ := !![(40/81)]
def certificate := exactCandidate model outputs inputs finalGain

theorem returned_by_solver :
    solveGain model outputs inputs (1/20) initial = some certificate := by
  decide +kernel

theorem iterate_matches : model.solverGain initial 4 = finalGain := by
  decide +kernel

theorem posterior_tolerance :
    wasserstein2 model.posterior (model.approximation certificate.gain) ≤
      ENNReal.ofReal (((1/20) : ℚ) : ℝ) := by
  exact solver_return_bounds_posterior model outputs inputs (1/20) initial
    certificate returned_by_solver

end Komorebi.ExactPosterior.GeneratedRichardsonScalar
