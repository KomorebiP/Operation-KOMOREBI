module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case005
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (2^5)
def A : Fin 2 → Mat R 4 4 := ![![![30, 8, 13, 31], ![6, 21, 0, 1], ![22, 24, 31, 8], ![3, 28, 31, 9]], ![![27, 14, 23, 9], ![24, 18, 17, 27], ![18, 4, 15, 30], ![25, 6, 11, 12]]]
def O : Mat R 1 4 := ![![27, 7, 11, 7]]
def result : List (Test 2 1) := [([], 0), ([0], 0)]
theorem computed : fastPrimeDiscover 2 5 4
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case005
