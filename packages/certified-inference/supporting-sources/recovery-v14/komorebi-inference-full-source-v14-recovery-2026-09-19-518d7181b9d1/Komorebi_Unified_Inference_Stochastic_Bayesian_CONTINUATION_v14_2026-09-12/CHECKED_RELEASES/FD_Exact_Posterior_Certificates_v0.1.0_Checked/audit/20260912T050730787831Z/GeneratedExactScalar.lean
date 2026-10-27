import Komorebi.RationalPosteriorCertificate
import Mathlib.Data.Matrix.Notation

set_option autoImplicit false
set_option maxRecDepth 8192
set_option maxHeartbeats 800000
namespace Komorebi.ExactPosterior.GeneratedExactScalar
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

def candidate0 : RationalCandidate (Fin 1) (Fin 1) (Fin 1) (Fin 1) where
  gain := !![0]
  packetUpper := !![1]
  innovationUpper := 1

theorem candidate0_checked : checkCandidate model outputs inputs candidate0 = true := by decide

def candidate1 : RationalCandidate (Fin 1) (Fin 1) (Fin 1) (Fin 1) where
  gain := !![(49/100)]
  packetUpper := !![(1/2500)]
  innovationUpper := 1

theorem candidate1_checked : checkCandidate model outputs inputs candidate1 = true := by decide

theorem candidate1_tolerance : checkTolerance model candidate1 (1/20) = true := by decide
theorem candidate1_posterior_bound :
    wasserstein2 model.posterior (model.approximation candidate1.gain) ≤ ENNReal.ofReal ((1/20) : ℝ) := by
  exact checked_tolerance_bounds_posterior model outputs inputs candidate1 (1/20) candidate1_checked candidate1_tolerance

def candidate2 : RationalCandidate (Fin 1) (Fin 1) (Fin 1) (Fin 1) where
  gain := !![(2/5)]
  packetUpper := !![0]
  innovationUpper := 1

theorem candidate2_checked : checkCandidate model outputs inputs candidate2 = false := by decide

def selected := selectCandidates model outputs inputs candidate0 [candidate1, candidate2]
theorem selected_checked : checkCandidate model outputs inputs selected = true := by decide
theorem selected_score_nonincrease : candidateScore model selected ≤ candidateScore model candidate0 := by
  exact selectCandidates_score_le model outputs inputs candidate0 [candidate1, candidate2]

theorem selected_tolerance : checkTolerance model selected (1/20) = true := by decide
theorem selected_posterior_bound :
    wasserstein2 model.posterior (model.approximation selected.gain) ≤ ENNReal.ofReal ((1/20) : ℝ) := by
  exact checked_tolerance_bounds_posterior model outputs inputs selected (1/20) selected_checked selected_tolerance

end Komorebi.ExactPosterior.GeneratedExactScalar
