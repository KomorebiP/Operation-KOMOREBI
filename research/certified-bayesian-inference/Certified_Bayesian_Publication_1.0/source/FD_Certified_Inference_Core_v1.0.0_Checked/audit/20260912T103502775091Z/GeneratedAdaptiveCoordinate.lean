import Komorebi.AdaptivePacketOutput
import Komorebi.AdaptivePacketOrigin
import Komorebi.AdaptivePacketInvariants
import Komorebi.RationalSolverDecidable
import Mathlib.LinearAlgebra.Matrix.Notation

set_option autoImplicit false
set_option maxRecDepth 65536
set_option maxHeartbeats 8000000
namespace Komorebi.AdaptivePosterior.GeneratedAdaptiveCoordinate
open Komorebi.ExactPosterior Komorebi.RoundedPosterior Komorebi.PosteriorOutput Komorebi.QuadraticTransport

def model : RationalModel (Fin 2) (Fin 1) (Fin 2) (Fin 1) where
  observationMatrix := !![1, 1]
  priorFactor := !![2, 0; 0, 1]
  noiseFactor := !![0]
  noiseFloor := 1
  mean := ![0, 0]
  observation := ![1]
def outputs : Fin 2 → Matrix (Fin 2) (Fin 2) ℚ := ![!![1, 0; 0, 0], !![0, 0; 0, 1]]
def inputs : Fin 1 → Matrix (Fin 1) (Fin 1) ℚ := ![!![1]]
def initial : Matrix (Fin 2) (Fin 1) ℚ := !![0; 0]
def finalGain : Matrix (Fin 2) (Fin 1) ℚ := !![(228/343); (8/49)]
def certificate := roundedCandidate 12 model outputs inputs finalGain
theorem fuel_computed : adaptiveFuel model initial (1/20) 2 = 410093 := by decide +kernel
theorem iterate_computed : greedyGain model outputs 0 [0, 1] initial 5 = finalGain := by decide +kernel
theorem score_computed : candidateScore model certificate = (1525/1048576) := by decide +kernel
theorem adaptive_return : solveAdaptive model outputs inputs 0 [0, 1] (1/20) [4, 12] initial = some (12,certificate) := by decide +kernel
theorem posterior_tolerance : wasserstein2 model.posterior (model.approximation certificate.gain) ≤ ENNReal.ofReal (((1/20) : ℚ) : ℝ) :=
  adaptive_solver_return_bounds_posterior model outputs inputs 0 [0, 1] (1/20) [4, 12] initial 12 certificate adaptive_return
theorem selected_0 : selectPacket model outputs 0 [0, 1] (greedyGain model outputs 0 [0, 1] initial 0) = 0 := by decide +kernel
theorem selected_1 : selectPacket model outputs 0 [0, 1] (greedyGain model outputs 0 [0, 1] initial 1) = 1 := by decide +kernel
theorem selected_2 : selectPacket model outputs 0 [0, 1] (greedyGain model outputs 0 [0, 1] initial 2) = 0 := by decide +kernel
theorem selected_3 : selectPacket model outputs 0 [0, 1] (greedyGain model outputs 0 [0, 1] initial 3) = 1 := by decide +kernel
theorem selected_4 : selectPacket model outputs 0 [0, 1] (greedyGain model outputs 0 [0, 1] initial 4) = 0 := by decide +kernel
def outputArrays := represent model finalGain (1/1000)
theorem output_precision_computed : outputPrecision model finalGain (1/1000) = 32 := by decide +kernel
theorem mean_centers_computed : (fun i => (outputArrays.mean i).center) = ![(2854963683/4294967296), (350609575/2147483648)] := by decide +kernel
theorem mean_radii_computed : (fun i => (outputArrays.mean i).radius) = ![(1/4294967296), (1/4294967296)] := by decide +kernel
theorem covariance_centers_computed : (fun i j => (outputArrays.covariance i j).center) = !![(5726720411/4294967296), (-178946323/268435456); (-178946323/268435456), (1789718775/2147483648)] := by funext i j; fin_cases i <;> fin_cases j <;> decide +kernel
theorem covariance_radii_computed : (fun i j => (outputArrays.covariance i j).radius) = !![(1/536870912), (7/4294967296); (7/4294967296), (5/4294967296)] := by funext i j; fin_cases i <;> fin_cases j <;> decide +kernel
def outputResult : Result (Fin 2) (Fin 1) (Fin 2) (Fin 1) := ⟨12,certificate,outputPrecision model finalGain (1/1000),outputArrays⟩
theorem output_return : runAdaptive model outputs inputs 0 [0, 1] (1/20) (1/1000) [4, 12] initial = some outputResult := by
  simp only [runAdaptive, ite_eq_left (show (0 : ℚ) < (1/1000) by norm_num), adaptive_return]
  rfl
theorem output_valid : ResultValid model outputs inputs (1/20) (1/1000) outputResult :=
  runAdaptive_sound model outputs inputs 0 [0, 1] (1/20) (1/1000) [4, 12] initial outputResult output_return
end Komorebi.AdaptivePosterior.GeneratedAdaptiveCoordinate
