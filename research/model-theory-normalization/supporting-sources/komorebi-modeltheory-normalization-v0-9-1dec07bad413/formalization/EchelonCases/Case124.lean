module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case124
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (3^5)
def A : Fin 2 → Mat R 1 1 := ![![![97]], ![![142]]]
def O : Mat R 2 1 := ![![171], ![39]]
def result : List (Test 2 2) := [([], 0), ([], 1)]
theorem computed : fastPrimeDiscover 3 5 1
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case124
