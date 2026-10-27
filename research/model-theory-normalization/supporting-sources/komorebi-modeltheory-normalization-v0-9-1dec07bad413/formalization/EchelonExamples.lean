module
public import EchelonDiscovery

@[expose] public section
namespace Komorebi.EchelonExamples
open Komorebi.Echelon Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 4000000

theorem torsion_member : member 4 [(![2] : Fin 1 → ZMod 4)] ![2] = true := by decide +kernel
theorem torsion_nonmember : member 4 [(![2] : Fin 1 → ZMod 4)] ![1] = false := by decide +kernel
theorem composite_member : member 6 [(![2] : Fin 1 → ZMod 6)] ![4] = true := by decide +kernel
theorem composite_nonmember : member 6 [(![2] : Fin 1 → ZMod 6)] ![3] = false := by decide +kernel
theorem coupled_member : member 64 [(![2,32] : Fin 2 → ZMod 64)] ![4,0] = true := by decide +kernel
theorem coupled_nonmember : member 64 [(![2,32] : Fin 2 → ZMod 64)] ![0,32] = false := by decide +kernel
theorem negative_integer_insertion :
    (coordinates (Komorebi.Echelon.insert (diagonal 6 (by decide) 2) ![-4,3]) ![2,3]).isSome = true := by decide +kernel

def shearA : Fin 1 → Mat (ZMod 4) 2 2 := ![![![1,1],![0,1]]]
def shearO : Mat (ZMod 4) 1 2 := ![![1,0]]
theorem shear_discovery : fastPrimeDiscover 2 2 2 (fun a => rowRight (shearA a)) shearO =
    some [([],0),([0],0)] := by decide +kernel

theorem empty_observations : fastPrimeDiscover 2 2 2
    (fun a => rowRight (shearA a)) (fun j : Fin 0 => Fin.elim0 j) = some [] := by decide +kernel

theorem zero_dimension : fastPrimeDiscover 2 5 0
    (fun _ : Fin 1 => LinearMap.id) (fun _ : Fin 1 => (0 : Fin 0 → ZMod (2^5))) =
    some [] := by decide +kernel

theorem zero_precision : fastPrimeDiscover 2 0 1
    (fun _ : Fin 1 => LinearMap.id) (fun _ : Fin 1 => (![1] : Fin 1 → ZMod (2^0))) =
    some [] := by decide +kernel

theorem no_actions : fastPrimeDiscover 3 2 1
    (fun a : Fin 0 => Fin.elim0 a) (fun _ : Fin 1 => (![3] : Fin 1 → ZMod (3^2))) =
    some [([],0)] := by decide +kernel

theorem zero_fuel_unresolved : fastWorklist 4 (fun a => rowRight (shearA a)) shearO
    0 (initial 4 2) [] (roots 1 1) = none := by decide +kernel

end Komorebi.EchelonExamples
