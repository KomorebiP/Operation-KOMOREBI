module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case176
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (5^2)
def A : Fin 3 → Mat R 5 5 := ![![![8, 3, 20, 15, 0], ![10, 17, 7, 17, 23], ![23, 14, 8, 4, 4], ![18, 10, 21, 8, 2], ![17, 4, 18, 8, 13]], ![![22, 14, 5, 15, 8], ![5, 15, 1, 4, 20], ![24, 12, 23, 2, 21], ![10, 9, 5, 18, 21], ![11, 16, 16, 22, 23]], ![![10, 24, 10, 3, 23], ![0, 6, 22, 11, 3], ![21, 15, 20, 0, 11], ![9, 14, 20, 21, 9], ![2, 13, 10, 2, 8]]]
def O : Mat R 2 5 := ![![14, 15, 6, 2, 19], ![11, 22, 22, 4, 19]]
def result : List (Test 3 2) := [([], 0), ([], 1), ([0], 0), ([1], 0), ([2], 0)]
theorem computed : fastPrimeDiscover 5 2 5
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case176
