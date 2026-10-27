module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case121
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (3^4)
def A : Fin 2 → Mat R 1 1 := ![![![61]], ![![12]]]
def O : Mat R 1 1 := ![![71]]
def result : List (Test 2 1) := [([], 0)]
theorem computed : fastPrimeDiscover 3 4 1
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case121
