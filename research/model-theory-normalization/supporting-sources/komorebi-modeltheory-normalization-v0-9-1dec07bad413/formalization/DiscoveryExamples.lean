module
public import DiscoveryLogic
public meta import DiscoveryLogic

@[expose] public section
namespace Komorebi.Discovery.Examples
open Komorebi.Representation Komorebi.Representation.Matrix
open Komorebi.ModelTheory Komorebi.ModelTheory.Standard
open Komorebi.Discovery

set_option maxRecDepth 100000
set_option maxHeartbeats 2000000

/-- x evolves to x+y, and z is never observed. -/
def shearA : Fin 1 → Mat (ZMod 4) 3 3 := fun _ =>
  ![![1,1,0], ![0,1,0], ![0,0,1]]
def shearO : Mat (ZMod 4) 1 3 := ![![1,0,0]]
def shearTests : List (Test 1 1) := [([],0),([0],0)]

theorem shear_computed :
    finitePrimeDiscover 2 2 3 (fun a => rowRight (shearA a)) shearO = some shearTests := by
  decide +kernel

theorem shear_all_words (x y : Fin 3 → ZMod 4) :
    CodeEqual (linearSystem shearA shearO) shearTests x y ↔
      ObsEq (linearSystem shearA shearO) x y :=
  certified_code_exact _ _
    (discoveredCodeCertificate shearA shearO (enumerationOracle _ _) 6 shearTests shear_computed) x y

theorem shear_standard_definition (e : Fin 2 → TaggedCarrier (Fin 3 → ZMod 4) (ZMod 4)) :
    taggedRealize (linearSystem shearA shearO) (guardedCodeFormula shearTests) e ↔
      e ∈ taggedBehaviorSet (linearSystem shearA shearO) :=
  discoveredFormula_exact shearA shearO (enumerationOracle _ _) 6 shearTests shear_computed e

/-- Two genuinely nonzero order-two row directions are retained. -/
def torsionA : Fin 1 → Mat (ZMod 4) 2 2 := fun _ => ![![0,1],![1,0]]
def torsionO : Mat (ZMod 4) 1 2 := ![![2,0]]
theorem torsion_computed :
    finitePrimeDiscover 2 2 2 (fun a => rowRight (torsionA a)) torsionO =
      some [([],0),([0],0)] := by decide +kernel

/-- A chain actually needs three operations to expose its final coordinate. -/
def delayA : Fin 1 → Mat (ZMod 2) 4 4 := fun _ =>
  ![![0,1,0,0],![0,0,1,0],![0,0,0,1],![0,0,0,0]]
def delayO : Mat (ZMod 2) 1 4 := ![![1,0,0,0]]
theorem delay_computed :
    finitePrimeDiscover 2 1 4 (fun a => rowRight (delayA a)) delayO =
      some [([],0),([0],0),([0,0],0),([0,0,0],0)] := by decide +kernel

def ternaryA : Fin 1 → Mat (ZMod 3) 2 2 := fun _ => ![![1,2],![0,1]]
def ternaryO : Mat (ZMod 3) 1 2 := ![![1,0]]
theorem ternary_computed :
    finitePrimeDiscover 3 1 2 (fun a => rowRight (ternaryA a)) ternaryO =
      some [([],0),([0],0)] := by decide +kernel

def nilActions : Fin 0 → Mat (ZMod 4) 2 2 := Fin.elim0
def multipleO : Mat (ZMod 4) 3 2 := ![![2,0],![2,0],![0,2]]
theorem no_actions_computed :
    finitePrimeDiscover 2 2 2 (fun a => rowRight (nilActions a)) multipleO =
      some [([],0),([],2)] := by decide +kernel

def nilObservations : Mat (ZMod 4) 0 3 := Fin.elim0
theorem no_observations_computed :
    finitePrimeDiscover 2 2 3 (fun a => rowRight (shearA a)) nilObservations = some [] := by decide +kernel

def zeroA : Fin 1 → Mat (ZMod 4) 0 0 := fun _ => Fin.elim0
def zeroO : Mat (ZMod 4) 1 0 := fun _ => Fin.elim0
theorem zero_dimension_computed :
    finitePrimeDiscover 2 2 0 (fun a => rowRight (zeroA a)) zeroO = some [] := by decide +kernel

def trivialA : Fin 1 → Mat (ZMod 1) 1 1 := fun _ => ![![0]]
def trivialO : Mat (ZMod 1) 1 1 := ![![0]]
theorem precision_zero_computed :
    finitePrimeDiscover 2 0 1 (fun a => rowRight (trivialA a)) trivialO = some [] := by decide +kernel

/-- A resource-limited unfinished run reports none, never a completed quotient. -/
theorem insufficient_fuel :
    worklist (fun a => rowRight (shearA a)) shearO (enumerationOracle _ _) 1 [] (roots 1 1) =
      none := by decide +kernel

#eval (finitePrimeDiscover 2 2 3 (fun a => rowRight (shearA a)) shearO).map
  (fun ts => ts.map (fun t => (t.1.map Fin.val, t.2.val)))
#eval (finitePrimeDiscover 2 1 4 (fun a => rowRight (delayA a)) delayO).map
  (fun ts => ts.map (fun t => (t.1.map Fin.val, t.2.val)))

end Komorebi.Discovery.Examples
