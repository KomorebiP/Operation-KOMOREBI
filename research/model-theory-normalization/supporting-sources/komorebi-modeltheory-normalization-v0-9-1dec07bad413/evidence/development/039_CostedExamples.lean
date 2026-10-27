module
public import CostedBounds

@[expose] public section
namespace Komorebi.CostedExamples
open Komorebi.Costed Komorebi.Echelon
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000

def fourBasis : Basis 2 := .cons 4 (by decide) ![0] (.cons 4 (by decide) ![] .nil)

theorem signed_euclid : signedEuclidEval 240 (-46)=((-9,-47),30) := by decide +kernel
theorem failed_membership : coordinatesEval fourBasis ![3,3]=(none,2) := by decide +kernel
theorem residue_units : residueEval fourBasis ![3,3]=(![3,3],6) := by decide +kernel
theorem normalization_units : (normalizeEval fourBasis).2=2 := by decide +kernel
theorem insertion_units : (insertEval fourBasis ![3,3]).2=56 := by decide +kernel
theorem update_units : (updateEval fourBasis ![3,3]).2=58 := by decide +kernel
theorem update_value : entries (updateEval fourBasis ![3,3]).1=![![1,1],![0,4]] := by decide +kernel

def actions : Fin 2 → Mat ℤ 2 2 := ![![![1,1],![0,1]],![![0,1],![1,0]]]
def observation : Mat ℤ 1 2 := ![![1,0]]
theorem source_word_order : testEval actions observation ([0,1],0)=(![0,1],16) := by decide +kernel
theorem reversed_word_different : testEval actions observation ([1,0],0)=(![1,1],16) := by decide +kernel

theorem zero_dimension : discoverEval 2 3 0
    (k:=1) (o:=1) ![![]] ![![]]=(some [],1) := by decide +kernel
theorem no_observations : discoverEval 2 3 3
    (k:=0) (o:=0) ![] ![]=(some [],8) := by decide +kernel
theorem zero_precision : discoverEval 2 0 2
    (k:=1) (o:=1) ![![![1,0],![0,1]]] ![![1,1]]=(some [],13) := by decide +kernel
theorem exhausted_fuel : runEval 4 (k:=0) (o:=0) (![] : Fin 0 → Mat (ZMod 4) 2 2)
    ![] 0 fourBasis [] []=(none,0) := by decide +kernel
theorem exact_normalization_polynomial (d : Nat) :
    3*normalizationUnits d+d=d*d*d := normalizationUnits_cubic d

end Komorebi.CostedExamples
