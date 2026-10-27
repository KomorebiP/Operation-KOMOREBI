module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case194
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (5^3)
def A : Fin 3 → Mat R 6 6 := ![![![24, 66, 28, 73, 108, 90], ![88, 90, 116, 100, 34, 69], ![4, 63, 8, 79, 3, 42], ![19, 81, 62, 56, 16, 50], ![105, 67, 122, 7, 104, 0], ![112, 18, 67, 52, 10, 41]], ![![64, 109, 99, 36, 122, 10], ![5, 97, 70, 31, 41, 118], ![116, 58, 122, 55, 93, 104], ![52, 4, 30, 30, 8, 93], ![48, 94, 6, 6, 10, 91], ![80, 43, 58, 0, 16, 118]], ![![54, 18, 65, 34, 111, 78], ![47, 7, 119, 5, 48, 88], ![24, 110, 95, 37, 29, 82], ![98, 124, 89, 103, 55, 2], ![49, 113, 120, 15, 88, 55], ![102, 15, 3, 109, 77, 50]]]
def O : Mat R 2 6 := ![![86, 71, 44, 98, 62, 37], ![97, 24, 77, 0, 105, 85]]
def result : List (Test 3 2) := [([], 0), ([], 1), ([0], 0), ([1], 0), ([2], 0), ([0], 1)]
theorem computed : fastPrimeDiscover 5 3 6
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case194
