module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case174
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (2^2)
def A : Fin 1 → Mat R 5 5 := ![![![1, 0, 2, 1, 3], ![3, 1, 2, 0, 1], ![2, 0, 2, 2, 2], ![2, 3, 0, 2, 0], ![2, 3, 2, 2, 0]]]
def O : Mat R 2 5 := ![![1, 3, 3, 0, 3], ![2, 1, 3, 3, 2]]
def result : List (Test 1 2) := [([], 0), ([], 1), ([0], 0), ([0], 1), ([0,0], 0)]
theorem computed : fastPrimeDiscover 2 2 5
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case174
