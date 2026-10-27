module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case006
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (2^5)
def A : Fin 2 → Mat R 6 6 := ![![![7, 1, 3, 30, 26, 12], ![14, 0, 21, 17, 5, 24], ![26, 11, 24, 15, 20, 19], ![16, 3, 19, 14, 28, 19], ![12, 26, 25, 26, 13, 7], ![8, 19, 15, 14, 0, 7]], ![![9, 5, 8, 10, 20, 20], ![23, 15, 31, 8, 29, 7], ![21, 5, 31, 15, 0, 17], ![24, 17, 30, 0, 18, 22], ![28, 9, 12, 2, 4, 8], ![25, 15, 26, 14, 14, 8]]]
def O : Mat R 1 6 := ![![13, 18, 20, 28, 0, 27]]
def result : List (Test 2 1) := [([], 0), ([0], 0)]
theorem computed : fastPrimeDiscover 2 5 6
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case006
