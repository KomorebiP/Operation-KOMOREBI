module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case071
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (5^2)
def A : Fin 3 → Mat R 4 4 := ![![![2, 3, 23, 12], ![12, 8, 13, 2], ![12, 16, 15, 17], ![16, 6, 12, 11]], ![![14, 10, 3, 5], ![10, 7, 0, 10], ![1, 19, 14, 8], ![15, 1, 12, 12]], ![![19, 24, 18, 22], ![12, 7, 5, 19], ![23, 15, 5, 19], ![22, 17, 8, 6]]]
def O : Mat R 1 4 := ![![1, 8, 11, 6]]
def result : List (Test 3 1) := [([], 0), ([0], 0), ([1], 0), ([2], 0)]
theorem computed : fastPrimeDiscover 5 2 4
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case071
