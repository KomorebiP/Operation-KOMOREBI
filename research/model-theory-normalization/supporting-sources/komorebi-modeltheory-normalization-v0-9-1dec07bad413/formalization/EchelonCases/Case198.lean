module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case198
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (2^5)
def A : Fin 1 → Mat R 6 6 := ![![![27, 8, 24, 27, 3, 0], ![29, 18, 26, 18, 29, 18], ![3, 21, 12, 22, 10, 6], ![31, 15, 4, 28, 11, 23], ![19, 24, 14, 31, 26, 31], ![25, 11, 17, 25, 15, 7]]]
def O : Mat R 2 6 := ![![11, 13, 19, 21, 3, 26], ![10, 14, 5, 3, 31, 16]]
def result : List (Test 1 2) := [([], 0), ([], 1), ([0], 0), ([0], 1), ([0,0], 0), ([0,0], 1), ([0,0,0], 0)]
theorem computed : fastPrimeDiscover 2 5 6
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case198
