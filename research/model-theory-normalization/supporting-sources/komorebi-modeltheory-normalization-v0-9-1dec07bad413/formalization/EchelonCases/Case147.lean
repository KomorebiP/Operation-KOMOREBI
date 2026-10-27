module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case147
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (2^3)
def A : Fin 1 → Mat R 3 3 := ![![![6, 2, 0], ![5, 5, 6], ![6, 0, 4]]]
def O : Mat R 1 3 := ![![4, 4, 0]]
def result : List (Test 1 1) := [([], 0)]
theorem computed : fastPrimeDiscover 2 3 3
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case147
