module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case190
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (3^2)
def A : Fin 2 → Mat R 6 6 := ![![![1, 8, 2, 8, 5, 1], ![4, 1, 5, 8, 8, 8], ![1, 6, 8, 3, 7, 3], ![5, 6, 6, 8, 5, 2], ![6, 7, 2, 2, 7, 3], ![1, 4, 4, 5, 1, 5]], ![![5, 4, 1, 0, 0, 0], ![7, 8, 5, 6, 7, 4], ![8, 5, 4, 3, 4, 7], ![6, 7, 3, 2, 3, 3], ![2, 2, 4, 5, 2, 5], ![3, 3, 8, 1, 4, 1]]]
def O : Mat R 2 6 := ![![0, 0, 0, 0, 0, 0], ![0, 0, 0, 0, 0, 0]]
def result : List (Test 2 2) := []
theorem computed : fastPrimeDiscover 3 2 6
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case190
