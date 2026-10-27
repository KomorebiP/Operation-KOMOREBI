import Komorebi.HybridPosteriorGuarantee
import Komorebi.RationalSolverDecidable
import Mathlib.LinearAlgebra.Matrix.Notation

set_option autoImplicit false
set_option maxRecDepth 32768
set_option maxHeartbeats 6000000
namespace Komorebi.RoundedPosterior.GeneratedHybridRotated
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
def finalGain : Matrix (Fin 2) (Fin 2) ℚ := !![(203/625), (203/625); (203/625), (203/625)]
def certificate := roundedCandidate 72 model outputs inputs finalGain

theorem precision_computed :
    sufficientPrecision model outputs inputs finalGain ((1/4)^2/4) = 72 := by
  decide +kernel

theorem exact_solver_return :
    solveGain model outputs inputs ((1/4)/2) initial =
      some (exactCandidate model outputs inputs finalGain) := by
  decide +kernel

theorem score_computed : candidateScore model certificate = (685078892498860742968979662193511853623/87112285931760246646623899502532662132736) := by
  decide +kernel

theorem hybrid_return :
    hybridSolve model outputs inputs (1/4) initial = some (72,certificate) := by
  decide +kernel

theorem posterior_tolerance :
    wasserstein2 model.posterior (model.approximation certificate.gain) ≤
      ENNReal.ofReal (((1/4) : ℚ) : ℝ) := by
  exact hybrid_return_bounds_posterior model outputs inputs (1/4) initial
    72 certificate hybrid_return

end Komorebi.RoundedPosterior.GeneratedHybridRotated
