module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case033
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (2^5)
def A : Fin 1 → Mat R 1 1 := ![![![3]]]
def O : Mat R 1 1 := ![![7]]
def result : List (Test 1 1) := [([], 0)]
theorem computed : fastPrimeDiscover 2 5 1
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case033
