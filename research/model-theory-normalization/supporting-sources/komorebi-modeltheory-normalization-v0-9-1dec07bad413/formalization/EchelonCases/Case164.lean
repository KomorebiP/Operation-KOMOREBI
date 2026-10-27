module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case164
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (5^3)
def A : Fin 3 → Mat R 4 4 := ![![![104, 15, 50, 10], ![108, 2, 122, 119], ![81, 63, 119, 1], ![113, 38, 57, 94]], ![![48, 13, 120, 73], ![115, 93, 26, 118], ![81, 55, 42, 53], ![22, 46, 85, 35]], ![![12, 83, 51, 50], ![10, 28, 115, 78], ![1, 16, 51, 59], ![66, 21, 99, 117]]]
def O : Mat R 2 4 := ![![0, 0, 0, 0], ![0, 0, 0, 0]]
def result : List (Test 3 2) := []
theorem computed : fastPrimeDiscover 5 3 4
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case164
