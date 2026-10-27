module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case056
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (5^2)
def A : Fin 3 → Mat R 3 3 := ![![![20, 20, 9], ![17, 9, 4], ![5, 7, 18]], ![![20, 23, 3], ![24, 6, 22], ![8, 8, 1]], ![![14, 13, 8], ![14, 24, 8], ![11, 15, 24]]]
def O : Mat R 2 3 := ![![5, 10, 20], ![0, 20, 5]]
def result : List (Test 3 2) := [([], 0), ([], 1), ([0], 0)]
theorem computed : fastPrimeDiscover 5 2 3
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case056
