module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case177
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (2^3)
def A : Fin 1 → Mat R 5 5 := ![![![6, 2, 6, 0, 0], ![1, 0, 4, 1, 7], ![4, 7, 0, 0, 7], ![2, 3, 6, 4, 2], ![0, 1, 4, 3, 3]]]
def O : Mat R 1 5 := ![![0, 0, 0, 0, 0]]
def result : List (Test 1 1) := []
theorem computed : fastPrimeDiscover 2 3 5
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case177
