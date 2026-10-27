module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case009
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (3^3)
def A : Fin 2 → Mat R 4 4 := ![![![6, 5, 10, 1], ![22, 10, 26, 13], ![0, 15, 1, 15], ![20, 12, 4, 24]], ![![12, 0, 10, 12], ![7, 16, 7, 17], ![0, 12, 11, 21], ![26, 12, 23, 8]]]
def O : Mat R 1 4 := ![![18, 12, 1, 21]]
def result : List (Test 2 1) := [([], 0), ([0], 0)]
theorem computed : fastPrimeDiscover 3 3 4
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case009
