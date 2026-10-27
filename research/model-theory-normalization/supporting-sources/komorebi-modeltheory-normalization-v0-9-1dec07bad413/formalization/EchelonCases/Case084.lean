module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case084
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (2^2)
def A : Fin 1 → Mat R 5 5 := ![![![0, 1, 0, 2, 0], ![2, 1, 1, 3, 3], ![2, 0, 1, 2, 1], ![0, 2, 1, 2, 2], ![0, 0, 0, 0, 3]]]
def O : Mat R 2 5 := ![![0, 2, 0, 0, 2], ![0, 0, 0, 2, 0]]
def result : List (Test 1 2) := [([], 0), ([], 1), ([0], 0), ([0], 1)]
theorem computed : fastPrimeDiscover 2 2 5
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case084
