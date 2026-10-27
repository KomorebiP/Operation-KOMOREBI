module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case029
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (5^3)
def A : Fin 3 → Mat R 1 1 := ![![![121]], ![![45]], ![![80]]]
def O : Mat R 1 1 := ![![29]]
def result : List (Test 3 1) := [([], 0)]
theorem computed : fastPrimeDiscover 5 3 1
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case029
