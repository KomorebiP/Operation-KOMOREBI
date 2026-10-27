module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case138
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (2^5)
def A : Fin 1 → Mat R 2 2 := ![![![18, 26], ![8, 27]]]
def O : Mat R 2 2 := ![![0, 0], ![0, 0]]
def result : List (Test 1 2) := []
theorem computed : fastPrimeDiscover 2 5 2
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case138
