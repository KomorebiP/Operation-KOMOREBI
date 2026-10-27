module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case119
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (5^3)
def A : Fin 3 → Mat R 1 1 := ![![![60]], ![![100]], ![![84]]]
def O : Mat R 1 1 := ![![75]]
def result : List (Test 3 1) := [([], 0)]
theorem computed : fastPrimeDiscover 5 3 1
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case119
