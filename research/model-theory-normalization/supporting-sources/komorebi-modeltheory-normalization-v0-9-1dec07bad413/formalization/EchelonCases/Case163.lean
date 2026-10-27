module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case163
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (3^3)
def A : Fin 2 → Mat R 4 4 := ![![![23, 9, 26, 7], ![18, 0, 3, 2], ![15, 11, 16, 25], ![13, 8, 23, 20]], ![![25, 15, 0, 20], ![0, 23, 25, 16], ![7, 20, 18, 0], ![14, 22, 6, 13]]]
def O : Mat R 1 4 := ![![19, 23, 4, 1]]
def result : List (Test 2 1) := [([], 0), ([0], 0), ([1], 0), ([0,0], 0), ([1,0], 0)]
theorem computed : fastPrimeDiscover 3 3 4
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case163
