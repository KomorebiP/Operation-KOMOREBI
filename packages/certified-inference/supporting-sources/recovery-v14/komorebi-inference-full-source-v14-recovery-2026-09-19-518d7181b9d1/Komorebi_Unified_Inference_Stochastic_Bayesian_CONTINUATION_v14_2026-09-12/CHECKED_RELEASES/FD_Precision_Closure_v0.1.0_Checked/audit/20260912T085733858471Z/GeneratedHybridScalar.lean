import Komorebi.HybridPosteriorGuarantee
import Komorebi.RationalSolverDecidable
import Mathlib.LinearAlgebra.Matrix.Notation

set_option autoImplicit false
set_option maxRecDepth 32768
set_option maxHeartbeats 6000000
namespace Komorebi.RoundedPosterior.GeneratedHybridScalar
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
def certificate := roundedCandidate 61 model outputs inputs finalGain

theorem precision_computed :
    sufficientPrecision model outputs inputs finalGain ((1/20)^2/4) = 61 := by
  decide +kernel

theorem exact_solver_return :
    solveGain model outputs inputs ((1/20)/2) initial =
      some (exactCandidate model outputs inputs finalGain) := by
  decide +kernel

theorem score_computed : candidateScore model certificate = (50648833858593053607545418504129/166153499473114484112975882535043072) := by
  decide +kernel

theorem hybrid_return :
    hybridSolve model outputs inputs (1/20) initial = some (61,certificate) := by
  decide +kernel

theorem posterior_tolerance :
    wasserstein2 model.posterior (model.approximation certificate.gain) ≤
      ENNReal.ofReal (((1/20) : ℚ) : ℝ) := by
  exact hybrid_return_bounds_posterior model outputs inputs (1/20) initial
    61 certificate hybrid_return

end Komorebi.RoundedPosterior.GeneratedHybridScalar
