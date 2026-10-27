module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case106
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (3^4)
def A : Fin 2 → Mat R 6 6 := ![![![57, 35, 22, 33, 57, 75], ![0, 10, 70, 69, 35, 58], ![77, 52, 8, 19, 62, 65], ![73, 28, 12, 12, 53, 42], ![27, 54, 39, 54, 65, 45], ![36, 45, 80, 11, 60, 55]], ![![70, 22, 13, 58, 73, 9], ![51, 22, 57, 80, 51, 44], ![16, 48, 28, 5, 30, 13], ![5, 32, 39, 39, 8, 55], ![23, 65, 32, 31, 9, 44], ![68, 1, 73, 37, 18, 19]]]
def O : Mat R 2 6 := ![![15, 22, 30, 60, 51, 51], ![78, 3, 10, 57, 17, 53]]
def result : List (Test 2 2) := [([], 0), ([], 1), ([0], 0), ([1], 0), ([0], 1), ([1], 1)]
theorem computed : fastPrimeDiscover 3 4 6
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case106
