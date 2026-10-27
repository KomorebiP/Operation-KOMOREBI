module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case090
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (2^4)
def A : Fin 1 → Mat R 5 5 := ![![![12, 15, 0, 3, 11], ![12, 0, 6, 13, 1], ![9, 8, 15, 8, 10], ![2, 14, 13, 15, 3], ![14, 3, 0, 5, 13]]]
def O : Mat R 2 5 := ![![7, 3, 15, 10, 11], ![11, 8, 5, 10, 3]]
def result : List (Test 1 2) := [([], 0), ([], 1), ([0], 0), ([0], 1), ([0,0], 0)]
theorem computed : fastPrimeDiscover 2 4 5
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case090
