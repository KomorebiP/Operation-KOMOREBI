module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case178
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (3^3)
def A : Fin 2 → Mat R 5 5 := ![![![9, 26, 6, 11, 22], ![5, 3, 16, 21, 5], ![20, 21, 14, 18, 23], ![22, 10, 10, 0, 11], ![4, 1, 18, 10, 24]], ![![11, 7, 16, 1, 12], ![13, 23, 3, 6, 16], ![18, 0, 21, 9, 3], ![23, 19, 18, 12, 1], ![15, 18, 12, 9, 17]]]
def O : Mat R 2 5 := ![![1, 26, 5, 18, 8], ![1, 8, 11, 8, 14]]
def result : List (Test 2 2) := [([], 0), ([], 1), ([0], 0), ([1], 0), ([0], 1), ([1], 1)]
theorem computed : fastPrimeDiscover 3 3 5
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case178
