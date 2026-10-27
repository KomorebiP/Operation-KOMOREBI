module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case060
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (2^4)
def A : Fin 1 → Mat R 3 3 := ![![![15, 5, 9], ![14, 6, 5], ![15, 7, 2]]]
def O : Mat R 2 3 := ![![0, 0, 0], ![0, 0, 0]]
def result : List (Test 1 2) := []
theorem computed : fastPrimeDiscover 2 4 3
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case060
