module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case193
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (3^3)
def A : Fin 2 → Mat R 6 6 := ![![![1, 2, 20, 21, 24, 15], ![11, 4, 18, 5, 19, 5], ![15, 26, 25, 5, 7, 14], ![19, 12, 8, 3, 24, 21], ![20, 21, 16, 11, 13, 20], ![11, 16, 19, 9, 23, 5]], ![![2, 24, 11, 22, 16, 22], ![13, 15, 14, 21, 1, 1], ![21, 8, 17, 12, 23, 15], ![16, 22, 25, 25, 4, 6], ![4, 12, 11, 24, 5, 21], ![12, 13, 21, 5, 6, 16]]]
def O : Mat R 1 6 := ![![18, 4, 10, 3, 13, 23]]
def result : List (Test 2 1) := [([], 0), ([0], 0), ([1], 0), ([0,0], 0), ([1,0], 0), ([1,1], 0), ([0,0,0], 0)]
theorem computed : fastPrimeDiscover 3 3 6
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case193
