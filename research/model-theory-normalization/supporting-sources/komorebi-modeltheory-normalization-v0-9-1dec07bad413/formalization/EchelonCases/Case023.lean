module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case023
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (5^1)
def A : Fin 3 → Mat R 1 1 := ![![![3]], ![![1]], ![![3]]]
def O : Mat R 1 1 := ![![1]]
def result : List (Test 3 1) := [([], 0)]
theorem computed : fastPrimeDiscover 5 1 1
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case023
