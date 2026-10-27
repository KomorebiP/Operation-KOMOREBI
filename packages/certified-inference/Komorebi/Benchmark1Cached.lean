import Komorebi.RationalPosteriorCertificate
import Mathlib.LinearAlgebra.Matrix.Notation

set_option autoImplicit false
set_option maxRecDepth 65536
set_option maxHeartbeats 8000000
namespace Komorebi.ExactPosterior.Benchmark1Cached
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

def candidate0 : RationalCandidate (Fin 2) (Fin 2) (Fin 2) (Fin 2) where
  gain := !![(203/625), (203/625); (203/625), (203/625)]
  packetUpper := !![(3025/1048576), (1/262144); (1/262144), (1/262144)]
  innovationUpper := 2

theorem candidate0_checked : checkCandidate model outputs inputs candidate0 = true  := by decide +kernel

theorem candidate0_tolerance : checkTolerance model candidate0 (1/4) = true  := by decide +kernel
theorem candidate0_posterior_bound :
    wasserstein2 model.posterior (model.approximation candidate0.gain) ≤ ENNReal.ofReal ((1/4) : ℝ) := by
  simpa using checked_tolerance_bounds_posterior model outputs inputs candidate0 (1/4) candidate0_checked candidate0_tolerance

end Komorebi.ExactPosterior.Benchmark1Cached
