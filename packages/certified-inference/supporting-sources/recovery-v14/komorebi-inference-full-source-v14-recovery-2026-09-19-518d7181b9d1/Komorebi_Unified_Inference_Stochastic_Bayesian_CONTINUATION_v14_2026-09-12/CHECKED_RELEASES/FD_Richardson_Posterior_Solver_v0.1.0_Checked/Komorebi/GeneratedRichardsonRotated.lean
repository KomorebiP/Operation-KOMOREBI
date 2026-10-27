import Komorebi.RationalSolverPosterior
import Komorebi.RationalSolverDecidable
import Mathlib.LinearAlgebra.Matrix.Notation

set_option autoImplicit false
set_option maxRecDepth 16384
set_option maxHeartbeats 1200000
namespace Komorebi.ExactPosterior.GeneratedRichardsonRotated
open Komorebi.ExactPosterior Komorebi.QuadraticTransport

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
def finalGain : Matrix (Fin 2) (Fin 2) ℚ := !![(39/125), (39/125); (39/125), (39/125)]
def certificate := exactCandidate model outputs inputs finalGain

theorem returned_by_solver :
    solveGain model outputs inputs (1/4) initial = some certificate := by
  decide +kernel

theorem iterate_matches : model.solverGain initial 3 = finalGain := by
  decide +kernel

theorem posterior_tolerance :
    wasserstein2 model.posterior (model.approximation certificate.gain) ≤
      ENNReal.ofReal (((1/4) : ℚ) : ℝ) := by
  exact solver_return_bounds_posterior model outputs inputs (1/4) initial
    certificate returned_by_solver

end Komorebi.ExactPosterior.GeneratedRichardsonRotated
