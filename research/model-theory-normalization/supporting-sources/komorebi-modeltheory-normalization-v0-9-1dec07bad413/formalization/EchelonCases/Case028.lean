module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case028
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (3^3)
def A : Fin 2 → Mat R 1 1 := ![![![7]], ![![4]]]
def O : Mat R 2 1 := ![![18], ![9]]
def result : List (Test 2 2) := [([], 0)]
theorem computed : fastPrimeDiscover 3 3 1
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case028
