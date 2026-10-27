import Komorebi.AdaptivePacketInvariants
import Komorebi.RationalSolverDecidable
import Mathlib.LinearAlgebra.Matrix.Notation

set_option autoImplicit false
namespace Komorebi.AdaptivePosterior.Boundary
open Komorebi.ExactPosterior Komorebi.RoundedPosterior

def model : RationalModel (Fin 1) (Fin 2) (Fin 1) (Fin 1) where
  observationMatrix := !![1;1]
  priorFactor := !![1]
  noiseFactor := !![0;0]
  noiseFloor := 1
  mean := ![0]
  observation := ![0,0]
def gain : Matrix (Fin 1) (Fin 2) ℚ := !![-(1/3),2/3]
def rightSecond : Matrix (Fin 2) (Fin 2) ℚ := !![0,0;0,1]
def nextGain := packetStep model (1 : Matrix (Fin 1) (Fin 1) ℚ) gain

theorem residual_before : model.residual gain = !![1,0] := by decide +kernel
theorem residual_after : model.residual nextGain = !![3/5,-(1/5)] := by decide +kernel
/-- A previously zero input packet can grow under a valid output-packet update. -/
theorem right_packet_grows :
    rationalEnergy (model.residual gain * rightSecond) = 0 ∧
    rationalEnergy (model.residual nextGain * rightSecond) = 1/25 := by decide +kernel

theorem total_energy_decreases : rationalEnergy (model.residual gain) = 1 ∧
    rationalEnergy (model.residual nextGain) = 2/5 := by decide +kernel

def outputPackets : Fin 1 → Matrix (Fin 1) (Fin 1) ℚ := ![!![1]]
def inputPackets : Fin 2 → Matrix (Fin 2) (Fin 2) ℚ := ![!![1,0;0,0],!![0,0;0,1]]
theorem valid_setup : checkSetup model outputPackets inputPackets = true := by decide +kernel

theorem missing_scan_rejected : solveAdaptive model outputPackets inputPackets 0 [] (1/10) [12] gain = none := by decide +kernel

/-- Maximum scan ties preserve the incumbent, including duplicates. -/
theorem tie_preserves_seed : winner (fun (_ : Fin 2) => (3 : ℚ)) 1 [0,1,0] = 1 := by decide +kernel

end Komorebi.AdaptivePosterior.Boundary
