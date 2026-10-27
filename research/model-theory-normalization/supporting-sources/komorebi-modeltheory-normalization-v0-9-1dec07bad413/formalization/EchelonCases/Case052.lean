module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case052
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (3^1)
def A : Fin 2 → Mat R 3 3 := ![![![2, 0, 1], ![1, 2, 2], ![2, 1, 0]], ![![0, 0, 0], ![1, 1, 2], ![1, 0, 1]]]
def O : Mat R 2 3 := ![![0, 0, 1], ![1, 0, 2]]
def result : List (Test 2 2) := [([], 0), ([], 1), ([0], 0)]
theorem computed : fastPrimeDiscover 3 1 3
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case052
