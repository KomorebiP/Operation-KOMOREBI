module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case027
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (2^3)
def A : Fin 1 → Mat R 1 1 := ![![![5]]]
def O : Mat R 1 1 := ![![1]]
def result : List (Test 1 1) := [([], 0)]
theorem computed : fastPrimeDiscover 2 3 1
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case027
