import Komorebi.RoundedPrecisionSearch
import Mathlib.LinearAlgebra.Matrix.Notation

set_option autoImplicit false
set_option maxRecDepth 16384
set_option maxHeartbeats 4000000
namespace Komorebi.RoundedPosterior.GeneratedRoundedScalar
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
def gain : Matrix (Fin 1) (Fin 1) ℚ := !![(1025/2048)]

theorem setup_valid : checkSetup model outputs inputs = true := by decide +kernel

def candidate0 := roundedCandidate 4 model outputs inputs gain
theorem score0_computed : candidateScore model candidate0 = (1/32) := by decide +kernel
theorem tolerance0_computed : checkTolerance model candidate0 (1/500) = false := by decide +kernel

def candidate1 := roundedCandidate 12 model outputs inputs gain
theorem score1_computed : candidateScore model candidate1 = (1/524288) := by decide +kernel
theorem tolerance1_computed : checkTolerance model candidate1 (1/500) = true := by decide +kernel

theorem posterior1_bound : wasserstein2 model.posterior (model.approximation gain) ≤ ENNReal.ofReal ((1/500) : ℝ) := by
  have hs := (checkSetup_eq_true model outputs inputs).mp setup_valid
  simpa using rounded_tolerance_bounds_posterior 12 model outputs inputs gain (1/500) hs.1 hs.2.1 hs.2.2 tolerance1_computed

theorem successful_return : certifyRounded 12 model outputs inputs gain (1/500) = some candidate1 := by
  rw [certifyRounded, if_pos setup_valid]
  change (if checkTolerance model candidate1 (1/500) then some candidate1 else none) = some candidate1
  rw [if_pos tolerance1_computed]

end Komorebi.RoundedPosterior.GeneratedRoundedScalar
