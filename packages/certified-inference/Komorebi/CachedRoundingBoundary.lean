import Komorebi.CachedPacketSolver
import Komorebi.DyadicBall
import Komorebi.RationalSolverDecidable
import Mathlib.LinearAlgebra.Matrix.Notation

set_option autoImplicit false
namespace Komorebi.CachedPosterior.Boundary
open Komorebi.ExactPosterior Komorebi.RoundedPosterior

def model : RationalModel (Fin 1) (Fin 1) (Fin 1) (Fin 1) where
  observationMatrix := !![1]
  priorFactor := !![1]
  noiseFactor := !![0]
  noiseFloor := 1
  mean := ![0]
  observation := ![1]
def packets : Fin 1 → Matrix (Fin 1) (Fin 1) ℚ := ![!![1]]
def zeroGain : Matrix (Fin 1) (Fin 1) ℚ := !![0]
/-- Independently rounded gain and residual centers destroy the exact cache invariant. -/
def naiveRounded : State (Fin 1) (Fin 1) (Fin 1) :=
  let ideal := step (prepare model) 0 (initialState model packets zeroGain)
  let B := fun i j => down 0 (ideal.gain i j)
  let G := fun a i j => down 0 (ideal.residuals a i j)
  let e := fun a => rationalEnergy (G a)
  ⟨B,G,e,∑ a, e a⟩

theorem naive_score_zero : score (prepare model) naiveRounded = 0 := by decide +kernel
theorem true_score_two : model.residualScore naiveRounded.gain = 2 := by decide +kernel
theorem naive_cache_invalid : ¬ Valid model packets naiveRounded := by unfold Valid; decide +kernel
theorem valid_setup : checkSetup model packets packets = true := by decide +kernel

theorem naive_final_verification_rejected :
    Komorebi.RoundoffSolver.certifyGain model packets packets (1/10) [12] naiveRounded.gain = none := by decide +kernel

end Komorebi.CachedPosterior.Boundary
