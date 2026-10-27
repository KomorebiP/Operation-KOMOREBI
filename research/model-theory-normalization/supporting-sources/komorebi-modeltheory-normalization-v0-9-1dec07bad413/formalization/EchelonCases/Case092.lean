module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case092
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (5^4)
def A : Fin 3 → Mat R 5 5 := ![![![229, 287, 50, 317, 544], ![192, 326, 502, 259, 466], ![239, 6, 59, 596, 134], ![283, 460, 37, 549, 29], ![545, 154, 354, 501, 561]], ![![228, 153, 350, 589, 583], ![308, 252, 467, 249, 140], ![445, 375, 621, 543, 346], ![512, 323, 353, 27, 602], ![400, 76, 346, 528, 58]], ![![82, 101, 106, 233, 309], ![387, 35, 357, 162, 203], ![619, 6, 428, 317, 154], ![236, 163, 175, 392, 141], ![253, 283, 491, 528, 194]]]
def O : Mat R 2 5 := ![![467, 203, 247, 46, 165], ![354, 10, 202, 138, 248]]
def result : List (Test 3 2) := [([], 0), ([], 1), ([0], 0), ([1], 0), ([2], 0), ([0], 1)]
theorem computed : fastPrimeDiscover 5 4 5
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case092
