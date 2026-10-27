module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case093
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (2^5)
def A : Fin 1 → Mat R 5 5 := ![![![10, 4, 17, 24, 20], ![21, 6, 5, 17, 26], ![18, 25, 23, 19, 26], ![16, 4, 3, 11, 6], ![28, 30, 21, 1, 17]]]
def O : Mat R 1 5 := ![![22, 7, 30, 3, 2]]
def result : List (Test 1 1) := [([], 0), ([0], 0), ([0,0], 0), ([0,0,0], 0), ([0,0,0,0], 0)]
theorem computed : fastPrimeDiscover 2 5 5
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case093
