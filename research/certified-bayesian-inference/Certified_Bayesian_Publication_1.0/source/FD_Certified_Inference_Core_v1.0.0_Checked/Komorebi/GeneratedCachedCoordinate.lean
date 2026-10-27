import Komorebi.CachedPacketOutput
import Komorebi.AdaptivePacketOutput
import Komorebi.AdaptivePacketOrigin
import Komorebi.AdaptivePacketInvariants
import Komorebi.RationalSolverDecidable
import Mathlib.LinearAlgebra.Matrix.Notation

set_option autoImplicit false
set_option maxRecDepth 65536
set_option maxHeartbeats 8000000
namespace Komorebi.CachedPosterior.GeneratedCachedCoordinate
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
def finalGain : Matrix (Fin 2) (Fin 1) ℚ := !![(228/343); (57/343)]
def certificate := roundedCandidate 12 model outputs inputs finalGain
def initialCache := initialState model outputs initial
def finalCache := trajectory (prepare model) 0 [0, 1] initialCache 6
theorem fuel_computed : Komorebi.AdaptivePosterior.adaptiveFuel model initial (1/20) 2 = 410093 := by decide +kernel
theorem gain_computed : finalCache.gain = finalGain := by decide +kernel
theorem exact_score_computed : score (prepare model) finalCache = (34/117649) := by decide +kernel
theorem rounded_score_computed : candidateScore model certificate = (481/1048576) := by decide +kernel
theorem cached_return : solveCached model outputs inputs 0 [0, 1] (1/20) [4, 12] initial = some (12,certificate) := by decide +kernel
theorem selected_0 : chosen 0 [0, 1] (trajectory (prepare model) 0 [0, 1] initialCache 0) = 0 := by decide +kernel
theorem selected_1 : chosen 0 [0, 1] (trajectory (prepare model) 0 [0, 1] initialCache 1) = 1 := by decide +kernel
theorem selected_2 : chosen 0 [0, 1] (trajectory (prepare model) 0 [0, 1] initialCache 2) = 0 := by decide +kernel
theorem selected_3 : chosen 0 [0, 1] (trajectory (prepare model) 0 [0, 1] initialCache 3) = 1 := by decide +kernel
theorem selected_4 : chosen 0 [0, 1] (trajectory (prepare model) 0 [0, 1] initialCache 4) = 0 := by decide +kernel
theorem selected_5 : chosen 0 [0, 1] (trajectory (prepare model) 0 [0, 1] initialCache 5) = 1 := by decide +kernel
def outputArrays := represent model finalGain (1/1000)
theorem output_precision_computed : outputPrecision model finalGain (1/1000) = 32 := by decide +kernel
theorem mean_centers_computed : (fun i => (outputArrays.mean i).center) = ![(2854963683/4294967296), (89217615/536870912)] := by decide +kernel
theorem mean_radii_computed : (fun i => (outputArrays.mean i).radius) = ![(1/4294967296), (1/4294967296)] := by decide +kernel
theorem covariance_centers_computed : (fun i j => (outputArrays.covariance i j).center) = !![(5726720411/4294967296), (-1431643597/2147483648); (-1431643597/2147483648), (3579145495/4294967296)] := by funext i j; fin_cases i <;> fin_cases j <;> decide +kernel
theorem covariance_radii_computed : (fun i j => (outputArrays.covariance i j).radius) = !![(1/536870912), (7/4294967296); (7/4294967296), (1/536870912)] := by funext i j; fin_cases i <;> fin_cases j <;> decide +kernel
def outputResult : Result (Fin 2) (Fin 1) (Fin 2) (Fin 1) := ⟨12,certificate,outputPrecision model finalGain (1/1000),outputArrays⟩
theorem output_return : runCached model outputs inputs 0 [0, 1] (1/20) (1/1000) [4, 12] initial = some outputResult := by
  simp only [runCached,ite_eq_left (show (0 : ℚ) < (1/1000) by norm_num),cached_return]
  rfl
theorem output_valid : ResultValid model outputs inputs (1/20) (1/1000) outputResult :=
  runCached_sound model outputs inputs 0 [0, 1] (1/20) (1/1000) [4, 12] initial outputResult output_return
end Komorebi.CachedPosterior.GeneratedCachedCoordinate
