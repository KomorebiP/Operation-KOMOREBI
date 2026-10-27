module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case048
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (2^5)
def A : Fin 1 → Mat R 2 2 := ![![![23, 0], ![13, 18]]]
def O : Mat R 2 2 := ![![0, 1], ![15, 19]]
def result : List (Test 1 2) := [([], 0), ([], 1)]
theorem computed : fastPrimeDiscover 2 5 2
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case048
