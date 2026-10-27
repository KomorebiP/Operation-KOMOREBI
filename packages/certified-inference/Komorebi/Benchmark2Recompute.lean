import Komorebi.RationalPosteriorCertificate
import Mathlib.LinearAlgebra.Matrix.Notation

set_option autoImplicit false
set_option maxRecDepth 65536
set_option maxHeartbeats 8000000
namespace Komorebi.ExactPosterior.Benchmark2Recompute
open Komorebi.ExactPosterior Komorebi.QuadraticTransport

def model : RationalModel (Fin 4) (Fin 2) (Fin 1) (Fin 1) where
  observationMatrix := !![(-1/3), 0, (1/3), (-1/3); 0, (1/3), (-1/3), 0]
  priorFactor := !![1; 1; 0; 0]
  noiseFactor := !![0; 0]
  noiseFloor := 1
  mean := ![0, 0, 0, 0]
  observation := ![(1/2), (-1/2)]

def outputs : Fin 4 → Matrix (Fin 4) (Fin 4) ℚ := ![!![1, 0, 0, 0; 0, 0, 0, 0; 0, 0, 0, 0; 0, 0, 0, 0], !![0, 0, 0, 0; 0, 1, 0, 0; 0, 0, 0, 0; 0, 0, 0, 0], !![0, 0, 0, 0; 0, 0, 0, 0; 0, 0, 1, 0; 0, 0, 0, 0], !![0, 0, 0, 0; 0, 0, 0, 0; 0, 0, 0, 0; 0, 0, 0, 1]]
def inputs : Fin 1 → Matrix (Fin 2) (Fin 2) ℚ := ![!![1, 0; 0, 1]]

def candidate0 : RationalCandidate (Fin 4) (Fin 2) (Fin 4) (Fin 1) where
  gain := !![(-164265/707281), (164265/707281); (-164265/707281), (164265/707281); 0, 0; 0, 0]
  packetUpper := !![(86117/16777216); (86117/16777216); 0; 0]
  innovationUpper := (1/2)

theorem candidate0_checked : checkCandidate model outputs inputs candidate0 = true  := by decide +kernel

theorem candidate0_tolerance : checkTolerance model candidate0 (1/4) = true  := by decide +kernel
theorem candidate0_posterior_bound :
    wasserstein2 model.posterior (model.approximation candidate0.gain) ≤ ENNReal.ofReal ((1/4) : ℝ) := by
  simpa using checked_tolerance_bounds_posterior model outputs inputs candidate0 (1/4) candidate0_checked candidate0_tolerance

end Komorebi.ExactPosterior.Benchmark2Recompute
