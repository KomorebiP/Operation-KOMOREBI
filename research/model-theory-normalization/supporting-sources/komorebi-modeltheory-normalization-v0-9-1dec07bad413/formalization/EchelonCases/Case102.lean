module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case102
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (2^3)
def A : Fin 1 → Mat R 6 6 := ![![![4, 0, 3, 4, 6, 4], ![7, 1, 0, 7, 5, 1], ![5, 5, 5, 3, 2, 0], ![4, 6, 6, 7, 1, 7], ![4, 1, 1, 6, 0, 5], ![4, 0, 6, 4, 4, 7]]]
def O : Mat R 2 6 := ![![3, 5, 7, 7, 7, 2], ![4, 3, 0, 0, 2, 1]]
def result : List (Test 1 2) := [([], 0), ([], 1), ([0], 0), ([0], 1), ([0,0], 0), ([0,0], 1)]
theorem computed : fastPrimeDiscover 2 3 6
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case102
