module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case104
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (5^3)
def A : Fin 3 → Mat R 6 6 := ![![![68, 99, 104, 107, 33, 11], ![97, 106, 110, 103, 17, 96], ![51, 57, 47, 103, 82, 66], ![58, 15, 85, 59, 95, 81], ![3, 67, 122, 121, 98, 120], ![91, 39, 122, 45, 6, 50]], ![![119, 124, 124, 6, 103, 71], ![82, 53, 82, 119, 82, 30], ![27, 56, 41, 104, 13, 68], ![69, 112, 12, 58, 21, 78], ![106, 79, 40, 32, 49, 55], ![17, 78, 96, 104, 68, 96]], ![![61, 117, 70, 90, 4, 119], ![112, 51, 77, 83, 59, 72], ![55, 37, 109, 105, 68, 21], ![26, 24, 80, 9, 79, 55], ![9, 52, 88, 62, 41, 55], ![124, 110, 122, 64, 60, 17]]]
def O : Mat R 2 6 := ![![43, 20, 70, 92, 82, 15], ![6, 1, 112, 77, 90, 28]]
def result : List (Test 3 2) := [([], 0), ([], 1), ([0], 0), ([1], 0), ([2], 0), ([0], 1)]
theorem computed : fastPrimeDiscover 5 3 6
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case104
