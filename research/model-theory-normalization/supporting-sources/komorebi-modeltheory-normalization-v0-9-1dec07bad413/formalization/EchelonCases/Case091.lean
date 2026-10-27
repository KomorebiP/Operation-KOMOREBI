module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case091
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (3^4)
def A : Fin 2 → Mat R 5 5 := ![![![9, 43, 18, 8, 34], ![48, 74, 48, 28, 54], ![26, 79, 40, 1, 35], ![17, 17, 42, 77, 64], ![26, 14, 35, 17, 17]], ![![22, 79, 68, 63, 14], ![69, 76, 64, 36, 56], ![69, 12, 14, 69, 20], ![0, 56, 30, 63, 0], ![21, 4, 75, 34, 71]]]
def O : Mat R 1 5 := ![![0, 54, 54, 27, 27]]
def result : List (Test 2 1) := [([], 0), ([0], 0), ([1], 0), ([0,0], 0), ([1,0], 0)]
theorem computed : fastPrimeDiscover 3 4 5
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case091
