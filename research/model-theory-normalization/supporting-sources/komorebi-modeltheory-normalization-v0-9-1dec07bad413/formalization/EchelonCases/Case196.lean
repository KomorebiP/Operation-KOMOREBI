module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case196
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (3^4)
def A : Fin 2 → Mat R 6 6 := ![![![8, 19, 44, 66, 42, 8], ![21, 68, 61, 80, 63, 50], ![42, 67, 13, 43, 30, 70], ![79, 23, 37, 29, 17, 80], ![30, 33, 27, 67, 73, 47], ![68, 3, 45, 46, 22, 50]], ![![53, 76, 44, 41, 10, 52], ![34, 31, 8, 12, 32, 71], ![76, 54, 7, 69, 25, 39], ![28, 40, 40, 26, 72, 1], ![26, 76, 44, 65, 35, 28], ![47, 68, 67, 26, 57, 33]]]
def O : Mat R 2 6 := ![![27, 27, 0, 27, 0, 27], ![0, 0, 0, 27, 27, 0]]
def result : List (Test 2 2) := [([], 0), ([], 1), ([0], 0), ([1], 0), ([0], 1), ([1,0], 0)]
theorem computed : fastPrimeDiscover 3 4 6
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case196
