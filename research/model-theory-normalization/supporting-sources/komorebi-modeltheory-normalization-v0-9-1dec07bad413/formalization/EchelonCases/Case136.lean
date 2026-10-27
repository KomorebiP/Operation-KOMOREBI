module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case136
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (3^4)
def A : Fin 2 → Mat R 2 2 := ![![![2, 68], ![7, 64]], ![![56, 27], ![31, 42]]]
def O : Mat R 2 2 := ![![75, 9], ![78, 50]]
def result : List (Test 2 2) := [([], 0), ([], 1), ([0], 1)]
theorem computed : fastPrimeDiscover 3 4 2
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case136
