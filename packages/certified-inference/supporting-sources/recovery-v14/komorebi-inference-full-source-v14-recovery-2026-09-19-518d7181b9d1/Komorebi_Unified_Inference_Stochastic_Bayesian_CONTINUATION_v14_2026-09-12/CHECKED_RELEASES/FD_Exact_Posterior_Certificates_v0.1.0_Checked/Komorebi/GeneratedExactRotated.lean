import Komorebi.RationalPosteriorCertificate
import Mathlib.LinearAlgebra.Matrix.Notation

set_option autoImplicit false
set_option maxRecDepth 8192
set_option maxHeartbeats 800000
namespace Komorebi.ExactPosterior.GeneratedExactRotated
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
  gain := !![0, 0; 0, 0]
  packetUpper := !![4, 0; 0, 0]
  innovationUpper := 2

theorem candidate0_checked : checkCandidate model outputs inputs candidate0 = true  := by decide +kernel

def candidate1 : RationalCandidate (Fin 2) (Fin 2) (Fin 2) (Fin 2) where
  gain := !![(5/16), (5/16); (5/16), (5/16)]
  packetUpper := !![(17/1024), (1/1024); (1/1024), (1/1024)]
  innovationUpper := 2

theorem candidate1_checked : checkCandidate model outputs inputs candidate1 = true  := by decide +kernel

theorem candidate1_tolerance : checkTolerance model candidate1 (1/4) = true  := by decide +kernel
theorem candidate1_posterior_bound :
    wasserstein2 model.posterior (model.approximation candidate1.gain) ≤ ENNReal.ofReal ((1/4) : ℝ) := by
  simpa using checked_tolerance_bounds_posterior model outputs inputs candidate1 (1/4) candidate1_checked candidate1_tolerance

def candidate2 : RationalCandidate (Fin 2) (Fin 2) (Fin 2) (Fin 2) where
  gain := !![0, 0; 0, 0]
  packetUpper := !![-1, -1; -1, -1]
  innovationUpper := 2

theorem candidate2_checked : checkCandidate model outputs inputs candidate2 = false  := by decide +kernel

def candidate3 : RationalCandidate (Fin 2) (Fin 2) (Fin 2) (Fin 2) where
  gain := !![2, 2; 2, 2]
  packetUpper := !![100, 0; 0, 0]
  innovationUpper := 2

theorem candidate3_checked : checkCandidate model outputs inputs candidate3 = true  := by decide +kernel

def selected := selectCandidates model outputs inputs candidate0 [candidate1, candidate2, candidate3]
theorem selected_checked : checkCandidate model outputs inputs selected = true  := by decide +kernel
theorem selected_score_nonincrease : candidateScore model selected ≤ candidateScore model candidate0 := by
  exact selectCandidates_score_le model outputs inputs candidate0 [candidate1, candidate2, candidate3]

theorem selected_tolerance : checkTolerance model selected (1/4) = true  := by decide +kernel
theorem selected_posterior_bound :
    wasserstein2 model.posterior (model.approximation selected.gain) ≤ ENNReal.ofReal ((1/4) : ℝ) := by
  simpa using checked_tolerance_bounds_posterior model outputs inputs selected (1/4) selected_checked selected_tolerance

end Komorebi.ExactPosterior.GeneratedExactRotated
