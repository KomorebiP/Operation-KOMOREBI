module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case150
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (2^4)
def A : Fin 1 → Mat R 3 3 := ![![![12, 3, 2], ![15, 2, 3], ![10, 15, 12]]]
def O : Mat R 2 3 := ![![2, 1, 6], ![5, 11, 2]]
def result : List (Test 1 2) := [([], 0), ([], 1), ([0], 0)]
theorem computed : fastPrimeDiscover 2 4 3
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case150
