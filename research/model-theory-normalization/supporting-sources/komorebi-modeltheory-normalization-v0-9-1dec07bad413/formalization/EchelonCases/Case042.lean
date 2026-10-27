module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case042
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (2^3)
def A : Fin 1 → Mat R 2 2 := ![![![7, 4], ![5, 2]]]
def O : Mat R 2 2 := ![![0, 4], ![4, 0]]
def result : List (Test 1 2) := [([], 0), ([], 1)]
theorem computed : fastPrimeDiscover 2 3 2
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case042
