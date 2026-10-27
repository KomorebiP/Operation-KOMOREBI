module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case078
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (2^5)
def A : Fin 1 → Mat R 4 4 := ![![![18, 0, 1, 27], ![10, 31, 20, 10], ![16, 28, 15, 20], ![25, 21, 30, 23]]]
def O : Mat R 2 4 := ![![23, 1, 19, 28], ![7, 25, 16, 5]]
def result : List (Test 1 2) := [([], 0), ([], 1), ([0], 0), ([0], 1)]
theorem computed : fastPrimeDiscover 2 5 4
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case078
