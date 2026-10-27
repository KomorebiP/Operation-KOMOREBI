module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case108
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (2^5)
def A : Fin 1 → Mat R 6 6 := ![![![2, 29, 20, 13, 9, 8], ![29, 13, 18, 27, 27, 26], ![18, 28, 13, 11, 16, 31], ![5, 27, 2, 29, 9, 26], ![5, 8, 8, 4, 5, 6], ![7, 10, 26, 15, 8, 3]]]
def O : Mat R 2 6 := ![![31, 20, 26, 31, 24, 4], ![5, 27, 25, 8, 27, 1]]
def result : List (Test 1 2) := [([], 0), ([], 1), ([0], 0), ([0], 1), ([0,0], 0), ([0,0], 1)]
theorem computed : fastPrimeDiscover 2 5 6
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case108
