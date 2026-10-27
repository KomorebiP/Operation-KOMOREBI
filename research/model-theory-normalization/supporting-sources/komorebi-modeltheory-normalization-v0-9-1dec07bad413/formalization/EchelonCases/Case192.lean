module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case192
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (2^3)
def A : Fin 1 → Mat R 6 6 := ![![![6, 3, 5, 4, 6, 2], ![4, 1, 2, 6, 0, 1], ![7, 2, 5, 7, 4, 0], ![6, 3, 4, 1, 3, 0], ![7, 1, 4, 0, 0, 5], ![6, 4, 4, 1, 2, 7]]]
def O : Mat R 2 6 := ![![0, 3, 3, 3, 6, 7], ![0, 6, 0, 6, 2, 2]]
def result : List (Test 1 2) := [([], 0), ([], 1), ([0], 0), ([0], 1), ([0,0], 0), ([0,0,0], 0), ([0,0,0,0], 0)]
theorem computed : fastPrimeDiscover 2 3 6
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case192
