module
public import EchelonModularNormal
public import NormalizedDiscovery

@[expose] public section
namespace Komorebi.NormalizedExamples
open Komorebi.Echelon
open Komorebi.Discovery Komorebi.Discovery.NormalizedBackend
open Komorebi.Representation Komorebi.Representation.Matrix

set_option maxRecDepth 100000
set_option maxHeartbeats 4000000

def bigTail : Basis 2 := .cons 2 (by decide) ![130] (.cons 64 (by decide) ![] .nil)
def negativeTail : Basis 2 := .cons 2 (by decide) ![-130] (.cons 64 (by decide) ![] .nil)
def coupled : Basis 2 := .cons 2 (by decide) ![32] (.cons 64 (by decide) ![] .nil)

theorem positive_tail_reduced : entries (normalize bigTail)=![![2,2],![0,64]] := by decide +kernel
theorem negative_tail_reduced : entries (normalize negativeTail)=![![2,62],![0,64]] := by decide +kernel
theorem coupled_tail_retained : entries (normalize coupled)=![![2,32],![0,64]] := by decide +kernel
theorem clipped_state_excluded : (coordinates (normalize coupled) ![2,0]).isSome=false := by decide +kernel
theorem actual_coupled_state : (coordinates (normalize coupled) ![4,0]).isSome=true := by decide +kernel

def orderA : Basis 2 := normalizedInsert (normalizedInsert (diagonal 12 (by decide) 2) ![8,4]) ![6,9]
def orderB : Basis 2 := normalizedInsert (normalizedInsert (diagonal 12 (by decide) 2) ![6,9]) ![8,4]
theorem insertion_orders_match : entries orderA=entries orderB := by decide +kernel
theorem composite_normal_form : entries orderA=![![2,1],![0,6]] := by decide +kernel

theorem trivial_ring_keeps_kernel :
    entries (canonicalBasis 1 ([] : List (Fin 2 → ZMod 1)))=![![1,0],![0,1]] := by decide +kernel

def shearA : Fin 1 → Mat (ZMod 4) 2 2 := ![![![1,1],![0,1]]]
def shearO : Mat (ZMod 4) 1 2 := ![![1,0]]
theorem shear_computed : normalizedPrimeDiscover 2 2 2
    (fun a => rowRight (shearA a)) shearO=some [([],0),([0],0)] := by decide +kernel

def emptyA : Fin 0 → Mat (ZMod 4) 0 0 := ![]
def emptyO : Mat (ZMod 4) 0 0 := ![]
theorem dimension_zero : normalizedPrimeDiscover 2 2 0
    (fun a => rowRight (emptyA a)) emptyO=some [] := by decide +kernel

def zeroPrecA : Fin 1 → Mat (ZMod (2^0)) 1 1 := ![![![1]]]
def zeroPrecO : Mat (ZMod (2^0)) 1 1 := ![![1]]
theorem zero_precision : normalizedPrimeDiscover 2 0 1
    (fun a => rowRight (zeroPrecA a)) zeroPrecO=some [] := by decide +kernel

theorem no_fuel_is_unresolved : normalizedRun 4 (fun a => rowRight (shearA a)) shearO 0
    (diagonal 4 (by decide) 2) [] []=none := rfl

end Komorebi.NormalizedExamples
