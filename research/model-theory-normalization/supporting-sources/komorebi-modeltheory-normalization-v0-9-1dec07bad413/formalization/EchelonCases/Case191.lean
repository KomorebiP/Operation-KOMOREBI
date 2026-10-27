module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case191
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (5^2)
def A : Fin 3 → Mat R 6 6 := ![![![20, 21, 12, 18, 2, 6], ![2, 2, 10, 22, 18, 14], ![2, 2, 1, 0, 3, 20], ![8, 18, 2, 4, 13, 20], ![2, 9, 5, 19, 10, 22], ![10, 2, 5, 11, 9, 17]], ![![1, 13, 24, 5, 7, 23], ![8, 5, 5, 24, 18, 1], ![4, 5, 21, 20, 6, 5], ![0, 1, 6, 23, 5, 0], ![8, 2, 12, 13, 4, 1], ![7, 15, 19, 21, 12, 17]], ![![16, 23, 14, 24, 6, 21], ![23, 14, 0, 1, 22, 1], ![10, 10, 23, 13, 5, 17], ![23, 0, 5, 2, 5, 0], ![5, 12, 15, 16, 1, 10], ![24, 13, 21, 24, 14, 2]]]
def O : Mat R 1 6 := ![![22, 19, 4, 10, 21, 15]]
def result : List (Test 3 1) := [([], 0), ([0], 0), ([1], 0), ([2], 0), ([0,0], 0), ([1,0], 0)]
theorem computed : fastPrimeDiscover 5 2 6
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case191
