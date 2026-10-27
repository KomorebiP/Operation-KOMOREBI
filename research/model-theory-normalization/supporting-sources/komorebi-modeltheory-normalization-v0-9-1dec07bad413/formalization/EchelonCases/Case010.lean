module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case010
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (3^3)
def A : Fin 2 → Mat R 6 6 := ![![![0, 8, 10, 19, 2, 8], ![23, 24, 3, 15, 20, 1], ![1, 2, 13, 13, 24, 25], ![13, 26, 0, 17, 24, 9], ![5, 20, 20, 2, 9, 25], ![12, 0, 23, 14, 0, 14]], ![![19, 17, 1, 22, 13, 1], ![25, 22, 23, 10, 26, 11], ![26, 7, 18, 16, 26, 20], ![8, 17, 25, 25, 24, 1], ![14, 3, 22, 20, 0, 16], ![10, 12, 14, 24, 1, 17]]]
def O : Mat R 1 6 := ![![24, 17, 7, 14, 13, 23]]
def result : List (Test 2 1) := [([], 0), ([0], 0)]
theorem computed : fastPrimeDiscover 3 3 6
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case010
