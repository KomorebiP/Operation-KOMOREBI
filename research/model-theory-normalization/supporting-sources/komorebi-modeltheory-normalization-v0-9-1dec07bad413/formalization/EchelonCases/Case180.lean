module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case180
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (2^4)
def A : Fin 1 → Mat R 5 5 := ![![![8, 5, 4, 14, 14], ![14, 4, 3, 10, 0], ![4, 12, 8, 11, 11], ![10, 7, 2, 2, 10], ![6, 2, 3, 2, 9]]]
def O : Mat R 2 5 := ![![11, 7, 5, 15, 13], ![14, 8, 15, 11, 2]]
def result : List (Test 1 2) := [([], 0), ([], 1), ([0], 0), ([0], 1), ([0,0], 0)]
theorem computed : fastPrimeDiscover 2 4 5
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case180
