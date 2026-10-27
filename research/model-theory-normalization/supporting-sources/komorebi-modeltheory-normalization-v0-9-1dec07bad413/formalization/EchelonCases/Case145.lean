module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case145
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (3^2)
def A : Fin 2 → Mat R 3 3 := ![![![1, 1, 5], ![0, 2, 0], ![1, 0, 0]], ![![0, 7, 4], ![2, 7, 8], ![2, 8, 7]]]
def O : Mat R 1 3 := ![![7, 5, 8]]
def result : List (Test 2 1) := [([], 0), ([0], 0), ([1], 0), ([0,0], 0)]
theorem computed : fastPrimeDiscover 3 2 3
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case145
