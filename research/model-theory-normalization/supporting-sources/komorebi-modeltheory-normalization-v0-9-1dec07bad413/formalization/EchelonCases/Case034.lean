module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case034
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (3^5)
def A : Fin 2 → Mat R 1 1 := ![![![104]], ![![102]]]
def O : Mat R 2 1 := ![![0], ![0]]
def result : List (Test 2 2) := []
theorem computed : fastPrimeDiscover 3 5 1
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case034
