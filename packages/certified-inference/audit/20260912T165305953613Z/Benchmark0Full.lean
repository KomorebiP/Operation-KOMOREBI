import Komorebi.RationalPosteriorCertificate
import Mathlib.LinearAlgebra.Matrix.Notation

set_option autoImplicit false
set_option maxRecDepth 65536
set_option maxHeartbeats 8000000
namespace Komorebi.ExactPosterior.Benchmark0Full
open Komorebi.ExactPosterior Komorebi.QuadraticTransport

def model : RationalModel (Fin 2) (Fin 1) (Fin 2) (Fin 1) where
  observationMatrix := !![1, 1]
  priorFactor := !![2, 0; 0, 1]
  noiseFactor := !![0]
  noiseFloor := 1
  mean := ![0, 0]
  observation := ![1]

def outputs : Fin 2 → Matrix (Fin 2) (Fin 2) ℚ := ![!![1, 0; 0, 0], !![0, 0; 0, 1]]
def inputs : Fin 1 → Matrix (Fin 1) (Fin 1) ℚ := ![!![1]]

def candidate0 : RationalCandidate (Fin 2) (Fin 1) (Fin 2) (Fin 1) where
  gain := !![(228/343); (57/343)]
  packetUpper := !![(841/4194304); (121/4194304)]
  innovationUpper := 1

theorem candidate0_checked : checkCandidate model outputs inputs candidate0 = true  := by decide +kernel

theorem candidate0_tolerance : checkTolerance model candidate0 (1/20) = true  := by decide +kernel
theorem candidate0_posterior_bound :
    wasserstein2 model.posterior (model.approximation candidate0.gain) ≤ ENNReal.ofReal ((1/20) : ℝ) := by
  simpa using checked_tolerance_bounds_posterior model outputs inputs candidate0 (1/20) candidate0_checked candidate0_tolerance

end Komorebi.ExactPosterior.Benchmark0Full
