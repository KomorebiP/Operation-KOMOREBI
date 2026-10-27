module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case025
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (3^2)
def A : Fin 2 → Mat R 1 1 := ![![![6]], ![![0]]]
def O : Mat R 1 1 := ![![4]]
def result : List (Test 2 1) := [([], 0)]
theorem computed : fastPrimeDiscover 3 2 1
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case025
